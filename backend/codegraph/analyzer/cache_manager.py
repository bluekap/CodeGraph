import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional

class CacheManager:
    """Manages the .agents cache and artifact storage"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.agents_dir = self.repo_path / ".agents" / "codegraph"
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
            
    def is_cache_valid(self) -> bool:
        """Check if the cache matches the current commit hash"""
        if not self.cache_file.exists():
            return False
            
        current_hash = self.get_current_commit_hash()
        if not current_hash:
            return False
            
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                return data.get("commit_hash") == current_hash
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
        
        cache_data = {
            "commit_hash": current_hash,
            "data": data
        }
        
        try:
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            print(f"Error saving cache: {e}")
