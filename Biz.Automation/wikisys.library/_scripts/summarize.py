"""Plain-language audience summary — the canonical Librarian ``summarize()`` engine.

Implements the CODEX_LIBRARIAN.md v1.2 operation ``summarize(source, audience)``:
*render any canon/notes for a stated audience in plain language.* This is the
single canonical implementation of the capability; Codex consumers (e.g. the EMCC
dashboard) vendor this module via Sync and call it rather than re-implementing the
voice.

HONESTY — read before relying on this (the module's own canon requires it):

  The DETERMINISTIC, stdlib path is **extractive**. It SELECTS salient existing
  sentences and, for a non-technical audience, FILTERS OUT sentences dominated by
  jargon / file paths / hashes. It does **not** rewrite text into lay prose and it
  never mutates a sentence (no word deletion) — so every sentence it returns is a
  verbatim span of the source (the faithfulness guarantee). Extraction preserves
  the source's diction, jargon and all.

  True plain-language *rewriting* is a register transformation that only a language
  model performs. Inject a ``summarize_fn`` to get it. With no ``summarize_fn`` the
  output is faithful but jargon-preserving. **The "plain-language" contract of the
  capability is met by the seam, not by the default extractive path.**

Audiences (per the spec):
  - ``entrepreneur`` (default) — non-technical business owner. Extractive path
    drops jargon-dominated sentences and leads with the most salient remaining
    ones; a few sentences at most.
  - ``auditor`` — same extraction, a touch longer, no jargon filter.
  - ``developer`` — raw passthrough (the spec: "the developer view is simply the
    raw canon, no transform").

Public API:
    summarize(source, audience="entrepreneur", *, summarize_fn=None,
              max_sentences=None) -> str
        The facade. With a ``summarize_fn(source, audience) -> str`` it returns the
        true plain-language rewrite. Otherwise it returns the extractive fallback.
    extract_summary(source, audience="entrepreneur", max_sentences=None) -> str
        The deterministic extractive path on its own (no LLM).
    split_sentences(text) -> list[str]
        Abbreviation- / version- / decimal-aware sentence splitter.

Stdlib only. Deterministic (stable tie-breaks; no reliance on dict/hash ordering).
"""
# @component Codex[summarize]

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Audience → how many sentences the extractive path keeps (developer = passthrough).
_DEFAULT_MAX_SENTENCES = {
    "entrepreneur": 2,
    "auditor": 3,
}
_RAW_AUDIENCES = {"developer"}

# Abbreviations whose trailing period is NOT a sentence boundary.
_ABBREV = {
    "e.g", "i.e", "etc", "vs", "cf", "al", "inc", "ltd", "co", "mr", "mrs",
    "ms", "dr", "prof", "fig", "no", "eq", "sec", "approx", "est", "st",
}

# A sentence is "jargon-dominated" (dropped for the entrepreneur audience) when it
# carries any of: a file path (a/b), a dotted filename extension, a hex hash, a
# residual wikilink, or a §/code-ish token. Whole-sentence filter — never a
# word-level edit (word deletion would make the summary unfaithful to the source).
_JARGON_RE = re.compile(
    r"""
      (?:\S+/\S+)                      # a/b path
    | (?:\b\w+\.(?:py|md|ya?ml|json|txt|html|sh|ps1|toml|cfg)\b)  # filename.ext
    | (?:\b[0-9a-f]{7,40}\b)           # commit-ish hex hash
    | (?:\[\[)                         # residual wikilink
    | (?:§)                            # section sign
    | (?:\bR-\d{3,}\b)                 # R-XXXXX id
    """,
    re.VERBOSE | re.IGNORECASE,
)

_STOPWORDS = frozenset("""
a an the and or but if then else for of to in on at by with from as is are was
were be been being it its this that these those which who whom whose what when
where why how all any both each few more most other some such no nor not only own
same so than too very can will just should now into out up down over under again
""".split())

_SENT_END_RE = re.compile(r"[.!?]+(?=\s|$)")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]+")


def split_sentences(text):
    """Split prose into sentences, tolerant of abbreviations, versions, decimals.

    Boundaries are end punctuation followed by whitespace/EOL and then an
    uppercase / digit / opening quote. A trailing period after a known
    abbreviation is not a boundary. Version numbers (``v1.3``) and decimals
    (``3.14``) are never split — their dot is not followed by whitespace, so it
    is never a candidate boundary.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = []
    start = 0
    for match in _SENT_END_RE.finditer(text):
        end = match.end()
        rest = text[end:].lstrip()
        # Real boundary only if what follows looks like a new sentence (or EOL).
        if rest and not (rest[0].isupper() or rest[0].isdigit()
                         or rest[0] in "\"'(["):
            continue
        preceding = text[start:match.start()].split()
        last_word = preceding[-1].lower().rstrip(".") if preceding else ""
        if last_word in _ABBREV:
            continue
        sentence = text[start:end].strip()
        if sentence:
            sentences.append(sentence)
        start = end
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _strip_frontmatter(source):
    """Drop a leading ``---``-delimited YAML frontmatter block, if present."""
    if not source.startswith("---"):
        return source
    lines = source.splitlines(keepends=True)
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "".join(lines[i + 1:])
    return source


def _to_prose(source):
    """Reduce markdown to readable prose for sentence extraction.

    Removes frontmatter and fenced code, then flattens common inline markup
    (headings, list markers, wikilinks/links, emphasis, inline code) to their
    visible text. Headings end with a period so they read as sentences.
    """
    text = _strip_frontmatter(source)
    text = re.sub(r"(?ms)^(```|~~~).*?^\1\s*$", " ", text)   # fenced code
    out_lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            out_lines.append("")
            continue
        heading = re.match(r"^#{1,6}\s+(.*)$", line)
        if heading:
            head = heading.group(1).strip().rstrip(".")
            out_lines.append(head + "." if head else "")
            continue
        line = re.sub(r"^[-*+]\s+", "", line)               # bullet marker
        line = re.sub(r"^\d+[.)]\s+", "", line)             # ordered marker
        out_lines.append(line)
    text = "\n".join(out_lines)
    text = re.sub(r"!?\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]", r"\1", text)  # wikilink
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)    # [text](url)
    text = re.sub(r"`([^`]*)`", r"\1", text)                # inline code
    text = re.sub(r"(\*\*|\*|__|_|~~)", "", text)           # emphasis
    return text


def _score(sentence, freq):
    words = [w for w in (m.group(0).lower() for m in _WORD_RE.finditer(sentence))
             if w not in _STOPWORDS and len(w) > 2]
    if not words:
        return 0.0
    return sum(freq[w] for w in words) / len(words)


def extract_summary(source, audience="entrepreneur", max_sentences=None):
    """Deterministic extractive summary — selects (never rewrites) sentences.

    For ``developer`` returns the source verbatim. For other audiences: split into
    sentences, drop jargon-dominated ones (entrepreneur only), score by content-word
    frequency with a lead-position bias, take the top ``max_sentences`` and emit
    them in original document order. Every returned sentence is a verbatim span of
    the source's prose — the faithfulness guarantee.
    """
    if audience in _RAW_AUDIENCES:
        return source.strip()

    prose = _to_prose(source)
    sentences = split_sentences(prose)
    if not sentences:
        return ""

    if max_sentences is None:
        max_sentences = _DEFAULT_MAX_SENTENCES.get(audience, 2)
    max_sentences = max(1, max_sentences)

    indexed = list(enumerate(sentences))
    if audience == "entrepreneur":
        filtered = [(i, s) for (i, s) in indexed if not _JARGON_RE.search(s)]
        # Never return empty solely because everything looked technical — fall
        # back to the unfiltered lead so the summary stays faithful and non-empty.
        candidates = filtered or indexed
    else:
        candidates = indexed

    if len(candidates) <= max_sentences:
        return " ".join(s for _, s in candidates)

    n = len(candidates)
    freq = Counter()
    for _, s in candidates:
        for m in _WORD_RE.finditer(s):
            w = m.group(0).lower()
            if w not in _STOPWORDS and len(w) > 2:
                freq[w] += 1

    # Rank by score, then a lead-position bias, then original index (stable,
    # deterministic). rank_pos is the position WITHIN candidates so dropped
    # jargon sentences do not distort the lead bias.
    ranked = sorted(
        ((idx, sent, pos) for pos, (idx, sent) in enumerate(candidates)),
        key=lambda t: (-_score(t[1], freq) - (n - t[2]) / n, t[0]),
    )
    chosen = sorted(ranked[:max_sentences], key=lambda t: t[0])
    return " ".join(sent for _, sent, _ in chosen)


def summarize(source, audience="entrepreneur", *, summarize_fn=None,
              max_sentences=None):
    """Render ``source`` for ``audience`` in plain language.

    With a ``summarize_fn(source, audience) -> str`` injected, return its result —
    this is the ONLY path that yields true plain-language *rewriting*. Without one,
    return the deterministic extractive fallback (faithful, jargon-preserving). See
    the module docstring's HONESTY note.
    """
    if source is None:
        return ""
    source = str(source)
    if summarize_fn is not None:
        return summarize_fn(source, audience)
    return extract_summary(source, audience, max_sentences=max_sentences)


def _main(argv=None, stdout=None):
    stdout = stdout or sys.stdout
    parser = argparse.ArgumentParser(
        prog="summarize",
        description="Extractive plain-language summary (Librarian summarize op). "
                    "No LLM is wired here — output is extractive/faithful, not a "
                    "plain-language rewrite.",
    )
    parser.add_argument("path", help="markdown / text file to summarize")
    parser.add_argument("--audience", default="entrepreneur",
                        help="entrepreneur (default) | auditor | developer")
    parser.add_argument("--max-sentences", type=int, default=None)
    args = parser.parse_args(argv)

    source = Path(args.path).read_text(encoding="utf-8")
    print(summarize(source, args.audience, max_sentences=args.max_sentences),
          file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
