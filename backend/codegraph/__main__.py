#!/usr/bin/env python3
import argparse
import sys
import json
import asyncio
from pathlib import Path

# Add backend directory to sys.path so we can import app
sys.path.insert(0, str(Path(__file__).resolve().parent))

from codegraph.analyzer.repository_analyzer import RepositoryAnalyzer
from codegraph.analyzer.cache_manager import CacheManager
from codegraph.analyzer.artifact_generator import ArtifactGenerator

async def analyze_repo(repo_path: str, force: bool = False, max_files: int = 100, file_pattern: str = "*.py"):
    """Analyze the repository, use cache if available and not forced"""
    repo_path_obj = Path(repo_path).resolve()
    
    if not repo_path_obj.exists() and not repo_path.startswith("http"):
        print(f"Error: Repository path {repo_path} does not exist.")
        sys.exit(1)
        
    cache_mgr = CacheManager(str(repo_path_obj))
    generator = ArtifactGenerator(str(repo_path_obj / ".agents" / "codegraph"))
    
    if not force and cache_mgr.is_cache_valid():
        print("✅ Cache is valid. Loading from cache...")
        data = cache_mgr.load_cache()
        if data:
            print("📝 Generating artifacts from cached data...")
            generator.generate_all(data)
            print(f"✨ Success! Artifacts generated in {cache_mgr.agents_dir}")
            return
            
    print("🔍 Analyzing repository (this may take a moment)...")
    try:
        analyzer = RepositoryAnalyzer()
        # Ensure we pass the string
        nodes, edges, metrics = await analyzer.analyze_repository(
            repo_url=str(repo_path_obj) if not repo_path.startswith("http") else repo_path,
            max_files=max_files,
            file_pattern=file_pattern
        )
        
        # Serialize to dict
        data = {
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges],
            "metrics": metrics.model_dump()
        }
        
        print("💾 Saving to cache...")
        cache_mgr.save_cache(data)
        
        print("📝 Generating artifacts...")
        generator.generate_all(data)
        
        print(f"✨ Success! Artifacts generated in {cache_mgr.agents_dir}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

async def export_repo(repo_path: str, format_type: str, out_path: str = None):
    """Export the analysis data in a specific format"""
    repo_path_obj = Path(repo_path).resolve()
    cache_mgr = CacheManager(str(repo_path_obj))
    
    # Try to load from cache first
    data = cache_mgr.load_cache()
    if not data:
        print("🔍 No valid cache found. Analyzing first...")
        analyzer = RepositoryAnalyzer()
        nodes, edges, metrics = await analyzer.analyze_repository(
            repo_url=str(repo_path_obj) if not repo_path.startswith("http") else repo_path
        )
        data = {
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges],
            "metrics": metrics.model_dump()
        }
        cache_mgr.save_cache(data)

    output = ""
    if format_type == "json":
        output = json.dumps(data, indent=2)
    elif format_type == "markdown":
        output = f"# Export for {repo_path}\nTotal Files: {data['metrics']['total_files']}\nTotal LOC: {data['metrics']['total_loc']}"
    elif format_type == "mermaid":
        content = ["graph TD;"]
        for edge in data.get("edges", []):
            source = edge.get("source", "").replace("/", "_").replace(".", "_")
            target = edge.get("target", "").replace("/", "_").replace(".", "_")
            content.append(f'    {source} --> {target};')
        output = "\n".join(content)
    
    if out_path:
        with open(out_path, "w") as f:
            f.write(output)
        print(f"✨ Exported to {out_path}")
    else:
        print(output)

def main():
    parser = argparse.ArgumentParser(description="CodeGraph - AI Agent Skill for Codebase Analysis")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze repository and generate artifacts")
    analyze_parser.add_argument("repo", help="Path to local repository or GitHub URL")
    analyze_parser.add_argument("--force", action="store_true", help="Force regeneration, ignoring cache")
    analyze_parser.add_argument("--files", help="Specific files pattern to analyze (currently unused)")
    analyze_parser.add_argument("--max-files", type=int, default=100, help="Maximum files to analyze")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Check if the cache is still valid")
    validate_parser.add_argument("repo", help="Path to local repository")
    
    # export command
    export_parser = subparsers.add_parser("export", help="Export analysis in specific format")
    export_parser.add_argument("repo", help="Path to local repository")
    export_parser.add_argument("--format", choices=["json", "markdown", "mermaid"], default="json", help="Format to export")
    export_parser.add_argument("--out", help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        asyncio.run(analyze_repo(args.repo, args.force, args.max_files, args.files or "*.py"))
    elif args.command == "validate":
        cache_mgr = CacheManager(args.repo)
        if cache_mgr.is_cache_valid():
            print("✅ Cache is valid and up to date with the current git commit.")
        else:
            print("❌ Cache is stale or missing. Run 'analyze' to regenerate.")
    elif args.command == "export":
        asyncio.run(export_repo(args.repo, args.format, args.out))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
