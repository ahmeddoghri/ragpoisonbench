import unittest

from ragpoisonbench.sweep import run


class TrustSweepTest(unittest.TestCase):
    def test_the_defense_is_exactly_a_step_function_at_the_threshold(self):
        result = run()
        self.assertTrue(result["defense_is_a_step_function_at_threshold"], result["rows"])

    def test_poison_from_a_trusted_source_is_not_defended_at_all(self):
        rows = {row["poison_trust"]: row for row in run()["rows"]}
        at_threshold = rows[1.0]
        self.assertEqual(at_threshold["quarantined"], 0)
        self.assertEqual(at_threshold["defended_recall_at_1"], at_threshold["attacked_recall_at_1"])

    def test_low_trust_poison_is_fully_defended(self):
        rows = {row["poison_trust"]: row for row in run()["rows"]}
        self.assertEqual(rows[0.1]["defended_recall_at_1"], 1.0)


if __name__ == "__main__":
    unittest.main()
