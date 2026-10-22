from app.services.extractor import extract_criteria

SAMPLE = """Inclusion Criteria:
- Adults aged 18 years or older
- Histologically confirmed stage IV non-small cell lung cancer
- ECOG performance status 0-1
- Hemoglobin >= 9 g/dL

Exclusion Criteria:
- Pregnant or breastfeeding women
- Prior treatment with immune checkpoint inhibitors
"""


def by_text(result, fragment):
    return next(c for c in result["criteria"] if fragment in c["text"])


def test_sections_and_counts():
    r = extract_criteria(SAMPLE)
    assert r["summary"]["total"] == 6
    assert r["summary"]["inclusion"] == 4
    assert r["summary"]["exclusion"] == 2


def test_age_min():
    c = by_text(extract_criteria(SAMPLE), "aged 18")
    assert (c["field"], c["operator"], c["value"]) == ("age", ">=", 18.0)


def test_age_range():
    c = extract_criteria("Patients aged 18 to 75 years")["criteria"][0]
    assert c["operator"] == "between" and c["value"] == [18.0, 75.0]


def test_ecog_and_lab():
    r = extract_criteria(SAMPLE)
    assert by_text(r, "ECOG")["value"] == 1.0
    lab = by_text(r, "Hemoglobin")
    assert lab["field"] == "lab:hemoglobin" and lab["operator"] == ">=" and lab["value"] == 9.0


def test_unknown_goes_to_manual_review():
    c = by_text(extract_criteria(SAMPLE), "checkpoint")
    assert c["status"] == "manual_review" and c["field"] is None


def test_span_points_to_original_text():
    r = extract_criteria(SAMPLE)
    for c in r["criteria"]:
        start, end = c["span"]
        assert SAMPLE[start:end] == c["text"]  # evidence is exact
