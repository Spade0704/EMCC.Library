"""backfill_topics — bulk topic tagger for retrofitting pre-existing wikis.

Codex normally assigns `topics:` at ingest (build_topic_index, TF-IDF vs
`_canon/topics.yaml`). A wiki of thousands of already-built pages with no
registry can't use that path. This script backfills `topics:` from two
project-configured sources so `cross_link_topics.py` (#17) can then build the
See-also graph:

  1. PATH-DERIVED — each folder segment of a page is normalized to a canonical
     topic via `_config/topic_backfill.yaml`:
       - `strip_numeric_prefix: true` auto-derives `NN_Name` folders
         (e.g. `27_Flight_Controls` -> `flight-controls`).
       - `systems:`/`crosscutting:` map variant abbreviation folders
         (F_CTL, FCTL, ...) to the SAME canonical slug so cross-section pages
         unify.
       - `skip:` tokens (section codes / structural folders) never tag.
       - unknown tokens are reported UNMAPPED (not tagged).
  2. KEYWORD — when `use_keywords_yaml: true`, each `_config/keywords.yaml`
     term matched against a page's title + H1/H2 + filename becomes a topic.
  3. SECTION-CODE (dotted/dashed) — when `derive_section_codes: true`, bare
     numeric section codes embedded in path tokens OR the filename
     (e.g. `27-10`, `27.10.00`, `27-10-00`) derive a topic. A code (normalized
     to dash form, e.g. `27.10` -> `27-10`) listed in `section_code_topics:`
     maps to its canonical topic; an unlisted code falls back to a stable
     `<section_code_prefix><code>` slug (default prefix `ata-`, e.g.
     `ata-27-10`) so dotted codes still unify cross-section pages without a
     per-code map entry. This lets consumers (e.g. Aviation) retire local
     `stamp_topics`/`cross_link` forks and Sync the kit instead.

Additive + idempotent: existing `topics:` are never removed; a page already
carrying all derived topics is untouched. Pages with NO frontmatter get a
LINK-ONLY STUB (`status: stub-unstamped`) when `stub_unstamped: true`, body
byte-for-byte verbatim — they participate in cross-linking without a false
consequence/effectivity claim.

The per-project normalization map lives in the consumer's `_config/`; this
script is generic. Pure stdlib + `_lib`.

Modes:
    python backfill_topics.py <wiki_root>            # DRY-RUN (counts + unmapped)
    python backfill_topics.py <wiki_root> --apply
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from _lib import cli
from _lib import frontmatter
from _lib import markdown

ATA_RE = re.compile(r"^\d+_(.+)$")
NOISE_RE = re.compile(r"^(\d+|[A-Za-z])$")
# Dotted/dashed numeric section code (2-4 numeric groups of 1-3 digits each),
# e.g. 27-10, 27.10.00, 27-10-00. The code must START a token or follow a
# non-alphanumeric separator (`27-10_Aileron`, `Sec_27.30`); the lookbehind
# rejects a preceding digit/letter/`.`/`-` so a longer run is not re-anchored
# mid-number (a date `2026-06-13` does NOT yield `06-13`; a version `v1.2.3`
# does NOT match) and a plain single NN (caught by strip_numeric_prefix) is not
# matched. Letter-glued codes (`Ch27.10`) are intentionally NOT matched —
# rejecting them is what keeps version/word fragments out; ATA wikis token-split
# their codes, so this loses nothing real.
SECTION_CODE_RE = re.compile(r"(?<![0-9A-Za-z.\-])(\d{1,3}(?:[.\-]\d{1,3}){1,3})(?![0-9])")
H1H2_RE = re.compile(r"^(#{1,2})\s+(.*\S)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r'^title:\s*"?(.*?)"?\s*$', re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.*\S)\s*$", re.MULTILINE)

WIKI_ROOT = frontmatter.find_wiki_content_root()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _config_path(wiki_root: Path, name: str) -> Path:
    try:
        return frontmatter.find_config_dir(wiki_root) / name
    except FileNotFoundError:
        return wiki_root / "_config" / name


def load_backfill_config(wiki_root: Path) -> dict:
    path = _config_path(wiki_root, "topic_backfill.yaml")
    if not path.is_file():
        return {}
    try:
        return frontmatter.parse_config_yaml(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_revmap(cfg: dict) -> dict:
    """token.upper() -> canonical slug, from systems: + crosscutting: sections."""
    rev = {}
    for section in ("systems", "crosscutting"):
        sec = cfg.get(section)
        if isinstance(sec, dict):
            for canon, toks in sec.items():
                if isinstance(toks, list):
                    for t in toks:
                        rev[str(t).upper()] = canon
    return rev


def load_keyword_terms(wiki_root: Path):
    path = _config_path(wiki_root, "keywords.yaml")
    terms = []
    if not path.is_file():
        return terms
    category = None
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")) and line.rstrip().endswith(":"):
            category = line.strip()[:-1]
        elif line.lstrip().startswith("- ") and category:
            term = line.lstrip()[2:].strip().strip("'\"")
            terms.append((term.lower(), slug(term)))
    return terms


def path_topics(rel_parts, revmap, skipset, strip_numeric, unmapped):
    out = set()
    for tok in rel_parts[:-1]:
        if tok in skipset:
            continue
        if strip_numeric:
            m = ATA_RE.match(tok)
            if m:
                s = slug(m.group(1))
                if s and s != "chapter":
                    out.add(s)
                continue
        if NOISE_RE.match(tok):
            continue
        up = tok.upper()
        if up in revmap:
            out.add(revmap[up])
        else:
            unmapped[tok] += 1
    return out


def keyword_topics(name, text, terms):
    bits = [name.replace("_", " ")]
    tm = TITLE_RE.search(text[:2000])
    if tm:
        bits.append(tm.group(1))
    for _, head in H1H2_RE.findall(text):
        bits.append(head)
    hay = " \n ".join(bits).lower()
    return {ts for term, ts in terms if term in hay}


def normalize_section_code(code: str) -> str:
    """Canonicalize a dotted/dashed section code to dash form: 27.10 -> 27-10."""
    return code.replace(".", "-")


def build_section_code_map(cfg: dict) -> dict:
    """normalized-code -> canonical topic slug, from `section_code_topics:`.

    Keys are normalized (dash form) so `27.10` and `27-10` in either the config
    or the page collide to the same canonical topic. Values are passed through
    `slug` so a human-written canonical topic (e.g. `Aileron Control`) lands as
    a valid slug.
    """
    out = {}
    sec = cfg.get("section_code_topics")
    if isinstance(sec, dict):
        for code, topic in sec.items():
            out[normalize_section_code(str(code))] = slug(str(topic))
    return out


def section_code_topics(rel_parts, name, code_map, prefix):
    """Derive topics from dotted/dashed section codes in path tokens + filename.

    A code found in `code_map` maps to its canonical topic; an unmapped code
    falls back to `<prefix><normalized-code>` (default prefix `ata-`). Scans
    every path token AND the filename stem so codes carried in either place
    unify. Returns a set of topic slugs (possibly empty).
    """
    out = set()
    tokens = list(rel_parts[:-1]) + [Path(name).stem]
    for tok in tokens:
        for m in SECTION_CODE_RE.finditer(tok):
            norm = normalize_section_code(m.group(1))
            out.add(code_map.get(norm, prefix + norm))
    return out


# ---- frontmatter helpers ----

def _fm_close(lines):
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    return None


def _read_topics(fm_lines):
    """Return (existing_topics | None, line_indices_owned_by_topics).

    Handles BOTH frontmatter forms (per Auditor 2026-06-13 block-list finding):
      inline:  `topics: [a, b]`
      block:   `topics:` then following `  - a` / `  - b` lines
    Returns None when there is no `topics:` field. The index list lets the
    rewriter remove the whole existing field (incl. block items) before
    writing the merged inline form — so block-form pages don't lose topics or
    leave orphan `- ` lines.
    """
    for i, line in enumerate(fm_lines):
        if not line.lstrip().startswith("topics:"):
            continue
        inner = line.split(":", 1)[1].strip()
        if inner.startswith("["):
            inner = inner.strip("[]").strip()
            items = [t.strip().strip("'\"") for t in inner.split(",") if t.strip()] if inner else []
            return items, [i]
        if inner == "":
            items, idxs = [], [i]
            j = i + 1
            while j < len(fm_lines):
                s = fm_lines[j].strip()
                if fm_lines[j][:1] in (" ", "\t") and s.startswith("- "):
                    items.append(s[2:].strip().strip("'\""))
                    idxs.append(j)
                    j += 1
                else:
                    break
            return items, idxs
        return [inner.strip("'\"")], [i]   # scalar single value
    return None, []


def merge_topics_fm(text, topics):
    lines = text.split("\n")
    close = _fm_close(lines)
    if close is None:
        return text, False
    fm_lines = lines[1:close]
    current, owned = _read_topics(fm_lines)
    if current is not None:
        merged = sorted(set(current) | set(topics))
        if merged == sorted(set(current)):
            return text, False
        new_line = "topics: [" + ", ".join(merged) + "]"
        out_fm = []
        for idx, l in enumerate(fm_lines):
            if idx == owned[0]:
                out_fm.append(new_line)   # replace field at its first line
            elif idx in owned:
                continue                  # drop old block-list items
            else:
                out_fm.append(l)
        new_fm = out_fm
    else:
        new_fm = list(fm_lines) + ["topics: [" + ", ".join(sorted(set(topics))) + "]"]
    return "\n".join(["---"] + new_fm + ["---"] + lines[close + 1:]), True


def stub_stamp(text, topics):
    m = H1_RE.search(text)
    title = (m.group(1).strip().replace('"', "'") if m else "Untitled")
    block = "\n".join([
        "---",
        'title: "{}"'.format(title),
        "type: reference",
        "status: stub-unstamped",
        "topics: [" + ", ".join(sorted(set(topics))) + "]",
        "---", "", "",
    ])
    return block + text


def run(wiki_root: Path, apply: bool) -> dict:
    wiki_root = Path(wiki_root)
    cfg = load_backfill_config(wiki_root)
    if not cfg:
        # No project config → no-op (never tag from defaults alone).
        return {"matched": 0, "merged": 0, "stubbed": 0,
                "topic_pages": {}, "unmapped": {}, "configured": False}
    revmap = build_revmap(cfg)
    skipset = set(cfg.get("skip") or [])
    strip_numeric = bool(cfg.get("strip_numeric_prefix", True))
    stub = bool(cfg.get("stub_unstamped", False))
    terms = load_keyword_terms(wiki_root) if cfg.get("use_keywords_yaml", False) else []
    # Section-code derivation is opt-in (default off → byte-identical to prior
    # behavior for DFDU/Mentor and any consumer that doesn't enable it).
    derive_codes = bool(cfg.get("derive_section_codes", False))
    code_map = build_section_code_map(cfg) if derive_codes else {}
    code_prefix = str(cfg.get("section_code_prefix", "ata-")) if derive_codes else "ata-"

    topic_pages = Counter()
    unmapped = Counter()
    matched = merged = stubbed = 0

    for md in markdown.iter_content_pages(wiki_root):
        rel_parts = md.relative_to(wiki_root).parts
        text = md.read_text(encoding="utf-8")
        topics = path_topics(rel_parts, revmap, skipset, strip_numeric, unmapped)
        if terms:
            topics |= keyword_topics(md.name, text, terms)
        if derive_codes:
            topics |= section_code_topics(rel_parts, md.name, code_map, code_prefix)
        if not topics:
            continue
        matched += 1
        for t in topics:
            topic_pages[t] += 1
        if not apply:
            continue
        # Decide merge-vs-stub by ACTUAL frontmatter presence (a closed `---`
        # block), matching merge_topics_fm/_fm_close — not a loose `lstrip`
        # check that disagreed on leading-blank/malformed pages (Auditor 2026-06-13).
        if _fm_close(text.split("\n")) is not None:
            new_text, changed = merge_topics_fm(text, sorted(topics))
            if changed:
                md.write_text(new_text, encoding="utf-8")
                merged += 1
        elif stub:
            md.write_text(stub_stamp(text, sorted(topics)), encoding="utf-8")
            stubbed += 1

    return {
        "matched": matched,
        "merged": merged,
        "stubbed": stubbed,
        "topic_pages": dict(topic_pages),
        "unmapped": dict(unmapped),
        "configured": bool(cfg),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wiki_root", nargs="?", default=None)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = Path(a.wiki_root).resolve() if a.wiki_root else cli.resolve_cli_wiki_root(WIKI_ROOT)
    s = run(root, a.apply)
    if not s["configured"]:
        print("backfill_topics: no _config/topic_backfill.yaml found — nothing to do.")
        sys.exit(0)
    mode = "APPLY" if a.apply else "DRY-RUN"
    print("backfill_topics [{}]: matched={} merged={} stubbed={} topics={}".format(
        mode, s["matched"], s["merged"], s["stubbed"], len(s["topic_pages"])))
    for topic, n in sorted(s["topic_pages"].items(), key=lambda kv: (-kv[1], kv[0])):
        print("  {:5d}  {}".format(n, topic))
    if s["unmapped"]:
        print("UNMAPPED path tokens (add to topic_backfill.yaml or skip):")
        for tok, n in sorted(s["unmapped"].items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
            print("  {:5d}  {}".format(n, tok))
