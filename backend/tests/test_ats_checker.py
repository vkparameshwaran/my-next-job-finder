from app.analyzer.ats_checker import keyword_overlap, overlap_ratio
from app.models.resume import ResumeDoc


def _resume(raw: str) -> ResumeDoc:
    return ResumeDoc(raw_text=raw)


def test_overlap_empty_when_no_jd() -> None:
    assert keyword_overlap(_resume("python rust go"), None) == {}


def test_overlap_marks_present_and_missing_tokens() -> None:
    resume = _resume("Built distributed systems in Python and Go")
    overlap = keyword_overlap(resume, "Looking for Python and Kubernetes experts")
    assert overlap["python"] is True
    assert overlap["kubernetes"] is False


def test_overlap_ignores_stopwords() -> None:
    overlap = keyword_overlap(_resume("the and or to"), "the and or to React")
    assert "and" not in overlap
    assert overlap["react"] is False


def test_overlap_ratio_handles_empty_dict() -> None:
    assert overlap_ratio({}) == 0.0


def test_overlap_ratio_computes_hit_rate() -> None:
    assert overlap_ratio({"a": True, "b": False, "c": True}) == 2 / 3
