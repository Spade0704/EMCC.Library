"""Topic registry parser for cross-link generation (P18.1 foundation).

Parses `_canon/topics.yaml` per CODEX_BUILD_SPEC_v1_3.md §2.5 schema; emits
typed `Topic` records + alias-resolution lookup. Foundation module for the
3 consumer scripts: P18.2 build_topic_index + P18.3 cross_link_topics +
P18.4 validate_topic_registry. Pure stdlib.

Schema (CODEX_BUILD_SPEC_v1_3.md §2.5):
    topics:
      - name: example_topic                 # canonical name; lowercase snake_case
        aliases: [alt_name]                 # alternate names
        keywords:                           # word-boundary patterns scanned in H1/H2/intro
          - "example"
        cross_manual: true                  # cross top-level folder boundaries; default false
        min_similarity: 0.35                # per-topic TF-IDF override; defaults from cross_link.yaml

Required: name + keywords. Optional: aliases / cross_manual / min_similarity.

Public API:
    Topic                                       # @dataclass(frozen=True) immutable record
    parse_topics(yaml_text: str) -> List[Topic]
    load_topics(path: Path) -> List[Topic]
    build_alias_index(topics: List[Topic]) -> Dict[str, Topic]
    resolve_topic(name: str, alias_index: Dict[str, Topic]) -> Optional[Topic]

Halt-loud discipline: schema violations raise ValueError with offending
topic context (e.g. `topic 3: missing required key 'keywords'`). NO
try/except swallowing. NOT ConfigYamlError (semantic-distinct halt-loud
vs config_loader's WARN-skip permissive handling); pure ValueError per
spec foundation pattern.

DRY: reuses `_lib.frontmatter.parse_config_yaml` for raw YAML parsing
layer; custom topics-specific validation layer here per AC3 halt-loud
directive (config_loader's WARN-skip semantic does not fit).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from _lib.frontmatter import parse_config_yaml


SCHEMA_REQUIRED_KEYS = ("name", "keywords")
SCHEMA_OPTIONAL_KEYS = ("aliases", "cross_manual", "min_similarity")
SCHEMA_ALL_KEYS = SCHEMA_REQUIRED_KEYS + SCHEMA_OPTIONAL_KEYS


@dataclass(frozen=True)
class Topic:
    """Immutable topic record per CODEX_BUILD_SPEC_v1_3.md §2.5 schema."""

    name: str
    keywords: List[str]
    aliases: List[str] = field(default_factory=list)
    cross_manual: bool = False
    min_similarity: Optional[float] = None


def parse_topics(yaml_text: str) -> List[Topic]:
    """Parse topics.yaml text; return List[Topic]; raise ValueError on schema violation.

    Reuses `_lib.frontmatter.parse_config_yaml` for raw YAML parsing;
    layers topics-specific schema validation on top per AC3 halt-loud.
    """
    parsed = parse_config_yaml(yaml_text)
    raw_list = parsed.get("topics", [])
    if not isinstance(raw_list, list):
        raise ValueError(
            "top-level 'topics' must be a list, got {}".format(
                type(raw_list).__name__
            )
        )
    return [_validate_topic_entry(raw, idx) for idx, raw in enumerate(raw_list, start=1)]


def load_topics(path: Union[str, Path]) -> List[Topic]:
    """Read topics.yaml file and parse; delegates to parse_topics."""
    text = Path(path).read_text(encoding="utf-8")
    return parse_topics(text)


def build_alias_index(topics: List[Topic]) -> Dict[str, Topic]:
    """Build canonical-name + aliases → Topic lookup (case-folded keys).

    Original case preserved in Topic.name + Topic.aliases (lossless storage;
    case-folded only at lookup key). Raises ValueError on alias-canonical
    collision at lowercase-key level.
    """
    index: Dict[str, Topic] = {}
    for topic in topics:
        for key in [topic.name] + list(topic.aliases):
            normalized = key.lower()
            if normalized in index:
                raise ValueError(
                    "alias-canonical collision: {!r} maps to both {!r} and {!r}".format(
                        normalized, index[normalized].name, topic.name
                    )
                )
            index[normalized] = topic
    return index


def resolve_topic(
    name: str, alias_index: Dict[str, Topic]
) -> Optional[Topic]:
    """Case-insensitive single-call resolution; returns Topic or None."""
    return alias_index.get(name.lower())


_DEFAULT_CROSS_LINK_CONFIG: Dict[str, Any] = {
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


def load_cross_link_config(wiki_root: Union[str, Path]) -> Dict[str, Any]:
    """Load `_config/cross_link.yaml` and merge with hardcoded defaults.

    Behavior-compatible: shipped defaults == hardcoded. Missing config
    OR malformed config triggers graceful degradation to defaults
    (matches `load_plugin` precedent in build_topic_index.py per
    spec §2.7 'log warning + degrade, never block').

    Returns merged dict with same top-level shape as
    `_DEFAULT_CROSS_LINK_CONFIG` (tfidf / plugin / tags); per-section
    keys absent in user config fall back to defaults.
    """
    config_path = Path(wiki_root) / "_config" / "cross_link.yaml"
    merged = {section: dict(values) for section, values in _DEFAULT_CROSS_LINK_CONFIG.items()}
    if not config_path.is_file():
        return merged
    try:
        text = config_path.read_text(encoding="utf-8")
        parsed = parse_config_yaml(text)
    except Exception:
        return merged
    for section, section_defaults in _DEFAULT_CROSS_LINK_CONFIG.items():
        user_section = parsed.get(section)
        if isinstance(user_section, dict):
            for key in section_defaults:
                if key in user_section:
                    merged[section][key] = user_section[key]
    return merged


def _validate_topic_entry(raw: Any, idx: int) -> Topic:
    """Validate a single topic entry; raise ValueError on schema violation."""
    if not isinstance(raw, dict):
        raise ValueError(
            "topic {}: entry must be a mapping, got {}".format(idx, type(raw).__name__)
        )
    for key in SCHEMA_REQUIRED_KEYS:
        if key not in raw:
            raise ValueError(
                "topic {}: missing required key {!r}".format(idx, key)
            )
    unknown = [k for k in raw if k not in SCHEMA_ALL_KEYS]
    if unknown:
        raise ValueError(
            "topic {}: unknown keys {}".format(idx, sorted(unknown))
        )

    name = raw["name"]
    if not isinstance(name, str):
        raise ValueError(
            "topic {}: 'name' must be str, got {}".format(idx, type(name).__name__)
        )

    keywords = raw["keywords"]
    if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
        raise ValueError(
            "topic {} ({!r}): 'keywords' must be List[str]".format(idx, name)
        )

    aliases = raw.get("aliases", [])
    if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
        raise ValueError(
            "topic {} ({!r}): 'aliases' must be List[str]".format(idx, name)
        )

    cross_manual = raw.get("cross_manual", False)
    if not isinstance(cross_manual, bool):
        raise ValueError(
            "topic {} ({!r}): 'cross_manual' must be bool".format(idx, name)
        )

    min_similarity_raw = raw.get("min_similarity")
    if min_similarity_raw is not None:
        # bool is an int subclass; reject explicitly so `min_similarity: true`
        # does not silently coerce to 1.0.
        if isinstance(min_similarity_raw, bool):
            raise ValueError(
                "topic {} ({!r}): 'min_similarity' must be float or None".format(
                    idx, name
                )
            )
        # _lib.frontmatter._parse_value returns float literals as strings
        # ("0.35"); coerce string-form floats here. Non-numeric strings raise.
        if isinstance(min_similarity_raw, str):
            try:
                min_similarity_raw = float(min_similarity_raw)
            except ValueError:
                raise ValueError(
                    "topic {} ({!r}): 'min_similarity' must be float or None".format(
                        idx, name
                    )
                )
        if not isinstance(min_similarity_raw, (float, int)):
            raise ValueError(
                "topic {} ({!r}): 'min_similarity' must be float or None".format(
                    idx, name
                )
            )
    min_similarity = (
        float(min_similarity_raw) if min_similarity_raw is not None else None
    )

    return Topic(
        name=name,
        keywords=list(keywords),
        aliases=list(aliases),
        cross_manual=cross_manual,
        min_similarity=min_similarity,
    )
