import tempfile
import unittest
from pathlib import Path

from codegraph.analyzer.artifact_generator import ArtifactGenerator


class ArtifactGeneratorTests(unittest.TestCase):
    def test_generate_all_writes_expected_markdown_files(self):
        analysis_data = {
            "nodes": [
                {
                    "path": "src/app.py",
                    "name": "app.py",
                    "complexity": 2.0,
                    "symbols": {
                        "classes": [],
                        "functions": [
                            {
                                "name": "main",
                                "args": [],
                                "docstring": "Run the app.",
                            }
                        ],
                    },
                    "function_details": [
                        {
                            "name": "main",
                            "type": "function",
                            "complexity": 2.0,
                        }
                    ],
                }
            ],
            "edges": [
                {
                    "source": "src/app.py",
                    "target": "src/config.py",
                }
            ],
            "metrics": {
                "total_files": 1,
                "total_loc": 12,
                "avg_complexity": 2.0,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            ArtifactGenerator(str(output_dir)).generate_all(analysis_data)

            architecture = output_dir / "architecture.md"
            file_level = output_dir / "architecture-file-level.md"
            modules = output_dir / "modules.md"
            hotspots = output_dir / "hotspots.md"

            self.assertTrue(architecture.exists())
            self.assertTrue(file_level.exists())
            self.assertTrue(modules.exists())
            self.assertTrue(hotspots.exists())
            self.assertIn("# Architecture Index", architecture.read_text(encoding="utf-8"))
            self.assertIn("graph TD;", file_level.read_text(encoding="utf-8"))
            self.assertIn("fn `main()`", modules.read_text(encoding="utf-8"))
            self.assertIn("src/app.py", hotspots.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
