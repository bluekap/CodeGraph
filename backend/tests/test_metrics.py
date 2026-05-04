import unittest
from pathlib import Path

from codegraph.analyzer.metrics import MetricsAnalyzer


class MetricsAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = MetricsAnalyzer()

    def test_analyze_file_reports_basic_metrics(self):
        content = """
class Example:
    def choose(self, value):
        if value:
            return "yes"
        return "no"
"""

        metrics = self.analyzer.analyze_file(Path("example.py"), content)

        self.assertGreater(metrics["loc"], 0)
        self.assertEqual(metrics["classes"], 1)
        self.assertEqual(metrics["functions"], 1)
        self.assertGreater(metrics["complexity"], 0)
        self.assertEqual(
            [item["name"] for item in metrics["function_details"]],
            ["Example", "choose"],
        )

    def test_calculate_repository_stats_handles_empty_input(self):
        self.assertEqual(
            self.analyzer.calculate_repository_stats([]),
            {
                "total_files": 0,
                "total_loc": 0,
                "avg_complexity": 0,
                "max_complexity": 0,
                "total_functions": 0,
                "total_classes": 0,
            },
        )

    def test_get_file_language_uses_extension(self):
        self.assertEqual(self.analyzer.get_file_language(Path("tool.py")), "python")
        self.assertEqual(self.analyzer.get_file_language(Path("unknown.txt")), "unknown")


if __name__ == "__main__":
    unittest.main()
