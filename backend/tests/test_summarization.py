from backend.app.services.summarizer import Summarizer


def test_summarizer_short_text():
    s = Summarizer()
    text = """
    The company encourages continuous learning. Employees can enroll in training programs via LMS.
    Security policies must be followed strictly including password hygiene and device encryption.
    """.strip()
    out = s.summarize(text)
    assert isinstance(out, str)
    assert len(out) > 0


