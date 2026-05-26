"""Raw requirement gate classification.

This module decides whether a raw extracted item should enter the formal
requirement pool or stay as constraint/capability/evidence metadata.

Gate rules are loaded from ``references/raw_classification_rules.yaml`` so
they can be audited and adjusted without touching classification logic.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Literal

RawDisposition = Literal[
    "formal_requirement",
    "constraint",
    "capability",
    "metadata",
    "evidence",
    "architecture_seed_only",
    "test_seed_only",
    "open_issue",
]

# Cached rule set — loaded once on first classification call.
_RULES: list[dict[str, Any]] | None = None
_CAPABILITY_TOKENS: list[str] = []
_CAPABILITY_REGEXES: list[str] = []


def _rules_path() -> Path:
    """Resolve the rules YAML relative to this source file."""
    this_file = Path(__file__).resolve()
    # Walk up from src/fc_requirement_workbench/ to the skill root
    skill_root = this_file.parents[2]
    return skill_root / "references" / "raw_classification_rules.yaml"


def _load_rules() -> None:
    """Parse the gate rules YAML file into the module-level caches."""
    global _RULES, _CAPABILITY_TOKENS, _CAPABILITY_REGEXES

    path = _rules_path()
    if not path.exists():
        _RULES = []
        return

    doc = _parse_simple_yaml(path.read_text(encoding="utf-8"))

    _RULES = doc.get("rules", [])

    cap = doc.get("capability_patterns", {})
    _CAPABILITY_TOKENS = cap.get("tokens", [])
    _CAPABILITY_REGEXES = cap.get("regexes", [])


def classify_raw_item(
    *,
    category: str,
    title: str,
    description: str,
    source_section: str = "",
) -> tuple[RawDisposition, str]:
    global _RULES
    if _RULES is None:
        _load_rules()

    text = f"{title} {description}".strip()
    lowered = text.lower()
    source_section_lowered = source_section.lower()

    for rule in (_RULES or []):
        if _rule_matches(
            rule,
            category=category,
            text=text,
            lowered=lowered,
            source_section=source_section,
            source_section_lowered=source_section_lowered,
        ):
            return (rule["disposition"], rule["reason"])

    return ("formal_requirement", "The raw item is currently eligible to enter the formal requirement pool.")


def _rule_matches(
    rule: dict[str, Any],
    *,
    category: str,
    text: str,
    lowered: str,
    source_section: str,
    source_section_lowered: str,
) -> bool:
    match = rule.get("match", {})

    if "category_is" in match:
        if category not in match["category_is"]:
            return False

    if "tokens_in_text" in match:
        if not any(token in lowered for token in match["tokens_in_text"]):
            return False

    if "regex" in match:
        if not re.search(match["regex"], text):
            return False

    if "source_section_tokens" in match:
        if not any(token in source_section_lowered for token in match["source_section_tokens"]):
            return False

    if "source_section_regex" in match:
        if not re.search(match["source_section_regex"], source_section):
            return False

    if match.get("capability_pattern"):
        if not _looks_like_chip_capability(text, lowered):
            return False

    # Rule matched only if at least one match condition was present and satisfied.
    # A rule with an empty match block never fires.
    if not match:
        return False
    return True


def _looks_like_chip_capability(text: str, lowered: str) -> bool:
    for token in _CAPABILITY_TOKENS:
        if token in text:
            return True
    for pattern in _CAPABILITY_REGEXES:
        if re.search(pattern, text):
            return True
    if re.search(r"支持.+能力", text):
        return True
    if re.search(r"支持通过(?:i2c|spi).+访问", lowered):
        return True
    if "chip" in lowered and "support" in lowered:
        return True
    return False


# ---------------------------------------------------------------------------
# Minimal YAML parser — built specifically for raw_classification_rules.yaml.
# No PyYAML dependency.
# ---------------------------------------------------------------------------

def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse raw_classification_rules.yaml into ``{rules: [...], capability_patterns: {...}}``.

    Uses a simple line-by-line state machine tuned to the exact structure of the
    rules file.  No PyYAML dependency.
    """
    return {
        "rules": _parse_rules(text),
        "capability_patterns": _parse_capability_patterns(text),
    }


def _parse_rules(text: str) -> list[dict[str, Any]]:
    """Parse the ``rules:`` section line-by-line."""
    rules: list[dict[str, Any]] = []
    lines = text.splitlines()
    idx = 0

    # Advance to ``rules:``
    while idx < len(lines):
        if lines[idx].strip() == "rules:":
            idx += 1
            break
        idx += 1

    current_rule: dict[str, Any] | None = None
    current_match: dict[str, Any] | None = None
    collecting_list: str | None = None  # name of the list field being collected

    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        line_indent = len(line) - len(line.lstrip())
        # Skip blank lines / comments / section headers outside rules
        if not stripped or stripped.startswith("#"):
            idx += 1
            continue
        if line_indent == 0 and ":" in stripped and current_rule is None:
            # Hit a non-rule section (e.g. capability_patterns:)
            break

        # New rule item: ``  - disposition: value``
        if stripped.startswith("- disposition:"):
            if current_rule is not None:
                rules.append(_finalise_rule(current_rule, current_match))
            current_rule = {"disposition": _yv(stripped), "reason": "", "match": {}}
            current_match = {}
            collecting_list = None
            idx += 1
            continue

        if current_rule is None:
            idx += 1
            continue

        # Fields at rule level
        if stripped.startswith("reason:"):
            current_rule["reason"] = _yv(stripped)
            idx += 1
            continue

        if stripped == "match:":
            current_match = {}
            collecting_list = None
            idx += 1
            continue

        # Fields inside match: — may be inline arrays or multi-line lists
        if current_match is not None:
            consumed, collecting_list = _try_parse_match_field(stripped, current_match)
            if consumed:
                idx += 1
                continue

        # Multi-line list continuation
        if stripped.startswith("- ") and collecting_list and current_match is not None:
            value = stripped[2:].strip().strip('"').strip("'")
            current_match[collecting_list].append(value)
            idx += 1
            continue

        idx += 1

    if current_rule is not None:
        rules.append(_finalise_rule(current_rule, current_match))

    return rules


def _try_parse_match_field(stripped: str, match: dict[str, Any]) -> tuple[bool, str | None]:
    """Try to parse a match-block field.

    Returns ``(consumed, collecting_list_name)`` so callers can continue
    consuming multi-line YAML lists when the field had no inline values.
    """
    if stripped == "category_is:" or stripped.startswith("category_is:"):
        raw = _yv(stripped)
        if raw:
            match["category_is"] = _parse_inline_list(raw)
            return (True, None)
        else:
            match["category_is"] = []
            return (True, "category_is")

    if stripped == "tokens_in_text:" or stripped.startswith("tokens_in_text:"):
        raw = _yv(stripped)
        if raw:
            match["tokens_in_text"] = _parse_inline_list(raw)
            return (True, None)
        else:
            match["tokens_in_text"] = []
            return (True, "tokens_in_text")

    if stripped == "source_section_tokens:" or stripped.startswith("source_section_tokens:"):
        raw = _yv(stripped)
        if raw:
            match["source_section_tokens"] = _parse_inline_list(raw)
            return (True, None)
        match["source_section_tokens"] = []
        return (True, "source_section_tokens")

    if stripped.startswith("source_section_regex:"):
        match["source_section_regex"] = _yv(stripped)
        return (True, None)

    if stripped.startswith("capability_pattern:"):
        match["capability_pattern"] = _yv(stripped) == "true"
        return (True, None)

    if stripped.startswith("regex:"):
        match["regex"] = _yv(stripped)
        return (True, None)

    return (False, None)


def _finalise_rule(rule: dict[str, Any], match: dict[str, Any] | None) -> dict[str, Any]:
    """Attach the accumulated match block to the rule."""
    if match:
        rule["match"] = match
    return rule


def _yv(stripped: str) -> str:
    """Extract the value part of ``key: value`` from a stripped line."""
    _, _, value = stripped.partition(":")
    return value.strip().strip('"').strip("'")


def _parse_inline_list(raw: str) -> list[str]:
    """Parse an inline YAML/JSON list like ``["a", "b"]`` or ``[a, b]``."""
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        items = re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,]+)', inner)
        return [
            (g[0] or g[1] or g[2]).strip().strip('"').strip("'")
            for g in items
            if (g[0] or g[1] or g[2]).strip()
        ]
    return [raw]


def _parse_capability_patterns(text: str) -> dict[str, Any]:
    """Parse the ``capability_patterns:`` section."""
    result: dict[str, Any] = {"tokens": [], "regexes": []}
    lines = text.splitlines()
    idx = 0

    # Advance to ``capability_patterns:``
    while idx < len(lines):
        if lines[idx].strip() == "capability_patterns:":
            idx += 1
            break
        idx += 1

    current_list: str | None = None
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        line_indent = len(line) - len(line.lstrip())
        if not stripped or stripped.startswith("#"):
            idx += 1
            continue
        # Stop at another top-level key (indent 0, not a list item)
        if line_indent == 0 and ":" in stripped and current_list is None:
            break
        if stripped == "tokens:" or stripped.startswith("tokens:"):
            raw = _yv(stripped)
            if raw:
                result["tokens"] = _parse_inline_list(raw)
            else:
                current_list = "tokens"
            idx += 1
            continue
        if stripped == "regexes:" or stripped.startswith("regexes:"):
            raw = _yv(stripped)
            if raw:
                result["regexes"] = _parse_inline_list(raw)
            else:
                current_list = "regexes"
            idx += 1
            continue
        if stripped.startswith("- ") and current_list:
            value = stripped[2:].strip().strip('"').strip("'")
            result[current_list].append(value)
        idx += 1

    return result
