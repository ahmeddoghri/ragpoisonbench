import unittest

from ragpoisonbench.core import DEMO, analyze, retrieve


class RagPoisonBenchTests(unittest.TestCase):
    def test_attack_controls_top_rank(self):
        result = analyze(DEMO)
        self.assertEqual(result["attacked_recall_at_1"], 0.0)
        self.assertEqual(result["attack_success_rate"], 1.0)

    def test_provenance_quarantine_restores_recall(self):
        result = analyze(DEMO)
        self.assertEqual(result["quarantined_documents"], 4)
        self.assertEqual(result["defended_recall_at_1"], 1.0)
        self.assertTrue(result["clean_recall_preserved"])

    def test_leave_one_document_out_identifies_influence(self):
        result = analyze(DEMO)
        self.assertEqual(result["single_document_influence_rate"], 1.0)

    def test_retrieval_is_deterministic(self):
        first = retrieve(DEMO["queries"][0]["text"], DEMO["documents"])
        second = retrieve(DEMO["queries"][0]["text"], DEMO["documents"])
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
