from backend.app.services.keyword_extractor import KeywordExtractor


def test_keywords():
    k = KeywordExtractor()
    text = "Employees must follow HR policies, security policies, and IT guidelines."
    kws = k.extract(text)
    assert isinstance(kws, list)
    assert len(kws) > 0


