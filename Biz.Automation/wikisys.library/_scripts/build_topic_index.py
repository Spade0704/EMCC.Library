"""P18.2 build_topic_index — TF-IDF topic-to-pages map + frontmatter additive update.

Per CODEX_BUILD_SPEC_v1_3.md §2.4 #16 + §2.5 matching rules + §2.7 plug-in
interface + §2.7 tag mirroring. Walks the wiki content pages, applies
spec §2.5 word-boundary case-insensitive keyword + alias matching to
build a topic → pages map, additively updates each page's frontmatter
`topics:` + mirrors topic-derived tags per cfg.tags, writes
`_dashboards/topic_index.md` via _lib.dashboard SSOT.

Scope per S046-T-XL-3 (Architect SCOPE REDUCTION arbitration APPROVED
2026-05-21): cross_link.yaml parsing DEFERRED to T-XL-3a followup —
_lib.frontmatter.parse_config_yaml lacks nested-mapping support per
docstring 'Out of scope: nested mappings'. This cycle ships with
HARDCODED DEFAULTS matching spec §2.5 _config/cross_link.yaml schema.
Plug-in path is dead at runtime (plugin.module_path=None default) but
load_plugin signature + failure-isolation contract maintained for
T-XL-3a future enablement.

Public API:
    run(wiki_root: Path) -> Dict[str, Any]
        Orchestrator entry-point. Returns:
            {
                "topic_to_pages": Dict[str, List[Path]],
                "pages_scanned": int,
                "dashboard_path": Path,
            }

    extract_scan_text(page_path: Path, scan_fields: List[str]) -> str
    tfidf_score(query_text: str, doc_text: str) -> float
    match_topics_to_page(page_scan_text, topics, alias_index) -> List[str]
    load_plugin(config: Dict[str, Any]) -> Optional[Callable]
    blend_results(tfidf_scores, plugin_scores, weight) -> Dict[str, float]
    update_page_frontmatter(page_path: Path, matched_topics: List[str], cfg: Dict[str, Any]) -> None
    render_topic_index(topic_to_pages: Dict[str, List[Path]], wiki_root: Path) -> str

Pure stdlib per AC1 + spec §8 Hard Rule 1.
"""

import importlib
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from _lib import dashboard
from _lib import frontmatter
from _lib import markdown
from _lib.topics import (
    Topic,
    build_alias_index,
    load_cross_link_config,
    load_topics,
    resolve_topic,
)


WIKI_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_RELATIVE = "_dashboards/topic_index.md"
TOPICS_RELATIVE = "_canon/topics.yaml"

# Hardcoded defaults per Architect SCOPE REDUCTION T-XL-3. Matches spec
# §2.5 _config/cross_link.yaml schema. T-XL-3a followup adds runtime
# load_cross_link_config replacement once parse_config_yaml nested-mapping
# support shipped.
DEFAULT_CONFIG: Dict[str, Any] = {
    "tfidf": {
        "min_similarity": 0.35,
        "max_links_per_page": 8,
        "scan_fields": ["h1", "h2", "intro_para_1"],
    },
    "plugin": {
        "module_path": None,
        "callable": None,
        "weight": 0.5,
    },
    "tags": {
        "mirror_from": ["topics"],
        "prefix_scheme": "flat",
        "prefix_map": {"topics": "topic"},
    },
}

_WORD_TOKEN_RE = re.compile(r"\b\w+\b")
_H1_RE = re.compile(r"^# (.+)$", re.MULTILINE)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def extract_scan_text(page_path: Path, scan_fields: List[str]) -> str:
    """Extract page scan text per spec §2.5 scan_fields (h1 / h2 / intro_para_1).

    Frontmatter + fenced/inline code stripped via _lib.markdown.strip_code
    before extraction per spec §2.5 matching rules. Returns space-joined
    text from all configured scan fields.
    """
    raw = page_path.read_text(encoding="utf-8")
    lines = raw.split("\n")
    close = frontmatter.find_frontmatter_close(lines)
    body = "\n".join(lines[close + 1:]) if close is not None else raw
    body = markdown.strip_code(body)

    parts: List[str] = []
    if "h1" in scan_fields:
        for m in _H1_RE.finditer(body):
            parts.append(m.group(1).strip())
    if "h2" in scan_fields:
        for m in _H2_RE.finditer(body):
            parts.append(m.group(1).strip())
    if "intro_para_1" in scan_fields:
        intro: List[str] = []
        in_intro = False
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                if in_intro:
                    break
                continue
            if stripped == "":
                if in_intro:
                    break
                continue
            in_intro = True
            intro.append(stripped)
        if intro:
            parts.append(" ".join(intro))
    return " ".join(parts)


def _tokenize(text: str) -> List[str]:
    """Lowercase word-token list via `\\b\\w+\\b` regex."""
    return _WORD_TOKEN_RE.findall(text.lower())


def tfidf_score(query_text: str, doc_text: str) -> float:
    """Cosine similarity between query and doc TF vectors. Returns 0.0 to 1.0.

    Pure stdlib (math + collections.Counter + re). Identical token sets
    → 1.0; orthogonal → 0.0; partial overlap → in-between. Empty query
    or doc → 0.0. 2-doc corpus IDF is degenerate (log(2/2)=0 for shared
    terms), so this implementation uses TF cosine (no IDF weighting)
    per primitive-helper simplicity. Corpus-wide IDF deferrable to
    future cycle if cross-page ranking with IDF weighting becomes needed.
    """
    query_tokens = _tokenize(query_text)
    doc_tokens = _tokenize(doc_text)
    if not query_tokens or not doc_tokens:
        return 0.0
    query_tf = Counter(query_tokens)
    doc_tf = Counter(doc_tokens)
    shared = set(query_tf) & set(doc_tf)
    dot = sum(query_tf[t] * doc_tf[t] for t in shared)
    norm_q = math.sqrt(sum(v * v for v in query_tf.values()))
    norm_d = math.sqrt(sum(v * v for v in doc_tf.values()))
    if norm_q == 0 or norm_d == 0:
        return 0.0
    return dot / (norm_q * norm_d)


def match_topics_to_page(
    page_scan_text: str,
    topics: List[Topic],
    alias_index: Dict[str, Topic],
) -> List[str]:
    """Word-boundary case-insensitive keyword + alias match per spec §2.5.

    Each topic matches if any of its keywords / aliases / canonical name
    appears in page_scan_text (word-boundary, case-insensitive).
    Returns sorted unique canonical names matched. alias_index reserved
    for future alias-lookup-driven match strategies; current impl uses
    per-topic regex iteration.
    """
    matched: set = set()
    for topic in topics:
        terms = [topic.name] + list(topic.aliases) + list(topic.keywords)
        for term in terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, page_scan_text, re.IGNORECASE):
                matched.add(topic.name)
                break
    return sorted(matched)


def load_plugin(config: Dict[str, Any]) -> Optional[Callable]:
    """Import + resolve plug-in callable per spec §2.7 plug-in interface.

    Returns the callable on success, None on missing-config OR
    ImportError OR AttributeError OR other Exception. Logs warning to
    stderr per spec §2.7 'log a warning and degrade to TF-IDF-only.
    Never block the pipeline.'
    """
    plugin_cfg = config.get("plugin", {})
    module_path = plugin_cfg.get("module_path")
    callable_name = plugin_cfg.get("callable")
    if not module_path or not callable_name:
        return None
    try:
        module = importlib.import_module(module_path)
        return getattr(module, callable_name)
    except (ImportError, AttributeError) as exc:
        print(
            "WARN: cross-link plug-in unavailable ({}); degrading to "
            "TF-IDF-only.".format(exc),
            file=sys.stderr,
        )
        return None
    except Exception as exc:
        print(
            "WARN: cross-link plug-in raised on import ({}); degrading "
            "to TF-IDF-only.".format(exc),
            file=sys.stderr,
        )
        return None


def blend_results(
    tfidf_scores: Dict[str, float],
    plugin_scores: Optional[Dict[str, float]],
    weight: float,
) -> Dict[str, float]:
    """Linear interpolation: final = (1 - weight) * tfidf + weight * plugin.

    Per spec §2.7 plug-in interface. weight=0.0 → tfidf-only;
    weight=1.0 → plugin-only; 0.5 → 50/50. plugin_scores=None →
    pass-through tfidf_scores. Keys union of both inputs (missing keys
    in one side treated as 0.0).
    """
    if plugin_scores is None:
        return dict(tfidf_scores)
    keys = set(tfidf_scores) | set(plugin_scores)
    return {
        k: (1.0 - weight) * tfidf_scores.get(k, 0.0)
        + weight * plugin_scores.get(k, 0.0)
        for k in keys
    }


def _format_fm_list(values: List[str]) -> str:
    """Format List[str] for frontmatter as flow-list per YAML-subset shape."""
    if not values:
        return "[]"
    return "[" + ", ".join(values) + "]"


def update_page_frontmatter(
    page_path: Path,
    matched_topics: List[str],
    cfg: Dict[str, Any],
) -> None:
    """Additively extend page frontmatter `topics:` + mirror tags per cfg.

    Existing topics + tags PRESERVED zero-deviation per spec §3
    Principle #13. Matched values appended; sorted+unique. Tag
    mirroring per cfg.tags.mirror_from + prefix_scheme. NEVER removes
    existing tags or topics.
    """
    raw = page_path.read_text(encoding="utf-8")
    lines = raw.split("\n")
    close = frontmatter.find_frontmatter_close(lines)
    if close is None:
        # No frontmatter — skip per AC2 additive discipline (don't
        # synthesize fm on pages without it).
        return

    fm = frontmatter.parse_frontmatter(raw) or {}
    existing_topics = fm.get("topics") or []
    if not isinstance(existing_topics, list):
        existing_topics = []
    new_topics = sorted(set(existing_topics + matched_topics))

    existing_tags = fm.get("tags") or []
    if not isinstance(existing_tags, list):
        existing_tags = []
    mirrored_tags = _compute_mirrored_tags(new_topics, cfg)
    new_tags = sorted(set(existing_tags + mirrored_tags))

    fm_block_lines = lines[1:close]
    updated_fm_lines = _rewrite_fm_block(fm_block_lines, new_topics, new_tags)

    out_lines = ["---"] + updated_fm_lines + ["---"] + lines[close + 1:]
    page_path.write_text("\n".join(out_lines), encoding="utf-8")


def _compute_mirrored_tags(
    topics: List[str], cfg: Dict[str, Any]
) -> List[str]:
    """Compute topic-derived tags per cfg.tags.mirror_from + prefix_scheme."""
    tags_cfg = cfg.get("tags", {})
    mirror_from = tags_cfg.get("mirror_from", [])
    if not mirror_from or "topics" not in mirror_from:
        return []
    prefix_scheme = tags_cfg.get("prefix_scheme", "flat")
    prefix_map = tags_cfg.get("prefix_map", {})
    if prefix_scheme == "nested":
        prefix = prefix_map.get("topics", "topic")
        return ["{}/{}".format(prefix, t) for t in topics]
    return list(topics)


def _rewrite_fm_block(
    fm_lines: List[str], new_topics: List[str], new_tags: List[str]
) -> List[str]:
    """Update or insert `topics:` + `tags:` lines in existing fm block.

    Preserves all other fm lines verbatim. If a key already exists,
    replaces its line; if absent, appends at end of block.
    """
    out: List[str] = []
    saw_topics = False
    saw_tags = False
    for line in fm_lines:
        stripped = line.lstrip()
        if stripped.startswith("topics:"):
            out.append("topics: " + _format_fm_list(new_topics))
            saw_topics = True
        elif stripped.startswith("tags:"):
            out.append("tags: " + _format_fm_list(new_tags))
            saw_tags = True
        else:
            out.append(line)
    if not saw_topics:
        out.append("topics: " + _format_fm_list(new_topics))
    if not saw_tags and new_tags:
        out.append("tags: " + _format_fm_list(new_tags))
    return out


def render_topic_index(
    topic_to_pages: Dict[str, List[Path]], wiki_root: Path
) -> str:
    """Render `_dashboards/topic_index.md` markdown content."""
    today = date.today().isoformat()
    lines: List[str] = list(
        dashboard.render_fm_header("Topic Index Dashboard", today=today)
    )
    lines.append("")
    lines.append("# Topic Index — " + today)
    lines.append("")
    lines.append("**Topics indexed:** " + str(len(topic_to_pages)))
    total_pages = sum(len(p) for p in topic_to_pages.values())
    lines.append("**Total topic-page links:** " + str(total_pages))
    lines.append("")
    if not topic_to_pages:
        lines.append("No topics matched any pages.")
        lines.append("")
        return "\n".join(lines)
    for topic_name in sorted(topic_to_pages):
        pages = topic_to_pages[topic_name]
        lines.append("## " + topic_name)
        for page in sorted(pages, key=lambda p: p.as_posix()):
            try:
                rel = page.relative_to(wiki_root).as_posix()
            except ValueError:
                rel = page.as_posix()
            stem = page.stem
            lines.append("- [[" + stem + "]] (" + rel + ")")
        lines.append("")
    return "\n".join(lines)


def run(wiki_root: Path) -> Dict[str, Any]:
    """Orchestrator entry-point — build topic index + update fm + emit dashboard."""
    wiki_root = Path(wiki_root)
    # S047-T-XL-3a: load runtime config from `_config/cross_link.yaml`
    # with graceful fallback to hardcoded defaults on missing/malformed.
    cfg = load_cross_link_config(wiki_root)

    topics_path = wiki_root / TOPICS_RELATIVE
    if not topics_path.is_file():
        # Graceful early-exit: empty dashboard, no fm updates.
        content = render_topic_index({}, wiki_root)
        out_path = dashboard.write_dashboard(
            wiki_root, DASHBOARD_RELATIVE, content
        )
        return {
            "topic_to_pages": {},
            "pages_scanned": 0,
            "dashboard_path": out_path,
        }

    topics_list = load_topics(topics_path)
    alias_index = build_alias_index(topics_list)
    plugin_callable = load_plugin(cfg)
    _ = plugin_callable  # plug-in is dead code this cycle (defaults); kept for API stability

    topic_to_pages: Dict[str, List[Path]] = {}
    pages_scanned = 0
    scan_fields = cfg["tfidf"]["scan_fields"]
    for page_path in markdown.iter_content_pages(wiki_root):
        pages_scanned += 1
        scan_text = extract_scan_text(page_path, scan_fields)
        matched = match_topics_to_page(scan_text, topics_list, alias_index)
        if matched:
            update_page_frontmatter(page_path, matched, cfg)
            for topic_name in matched:
                topic_to_pages.setdefault(topic_name, []).append(page_path)

    content = render_topic_index(topic_to_pages, wiki_root)
    out_path = dashboard.write_dashboard(
        wiki_root, DASHBOARD_RELATIVE, content
    )
    return {
        "topic_to_pages": topic_to_pages,
        "pages_scanned": pages_scanned,
        "dashboard_path": out_path,
    }


if __name__ == "__main__":
    summary = run(WIKI_ROOT)
    rel = summary["dashboard_path"].relative_to(WIKI_ROOT).as_posix()
    print(
        "topic_index: topics={} pages_scanned={} -> {}".format(
            len(summary["topic_to_pages"]),
            summary["pages_scanned"],
            rel,
        )
    )
