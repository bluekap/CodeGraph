"""
Git repository handler for cloning and analyzing repositories
"""
import os
import tempfile
import shutil
import stat
from pathlib import Path
from typing import List, Optional
from git import Repo, GitCommandError


class GitHandler:
    """Handle Git repository operations"""
    
    def __init__(self):
        self.temp_dir: Optional[Path] = None
        self.repo: Optional[Repo] = None
    
    def clone_repository(self, repo_url: str) -> Path:
        """
        Clone a GitHub repository to a temporary directory
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Path to cloned repository
            
        Raises:
            ValueError: If repo_url is invalid
            GitCommandError: If cloning fails
        """
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="codegraph_"))
        
        try:
            # Clone the repository
            print(f"Cloning {repo_url}...")
            self.repo = Repo.clone_from(repo_url, self.temp_dir, depth=1)
            print(f"Repository cloned to {self.temp_dir}")
            return self.temp_dir
        except GitCommandError as e:
            self.cleanup()
            raise ValueError(f"Failed to clone repository: {str(e)}")
    
    def get_source_files(self, max_files: int = 100, include_tests: bool = False, pattern: str = "*.py") -> List[Path]:
        """
        Get source files from the repository matching a glob pattern.
        
        Args:
            max_files: Maximum number of files to return
            include_tests: Whether to include test files
            pattern: Glob pattern to match files
            
        Returns:
            List of source file paths
        """
        if not self.temp_dir:
            raise ValueError("No repository cloned")
        
        source_files = []
        exclude_patterns = [
            '__pycache__',
            '.git',
            'venv',
            'env',
            '.venv',
            'node_modules',
            'build',
            'dist',
            '.pytest_cache',
            '.tox'
        ]
        
        if not include_tests:
            exclude_patterns.extend(['test_', 'tests/', 'test/'])
        
        for source_file in self.temp_dir.rglob(pattern):
            # Skip excluded patterns
            if any(pattern in str(source_file) for pattern in exclude_patterns):
                continue
            
            # Skip empty files
            if source_file.stat().st_size == 0:
                continue
            
            source_files.append(source_file)
            
            if len(source_files) >= max_files:
                break
        
        return source_files

    def get_python_files(self, max_files: int = 100, include_tests: bool = False, pattern: str = "*.py") -> List[Path]:
        """Backward-compatible alias for older callers."""
        return self.get_source_files(max_files=max_files, include_tests=include_tests, pattern=pattern)
    
    def get_file_content(self, file_path: Path) -> str:
        """
        Read file content safely
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
        """
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            return file_path.read_text(encoding='latin-1')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def get_relative_path(self, file_path: Path) -> str:
        """
        Get relative path from repository root
        
        Args:
            file_path: Absolute file path
            
        Returns:
            Relative path string
        """
        if not self.temp_dir:
            return str(file_path)
        
        try:
            return str(file_path.relative_to(self.temp_dir))
        except ValueError:
            return str(file_path)
    
    def get_repo_name(self, repo_url: str) -> str:
        """
        Extract repository name from URL
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Repository name (e.g., 'flask' from 'https://github.com/pallets/flask')
        """
        # Remove .git suffix if present
        url = repo_url.rstrip('.git')
        # Extract last part
        return url.rstrip('/').split('/')[-1]
    
    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            def onerror(func, path, exc_info):
                """
                Error handler for ``shutil.rmtree``.

                If the error is due to an access error (read only file)
                it attempts to add write permission and then retries.

                If the error is for another reason it re-raises the error.

                Usage : ``shutil.rmtree(path, onerror=onerror)``
                """
                if not os.access(path, os.W_OK):
                    # Is the error an access error ?
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise

            try:
                shutil.rmtree(self.temp_dir, onerror=onerror)
                print(f"Cleaned up {self.temp_dir}")
            except Exception as e:
                print(f"Error cleaning up: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
