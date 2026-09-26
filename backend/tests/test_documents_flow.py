"""End-to-end-ish tests over the document flow, run in offline mock mode
(no live Gemini call, no network/API key needed). Ingestion always returns
the same deterministic mock "extracted" rental-agreement text in mock mode
(see app/gemini_client.py _mock_response / call_pro_multimodal), which is
what these tests exercise the rest of the pipeline against.
"""
import io


def _upload_sample_document(client):
    file_content = io.BytesIO(b"%PDF-1.4 fake pdf bytes for testing")
    resp = client.post(
        "/documents",
        files={"file": ("sample.pdf", file_content, "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_upload_returns_document_id(client):
    body = _upload_sample_document(client)
    assert "id" in body
    assert body["guardrail"]["disclaimer"]


def test_get_document_returns_masked_text(client):
    body = _upload_sample_document(client)
    doc_id = body["id"]
    resp = client.get(f"/documents/{doc_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "security deposit" in data["masked_text"].lower()


def test_unsupported_content_type_rejected(client):
    file_content = io.BytesIO(b"not a real doc")
    resp = client.post(
        "/documents",
        files={"file": ("sample.txt", file_content, "text/plain")},
    )
    assert resp.status_code == 400


def test_classify_flags_plain_rental_agreement_as_not_high_stakes(client):
    body = _upload_sample_document(client)
    doc_id = body["id"]
    resp = client.post(f"/documents/{doc_id}/actions/classify")
    assert resp.status_code == 200
    data = resp.json()
    assert data["document_type"] == "rental_agreement"
    assert data["high_stakes"] is False


def test_explain_returns_three_levels_both_languages_with_citations(client):
    body = _upload_sample_document(client)
    doc_id = body["id"]
    resp = client.post(f"/documents/{doc_id}/actions/explain")
    assert resp.status_code == 200
    data = resp.json()
    for lang_key in ("english", "kannada"):
        levels = data[lang_key]
        assert levels["gist"]
        assert levels["clause_by_clause"]
        assert levels["legal_view"]
        assert isinstance(levels["citations"], list)
        assert len(levels["citations"]) > 0


def test_red_flags_detects_planted_issues(client):
    body = _upload_sample_document(client)
    doc_id = body["id"]
    resp = client.post(f"/documents/{doc_id}/actions/red-flags")
    assert resp.status_code == 200
    data = resp.json()
    categories = {f["category"] for f in data["flags"]}
    # The mock ingestion text plants: 10-month deposit, and an
    # unconditional painting/cleaning deduction clause — at least these two
    # categories must be caught, each with a non-empty citation.
    assert "deposit_size" in categories
    assert "painting_cleaning_deduction" in categories
    for flag in data["flags"]:
        assert flag["citation"]


def test_red_flags_clean_document_has_no_false_flags(client):
    file_content = io.BytesIO(b"%PDF-1.4 placeholder")
    resp = client.post(
        "/documents",
        files={"file": ("clean.pdf", file_content, "application/pdf")},
    )
    doc_id = resp.json()["id"]

    # Directly exercise the detector against genuinely clean text (the mock
    # ingestion path always returns the same planted-issue sample text, so
    # to test the "no false flags" side of C11's acceptance criteria we
    # call the detector function directly against clean text here rather
    # than through the mocked ingestion endpoint).
    from app.red_flags import detect_red_flags

    clean_text = (
        "This rental agreement is between the landlord and the tenant. "
        "The security deposit is 2 months' rent. Both parties may "
        "terminate with 2 months notice."
    )
    flags = detect_red_flags(clean_text)
    assert flags == []


def test_qa_in_scope_question_returns_citation_and_confidence(client):
    body = _upload_sample_document(client)
    doc_id = body["id"]
    resp = client.post(
        f"/documents/{doc_id}/actions/qa",
        json={"question": "Is the security deposit amount normal?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["i_dont_know"] is False
    assert data["citation"]
    assert data["confidence"] in ("High", "Medium")


def test_qa_out_of_scope_question_returns_i_dont_know(client):
    body = _upload_sample_document(client)
    doc_id = body["id"]
    resp = client.post(
        f"/documents/{doc_id}/actions/qa",
        json={"question": "What is the capital of France?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["i_dont_know"] is True
    assert data["citation"] is None


def test_high_stakes_document_gets_legal_aid_redirect(client):
    file_content = io.BytesIO(b"%PDF-1.4 placeholder")
    resp = client.post(
        "/documents",
        files={"file": ("hs.pdf", file_content, "application/pdf")},
    )
    doc_id = resp.json()["id"]

    # Force high-stakes by directly manipulating the stored record's text,
    # since mock ingestion always returns the same sample text; this
    # isolates the guardrail-wiring behavior (C16) from the classification
    # heuristic (C8), which is tested separately.
    from app.storage import store

    store.documents[doc_id].masked_text += " There was an arrest involved."

    classify_resp = client.post(f"/documents/{doc_id}/actions/classify")
    assert classify_resp.json()["high_stakes"] is True

    explain_resp = client.post(f"/documents/{doc_id}/actions/explain")
    assert explain_resp.status_code == 200
    explain_data = explain_resp.json()
    assert explain_data["guardrail"]["high_stakes"] is True
    assert "legal aid" in explain_data["guardrail"]["legal_aid_redirect"].lower()

    qa_resp = client.post(
        f"/documents/{doc_id}/actions/qa", json={"question": "What should I do?"}
    )
    qa_data = qa_resp.json()
    assert qa_data["guardrail"]["high_stakes"] is True
