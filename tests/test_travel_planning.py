import unittest
from agents.validation import validate_requirements
from agents.budget_agent import budget_agent

class TravelPlanningTests(unittest.TestCase):
    def valid(self):
        return {"origin": "Visakhapatnam", "destination": "Hyderabad", "days": 3,
                "people": 4, "budget": 30000, "transport": "train"}

    def test_success_valid_requirements(self):
        self.assertTrue(validate_requirements(self.valid()))

    def test_success_budget_estimation(self):
        result = budget_agent(self.valid(), 1800)
        self.assertGreater(result["Total Estimated Cost"], 0)
        self.assertEqual(result["Total Budget"], 30000)

    def test_failure_zero_days(self):
        data = self.valid(); data["days"] = 0
        with self.assertRaisesRegex(ValueError, "days"):
            validate_requirements(data)

    def test_failure_negative_budget(self):
        data = self.valid(); data["budget"] = -5000
        with self.assertRaisesRegex(ValueError, "budget"):
            validate_requirements(data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
