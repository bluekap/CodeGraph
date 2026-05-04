import tempfile
import unittest
from pathlib import Path

from codegraph.analyzer.git_handler import GitHandler


class GitHandlerFilePatternTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

        (self.repo_root / "src" / "package").mkdir(parents=True)
        (self.repo_root / "tests").mkdir()
        (self.repo_root / "docs").mkdir()

        (self.repo_root / "app.py").write_text("print('app')\n", encoding="utf-8")
        (self.repo_root / "src" / "package" / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo_root / "tests" / "test_module.py").write_text("def test_module():\n    pass\n", encoding="utf-8")
        (self.repo_root / "docs" / "notes.md").write_text("# Notes\n", encoding="utf-8")

        self.handler = GitHandler()
        self.handler.temp_dir = self.repo_root

    def tearDown(self):
        self.temp_dir.cleanup()

    def relative_results(self, pattern, include_tests=False):
        files = self.handler.get_python_files(pattern=pattern, include_tests=include_tests)
        return sorted(path.relative_to(self.repo_root).as_posix() for path in files)

    def test_file_pattern_limits_results(self):
        self.assertEqual(
            self.relative_results("src/**/*.py"),
            ["src/package/module.py"],
        )

    def test_python_files_exclude_tests_by_default(self):
        self.assertEqual(
            self.relative_results("**/*.py"),
            ["app.py", "src/package/module.py"],
        )

    def test_python_files_can_include_tests(self):
        self.assertEqual(
            self.relative_results("**/*.py", include_tests=True),
            ["app.py", "src/package/module.py", "tests/test_module.py"],
        )


if __name__ == "__main__":
    unittest.main()
