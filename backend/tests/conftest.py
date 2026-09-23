import os
import sys
from pathlib import Path

# Force offline mock mode for all tests regardless of any local .env, so the
# test suite never attempts a live Gemini call.
os.environ["GEMINI_MOCK_MODE"] = "true"
os.environ.setdefault("GEMINI_API_KEY", "")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import store


@pytest.fixture()
def client():
    # Reset in-memory store between tests for isolation.
    store.documents.clear()
    store.sessions.clear()
    return TestClient(app)
