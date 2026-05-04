# Complexity Hotspots

This document lists the most complex files and functions in the repository.
High complexity usually indicates areas that are difficult to maintain and could benefit from refactoring.

## Complex Files (Top 10)
| File | Complexity |
|------|------------|
| `backend/codegraph/__main__.py` | 8.67 |
| `backend/codegraph/analyzer/dependency_parser.py` | 5.38 |
| `backend/codegraph/analyzer/metrics.py` | 5.17 |
| `backend/codegraph/analyzer/artifact_generator.py` | 5.17 |
| `backend/codegraph/analyzer/repository_analyzer.py` | 3.00 |
| `backend/codegraph/analyzer/git_handler.py` | 2.70 |
| `backend/codegraph/analyzer/cache_manager.py` | 2.50 |
| `backend/codegraph/agent_tools.py` | 1.75 |
| `backend/codegraph/models/schemas.py` | 1.00 |

## Complex Functions & Methods (Top 20)
| Function/Method | File | Complexity |
|-----------------|------|------------|
| `func:parse_symbols` | `backend/codegraph/analyzer/dependency_parser.py` | 13.00 |
| `func:generate_modules` | `backend/codegraph/analyzer/artifact_generator.py` | 11.00 |
| `func:analyze_repo` | `backend/codegraph/__main__.py` | 10.00 |
| `func:export_repo` | `backend/codegraph/__main__.py` | 10.00 |
| `func:calculate_repository_stats` | `backend/codegraph/analyzer/metrics.py` | 9.00 |
| `func:analyze_file` | `backend/codegraph/analyzer/metrics.py` | 8.00 |
| `func:get_python_files` | `backend/codegraph/analyzer/git_handler.py` | 8.00 |
| `func:generate_hotspots` | `backend/codegraph/analyzer/artifact_generator.py` | 8.00 |
| `func:analyze_repository` | `backend/codegraph/analyzer/repository_analyzer.py` | 8.00 |
| `func:parse_imports` | `backend/codegraph/analyzer/dependency_parser.py` | 8.00 |
| `func:main` | `backend/codegraph/__main__.py` | 6.00 |
| `cls:MetricsAnalyzer` | `backend/codegraph/analyzer/metrics.py` | 6.00 |
| `cls:ArtifactGenerator` | `backend/codegraph/analyzer/artifact_generator.py` | 6.00 |
| `cls:DependencyParser` | `backend/codegraph/analyzer/dependency_parser.py` | 6.00 |
| `func:resolve_local_imports` | `backend/codegraph/analyzer/dependency_parser.py` | 6.00 |
| `func:calculate_complexity_color` | `backend/codegraph/analyzer/metrics.py` | 5.00 |
| `func:is_cache_valid` | `backend/codegraph/analyzer/cache_manager.py` | 4.00 |
| `func:cleanup` | `backend/codegraph/analyzer/git_handler.py` | 4.00 |
| `func:generate_architecture` | `backend/codegraph/analyzer/artifact_generator.py` | 4.00 |
| `cls:RepositoryAnalyzer` | `backend/codegraph/analyzer/repository_analyzer.py` | 4.00 |