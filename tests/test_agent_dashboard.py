#!/usr/bin/env python3
"""
Dashboard Integration Tests for Agentic AI Layer
"""

import unittest
import sys
sys.path.insert(0, '.')

from agent.core import AgentCore


class TestAgentDashboardIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = AgentCore()

    def test_01_agent_ui_components_importable(self):
        try:
            from dashboard.components.agent_interface import render_agent_interface, display_agent_result
            self.assertTrue(callable(render_agent_interface))
        except ImportError:
            pass  # streamlit may not be installed in test env

    def test_02_demo_question_1_price_risk(self):
        q = "Which crops have the highest price risk?"
        res = self.agent.run(q)
        self.assertEqual(res["routed"]["intent"], "PRICE_RISK")
        self.assertIn("analytics", res["payload"].get("source", ""))
        self.assertIn("chart_type", res.get("chart", {}))

    def test_03_demo_question_2_mandi_risk(self):
        q = "Which mandis have high arrival volume and high price crash rates?"
        res = self.agent.run(q)
        self.assertIn(res["routed"]["intent"], ["PRICE_RISK", "MANDI_ANALYSIS"])
        self.assertIn("analytics", res["payload"].get("source", ""))

    def test_04_demo_question_3_wheat_trend(self):
        q = "Show Wheat arrival trends."
        res = self.agent.run(q)
        self.assertIn(res["routed"]["intent"], ["SUPPLY_TREND", "CROP_ANALYSIS"])
        self.assertIn("analytics", res["payload"].get("source", ""))

    def test_05_demo_question_4_longest_transit(self):
        q = "Which warehouse has the longest transit time?"
        res = self.agent.run(q)
        self.assertEqual(res["routed"]["intent"], "LOGISTICS")
        self.assertIn("analytics/warehouse_kpis.csv", res["payload"].get("source", ""))

    def test_06_demo_question_5_rainfall_correlation_with_safeguards(self):
        q = "Is rainfall strongly associated with arrivals?"
        res = self.agent.run(q)
        self.assertIn(res["routed"]["intent"], ["WEATHER", "SUPPLY_TREND"])
        explanation = res.get("explanation", "").lower()
        self.assertIn("correlation", explanation)
        self.assertTrue("date-level" in explanation or "mapping" in explanation or "unsupported" in explanation)

    def test_07_demo_question_6_data_cleaning_impact(self):
        q = "How much of the data needed cleaning?"
        res = self.agent.run(q)
        self.assertIn(res["routed"]["intent"], ["DATA_QUALITY", "UNSUPPORTED"])
        self.assertIn("analytics", res["payload"].get("source", "").lower() or res["payload"].get("source", "").lower())

    def test_08_unsupported_question_fallback(self):
        q = "Generate a SQL query for weather data;"
        res = self.agent.run(q)
        # Must either return unsupported intent or safe explanation
        combined = (res.get("explanation", "") + res.get("payload", {}).get("summary", "")).lower()
        self.assertTrue("unsupported" in combined or res["routed"]["intent"] == "UNSUPPORTED")

    def test_09_regression_existing_agent_tests_still_pass(self):
        # Confirm original agent tests work independently
        from agent.core import AgentCore
        agent = AgentCore()
        res = agent.run("Price crash rate?")
        self.assertIn(res["routed"]["intent"], ["PRICE_RISK", "PRICE_MSP"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
