import os
import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, Optional

class CacheManager:
    """Manages the .agents cache and artifact storage"""
    CACHE_SCHEMA_VERSION = "2"
    
    def __init__(self, repo_path: str, output_dir: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.agents_dir = Path(output_dir) if output_dir else self.repo_path / ".agents" / "codegraph"
        self.cache_file = self.agents_dir / "cache.json"
        
        # Create directory if it doesn't exist
        os.makedirs(self.agents_dir, exist_ok=True)
        
    def get_current_commit_hash(self) -> Optional[str]:
        """Get the current git commit hash of the repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def get_working_tree_fingerprint(self) -> Optional[str]:
        """Fingerprint uncommitted changes so cache can be invalidated before commit."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            status_output = result.stdout
            return hashlib.sha256(status_output.encode("utf-8")).hexdigest()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
            
    def is_cache_valid(self) -> bool:
        """Check if cache matches commit, worktree state, and schema version."""
        if not self.cache_file.exists():
            return False
            
        current_hash = self.get_current_commit_hash()
        current_tree = self.get_working_tree_fingerprint()
        if not current_hash:
            return False
            
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                return (
                    data.get("schema_version") == self.CACHE_SCHEMA_VERSION
                    and data.get("commit_hash") == current_hash
                    and data.get("working_tree_fingerprint") == current_tree
                )
        except (json.JSONDecodeError, IOError):
            return False
            
    def load_cache(self) -> Optional[Dict]:
        """Load the analysis data from cache"""
        if not self.is_cache_valid():
            return None
            
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f).get("data")
        except (json.JSONDecodeError, IOError):
            return None
            
    def save_cache(self, data: Dict):
        """Save analysis data to cache with the current commit hash"""
        current_hash = self.get_current_commit_hash()
        current_tree = self.get_working_tree_fingerprint()
        
        cache_data = {
            "schema_version": self.CACHE_SCHEMA_VERSION,
            "commit_hash": current_hash,
            "working_tree_fingerprint": current_tree,
            "data": data
        }
        
        try:
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            print(f"Error saving cache: {e}")
