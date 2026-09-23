from app.pii import contains_pii, mask_pii


def test_aadhaar_masked():
    text = "My Aadhaar number is 1234 5678 9012 for reference."
    masked = mask_pii(text)
    assert "1234 5678 9012" not in masked
    assert "[REDACTED-AADHAAR]" in masked


def test_pan_masked():
    text = "PAN: ABCDE1234F is on file."
    masked = mask_pii(text)
    assert "ABCDE1234F" not in masked
    assert "[REDACTED-PAN]" in masked


def test_no_pii_left_unchanged():
    text = "This document has no sensitive identifiers in it."
    assert mask_pii(text) == text


def test_contains_pii():
    assert contains_pii("Aadhaar 9999 8888 7777") is True
    assert contains_pii("PAN ABCDE1234F") is True
    assert contains_pii("nothing sensitive here") is False
