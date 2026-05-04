# Modules Cache
- Scope: top 9 high-value files (entrypoints + connected modules).
- Cap: 10 symbols per file.

## `backend/codegraph/__main__.py`
- fn `analyze_repo(repo_path, force, max_files, file_pattern)`
- fn `export_repo(repo_path, format_type, out_path)`
- fn `main()`

## `backend/codegraph/models/schemas.py`
- class `AnalyzeRequest`
- class `NodeData`
- class `EdgeData`
- class `RepositoryMetrics`
- class `AnalyzeResponse`
- class `ErrorResponse`

## `backend/codegraph/analyzer/dependency_parser.py`
- class `DependencyParser`
  - `__init__(self)`
  - `parse_imports(self, file_path, content)`
  - `parse_symbols(self, file_path, content)`
  - `resolve_local_imports(self, file_path, imports, all_files)`
  - `build_module_map(self, files, repo_root)`
  - `calculate_coupling(self, edges)`
  - `find_circular_dependencies(self, edges)`

## `backend/codegraph/analyzer/metrics.py`
- class `MetricsAnalyzer`
  - `analyze_file(self, file_path, content)`
  - `calculate_complexity_color(self, complexity)`
  - `calculate_node_size(self, loc, min_size, max_size)`
  - `get_file_language(self, file_path)`
  - `calculate_repository_stats(self, all_metrics)`

## `backend/codegraph/analyzer/repository_analyzer.py`
- class `RepositoryAnalyzer`
  - `__init__(self)`
  - `analyze_repository(self, repo_url, max_files, include_tests, file_pattern)`
  - `__enter__(self)`
  - `__exit__(self, exc_type, exc_val, exc_tb)`

## `backend/codegraph/agent_tools.py`
- fn `get_repository_architecture(path)`
- fn `get_module_details(path)`
- fn `get_complexity_hotspots(path)`

## `backend/codegraph/analyzer/artifact_generator.py`
- class `ArtifactGenerator`
  - `__init__(self, codegraph_dir)`
  - `generate_all(self, analysis_data)`
  - `generate_architecture(self, data)`
  - `generate_modules(self, data)`
  - `generate_hotspots(self, data)`

## `backend/codegraph/analyzer/cache_manager.py`
- class `CacheManager`
  - `__init__(self, repo_path)`
  - `get_current_commit_hash(self)`
  - `is_cache_valid(self)`
  - `load_cache(self)`
  - `save_cache(self, data)`

## `backend/codegraph/analyzer/git_handler.py`
- class `GitHandler`
  - `__init__(self)`
  - `clone_repository(self, repo_url)`
  - `get_python_files(self, max_files, include_tests, pattern)`
  - `get_file_content(self, file_path)`
  - `get_relative_path(self, file_path)`
  - `get_repo_name(self, repo_url)`
  - `cleanup(self)`
  - `__enter__(self)`
  - `__exit__(self, exc_type, exc_val, exc_tb)`
