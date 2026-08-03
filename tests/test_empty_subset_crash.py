import json
import threading
import time
import unittest
import urllib.error
import urllib.request

from ragpoisonbench.core import DEMO, analyze
from ragpoisonbench.server import serve


class EmptySubsetCrashTest(unittest.TestCase):
    """_evaluate indexed ranking[0] directly. Whenever a document subset
    (clean/defended/attacked) ends up with zero documents -- entirely
    plausible for a corpus with no trust==1.0 document, or a threshold that
    quarantines everything -- retrieve() returns an empty list and
    ranking[0] raised an uncaught IndexError, crashing the unauthenticated
    /api/analyze endpoint with no HTTP response."""

    def test_no_high_trust_document_does_not_crash(self):
        payload = {
            "trust_threshold": 0.6,
            "queries": [{"id": "q1", "text": "hello", "expected_doc": "a"}],
            "documents": [{"id": "a", "source": "x", "trust": 0.5, "text": "hello world"}],
        }
        result = analyze(payload)
        self.assertEqual(result["clean_recall_at_1"], 0.0)
        self.assertEqual(result["defended_recall_at_1"], 0.0)

    def test_empty_documents_does_not_crash(self):
        payload = {
            "trust_threshold": 0.6,
            "queries": [{"id": "q1", "text": "hello", "expected_doc": "a"}],
            "documents": [],
        }
        result = analyze(payload)
        self.assertEqual(result["attacked_recall_at_1"], 0.0)

    def test_live_server_survives_empty_trust_subset(self):
        server_thread = threading.Thread(target=serve, args=("127.0.0.1", 8098), daemon=True)
        server_thread.start()
        time.sleep(0.3)
        payload = {
            "trust_threshold": 0.6,
            "queries": [{"id": "q1", "text": "hello", "expected_doc": "a"}],
            "documents": [{"id": "a", "source": "x", "trust": 0.5, "text": "hello world"}],
        }
        request = urllib.request.Request(
            "http://127.0.0.1:8098/api/analyze",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            response = urllib.request.urlopen(request, timeout=3)
        except (urllib.error.URLError, ConnectionResetError) as error:
            self.fail(f"server crashed instead of returning a response: {error}")
        self.assertEqual(response.status, 200)

    def test_demo_output_unaffected(self):
        result = analyze(DEMO)
        self.assertEqual(result["clean_recall_at_1"], 1.0)
        self.assertEqual(result["attacked_recall_at_1"], 0.0)
        self.assertEqual(result["defended_recall_at_1"], 1.0)
        self.assertEqual(result["attack_success_rate"], 1.0)
        self.assertEqual(result["single_document_influence_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
