"""Shared config-yaml loader — wraps `_lib.frontmatter.parse_config_yaml`.

Promoted from per-script duplication in P6 (validate_terminology), P8
(validate_reveal_conceit), and P10 (check_cascade) per BUILD_DISCIPLINE
3rd-consumer rule. Gates P12 (check_canon_consistency) and any future
config-yaml consumer to import from here rather than duplicate the
parse + wrapper-extract + per-entry WARN-skip + ConfigYamlError-raise
scaffolding. Mirrors T6 `_lib/dashboard.py` promotion precedent
(a7b730f). Pure stdlib.

Public API:
    load_config_yaml(
        config_path: Path,
        wrapper_key: str,
        required_keys: Sequence[str] = (),
        entity_noun: str = "entry",
    ) -> List[Dict[str, Any]]
        Read `config_path` and return the list of validated entries
        under `wrapper_key`. Missing file -> []. Per-entry
        not-a-mapping OR missing-required-keys -> WARN to stderr +
        skipped (valid entries still returned). Top-level wrapper_key
        value not a list -> raises ConfigYamlError. Underlying YAML
        parse failure (frontmatter.ConfigYamlError) propagates.
        `entity_noun` controls the WARN message wording so consumers
        preserve byte-identical stderr scrollback (P6/P8 pass 'rule';
        P10 passes 'pair').

    ConfigYamlError
        Re-exported from `_lib.frontmatter` via assignment — same class
        object (identity-equal). `config_loader.ConfigYamlError IS
        frontmatter.ConfigYamlError` is True. Consumers may import from
        either module; `except ConfigYamlError` catches both spellings.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

from _lib.frontmatter import ConfigYamlError, parse_config_yaml


def load_config_yaml(
    config_path: Path,
    wrapper_key: str,
    required_keys: Sequence[str] = (),
    entity_noun: str = "entry",
) -> List[Dict[str, Any]]:
    """Parse a config yaml; extract wrapper_key list; per-entry validate.

    Returns list of raw dicts (consumer-side extra validation +
    transformation happens post-call). Missing file -> []. Top-level
    `wrapper_key` value not a list -> raises ConfigYamlError. Per-entry
    not-a-mapping OR missing one of `required_keys` -> WARN to stderr
    via `warning: skipping malformed {entity_noun} {idx}: <reason>`;
    valid entries still returned.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        return []
    text = config_path.read_text(encoding="utf-8")
    parsed = parse_config_yaml(text)
    raw_list = parsed.get(wrapper_key, [])
    if not isinstance(raw_list, list):
        raise ConfigYamlError(
            "{}: top-level '{}' must be a list-of-mappings".format(
                config_path.name, wrapper_key
            )
        )

    valid: List[Dict[str, Any]] = []
    for idx, raw in enumerate(raw_list, start=1):
        if not isinstance(raw, dict):
            print(
                "warning: skipping malformed {} {}: not a mapping".format(
                    entity_noun, idx
                ),
                file=sys.stderr,
            )
            continue
        if required_keys:
            missing = [k for k in required_keys if k not in raw]
            if missing:
                print(
                    "warning: skipping malformed {} {}: missing keys {}".format(
                        entity_noun, idx, missing
                    ),
                    file=sys.stderr,
                )
                continue
        valid.append(raw)
    return valid
