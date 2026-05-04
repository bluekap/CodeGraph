import unittest
from pathlib import Path

from codegraph.analyzer.dependency_parser import DependencyParser


class DependencyParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = DependencyParser()

    def test_parse_imports_extracts_top_level_modules(self):
        content = """
import os
import codegraph.analyzer.metrics
from pathlib import Path
from codegraph.models.schemas import NodeData
"""

        self.assertEqual(
            sorted(self.parser.parse_imports(Path("example.py"), content)),
            ["codegraph.analyzer.metrics", "codegraph.models.schemas", "os", "pathlib"],
        )

    def test_parse_symbols_extracts_classes_functions_and_docstrings(self):
        content = '''
class Example:
    """Example class."""

    def method(self, value):
        """Method docstring."""
        return value


async def load(path):
    """Load something."""
    return path
'''

        symbols = self.parser.parse_symbols(Path("example.py"), content)

        self.assertEqual(symbols["classes"][0]["name"], "Example")
        self.assertEqual(symbols["classes"][0]["docstring"], "Example class.")
        self.assertEqual(symbols["classes"][0]["methods"][0]["args"], ["self", "value"])
        self.assertEqual(symbols["functions"][0]["name"], "load")
        self.assertEqual(symbols["functions"][0]["docstring"], "Load something.")

    def test_resolve_local_imports_matches_module_map(self):
        module_map = {
            "codegraph/analyzer/metrics.py": "codegraph.analyzer.metrics",
            "codegraph/models/schemas.py": "codegraph.models.schemas",
        }

        self.assertEqual(
            sorted(
                self.parser.resolve_local_imports(
                    "codegraph/analyzer/repository_analyzer.py",
                    ["metrics", "schemas", "json"],
                    module_map,
                )
            ),
            ["codegraph/analyzer/metrics.py", "codegraph/models/schemas.py"],
        )

    def test_find_circular_dependencies_reports_cycle(self):
        cycles = self.parser.find_circular_dependencies(
            [("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py")]
        )

        self.assertIn(["a.py", "b.py", "c.py", "a.py"], cycles)


if __name__ == "__main__":
    unittest.main()
