from backend.domain.review_cleaner import clean_review_text


def test_clean_review_text_normalizes_and_removes_noise():
    raw_text = "Amazing product!!! 😍 Works grêat... 10/10."

    cleaned = clean_review_text(raw_text)

    assert cleaned == "Amazing product Works gre at 10 10"


def test_clean_review_text_returns_empty_string_for_non_string_input():
    assert clean_review_text(None) == ""
