"""Criteria Analyzer — baseline version (rule-based, no AI yet).

What it does:
  1. Splits eligibility text into INCLUSION and EXCLUSION sections.
  2. Splits each section into single criteria (one per line/bullet).
  3. Tries to turn each criterion into structured data with regex rules.
  4. Keeps the exact character span of the original text (the "evidence"),
     so a researcher can always check where a result came from.
  5. Anything the rules can't read safely -> status "manual_review".
     We never guess.

Later (Feature Set 1+): add an LLM that proposes structured criteria and
compare it against this baseline. This file is your baseline for that.
"""

import re
from dataclasses import asdict, dataclass
from dataclasses import field as dc_field  # renamed: "field" is also a Criterion attribute

# ---------- data model ----------


@dataclass
class Criterion:
    criterion_type: str  # "inclusion" | "exclusion"
    text: str  # original sentence
    span: tuple[int, int]  # start/end position in the full input text
    field: str | None = None  # e.g. "age", "ecog", "lab:hemoglobin"
    operator: str | None = None  # ">=", "<=", "between", "=", "present"
    value: float | str | list[float] | None = None
    unit: str | None = None
    status: str = "manual_review"  # "structured" | "manual_review"
    rules_matched: list[str] = dc_field(default_factory=list)


# ---------- section + line splitting ----------

INCLUSION_HEADER = re.compile(r"^\s*inclusion\s+criteria\s*:?\s*$", re.I | re.M)
EXCLUSION_HEADER = re.compile(r"^\s*exclusion\s+criteria\s*:?\s*$", re.I | re.M)
BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")


def _sections(text: str) -> list[tuple[str, int, int]]:
    """Return (type, start, end) blocks. Text without headers counts as inclusion."""
    marks = [(m.start(), m.end(), "inclusion") for m in INCLUSION_HEADER.finditer(text)]
    marks += [(m.start(), m.end(), "exclusion") for m in EXCLUSION_HEADER.finditer(text)]
    marks.sort()
    if not marks:
        return [("inclusion", 0, len(text))]
    blocks = []
    for i, (_, header_end, kind) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        blocks.append((kind, header_end, end))
    return blocks


def _lines(text: str, start: int, end: int):
    """Yield (clean_line, abs_start, abs_end) for each non-empty line in a block."""
    pos = start
    for raw in text[start:end].splitlines(keepends=True):
        line_start = pos
        pos += len(raw)
        stripped = raw.strip()
        if not stripped:
            continue
        bullet = BULLET.match(raw)
        offset = bullet.end() if bullet else len(raw) - len(raw.lstrip())
        clean = raw[offset:].rstrip()
        yield clean, line_start + offset, line_start + offset + len(clean)


# ---------- extraction rules ----------

GE = r"(?:>=|≥|at least|or older|or above|and older|minimum of)"
NUM = r"(\d+(?:\.\d+)?)"

AGE_RANGE = re.compile(rf"(?:aged?|age)\D{{0,15}}{NUM}\s*(?:-|–|to)\s*{NUM}\s*years", re.I)
AGE_MIN = re.compile(
    rf"(?:age[d]?\s*{GE}\s*{NUM})|(?:{NUM}\s*years\s*(?:of age\s*)?{GE})|(?:≥\s*{NUM}\s*years)",
    re.I,
)
ECOG = re.compile(
    r"ECOG[^0-9]{0,30}(\d)\s*(?:-|–|to|or)\s*(\d)|ECOG[^0-9]{0,30}(?:≤|<=)\s*(\d)", re.I
)
LAB = re.compile(
    r"(hemoglobin|haemoglobin|platelets?|creatinine|bilirubin|ANC|"
    r"absolute neutrophil count|ALT|AST|eGFR)\D{0,25}?(>=|≥|<=|≤|>|<)\s*"
    rf"{NUM}\s*([a-zA-Z/%µ\^0-9.×x ]{{0,15}})",
    re.I,
)
PREGNANT = re.compile(r"\b(pregnan\w*|breast[- ]?feeding|lactating)\b", re.I)

OPS = {"≥": ">=", "≤": "<="}


def _apply_rules(c: Criterion) -> None:
    t = c.text

    if m := AGE_RANGE.search(t):
        c.field, c.operator, c.unit = "age", "between", "years"
        c.value = [float(m.group(1)), float(m.group(2))]
        c.rules_matched.append("age_range")
    elif m := AGE_MIN.search(t):
        num = next(g for g in m.groups() if g)
        c.field, c.operator, c.value, c.unit = "age", ">=", float(num), "years"
        c.rules_matched.append("age_min")
    elif m := ECOG.search(t):
        c.field, c.operator = "ecog", "<="
        c.value = float(m.group(2) or m.group(3))
        c.rules_matched.append("ecog")
    elif m := LAB.search(t):
        name = m.group(1).lower().replace("haemoglobin", "hemoglobin")
        c.field = f"lab:{name}"
        c.operator = OPS.get(m.group(2), m.group(2))
        c.value = float(m.group(3))
        c.unit = m.group(4).strip() or None
        c.rules_matched.append("lab_threshold")
    elif PREGNANT.search(t):
        c.field, c.operator, c.value = "pregnancy_or_breastfeeding", "present", True
        c.rules_matched.append("pregnancy")

    if c.field:
        c.status = "structured"


# ---------- public function ----------


def extract_criteria(text: str) -> dict:
    """Main entry point. Returns criteria + a small summary."""
    criteria: list[Criterion] = []
    for kind, start, end in _sections(text):
        for clean, s, e in _lines(text, start, end):
            c = Criterion(criterion_type=kind, text=clean, span=(s, e))
            _apply_rules(c)
            criteria.append(c)

    structured = sum(c.status == "structured" for c in criteria)
    return {
        "method": "rule_based_v0",
        "summary": {
            "total": len(criteria),
            "structured": structured,
            "manual_review": len(criteria) - structured,
            "inclusion": sum(c.criterion_type == "inclusion" for c in criteria),
            "exclusion": sum(c.criterion_type == "exclusion" for c in criteria),
        },
        "criteria": [asdict(c) for c in criteria],
    }
