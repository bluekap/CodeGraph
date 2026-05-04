"""
Main repository analyzer orchestrating all analysis components
"""
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from codegraph.analyzer.git_handler import GitHandler
from codegraph.analyzer.dependency_parser import DependencyParser
from codegraph.analyzer.metrics import MetricsAnalyzer
from codegraph.models.schemas import NodeData, EdgeData, RepositoryMetrics


class RepositoryAnalyzer:
    """Main analyzer that orchestrates repository analysis"""
    
    def __init__(self):
        self.git_handler = GitHandler()
        self.dep_parser = DependencyParser()
        self.metrics_analyzer = MetricsAnalyzer()
    
    async def analyze_repository(
        self,
        repo_url: str,
        max_files: int = 100,
        include_tests: bool = False,
        file_pattern: str = "*"
    ) -> Tuple[List[NodeData], List[EdgeData], RepositoryMetrics]:
        """
        Analyze a GitHub repository and return graph data
        
        Args:
            repo_url: GitHub repository URL
            max_files: Maximum files to analyze
            include_tests: Include test files
            file_pattern: Glob pattern for files to analyze
            
        Returns:
            Tuple of (nodes, edges, metrics)
        """
        try:
            # Clone repository
            repo_path = self.git_handler.clone_repository(repo_url)
            
            source_suffixes = {'.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte'}
            source_files = self.git_handler.get_source_files(max_files, include_tests, file_pattern)
            source_files = [file for file in source_files if file.suffix.lower() in source_suffixes]
            
            if not source_files:
                raise ValueError("No supported source files found in repository")
            
            # Build module mapping
            module_map = self.dep_parser.build_module_map(source_files, repo_path)
            
            # Analyze each file
            nodes_data = []
            edges_list = []
            all_metrics = []
            language_counts = defaultdict(int)
            
            for source_file in source_files:
                # Read file content
                content = self.git_handler.get_file_content(source_file)
                if not content:
                    continue
                
                # Get relative path
                rel_path = self.git_handler.get_relative_path(source_file)
                
                # Analyze metrics
                metrics = self.metrics_analyzer.analyze_file(source_file, content)
                all_metrics.append(metrics)
                
                # Parse imports and symbols
                imports = self.dep_parser.parse_imports(source_file, content)
                symbols = self.dep_parser.parse_symbols(source_file, content)
                
                # Resolve local imports
                local_imports = self.dep_parser.resolve_local_imports(
                    rel_path, imports, module_map
                )
                
                # Get language
                language = self.metrics_analyzer.get_file_language(source_file)
                language_counts[language] += 1
                
                # Create node
                node = NodeData(
                    id=rel_path,
                    name=source_file.name,
                    path=rel_path,
                    loc=metrics['loc'],
                    complexity=round(metrics['complexity'], 2),
                    language=language,
                    imports=imports,
                    size=self.metrics_analyzer.calculate_node_size(metrics['loc']),
                    symbols=symbols,
                    function_details=metrics.get('function_details', [])
                )
                nodes_data.append(node)
                
                # Create edges for local imports
                for target in local_imports:
                    if target != rel_path:  # Avoid self-loops
                        edges_list.append((rel_path, target))
            
            # Remove duplicate edges
            unique_edges = list(set(edges_list))
            
            # Create edge objects
            edges_data = [
                EdgeData(source=source, target=target, weight=1)
                for source, target in unique_edges
            ]
            
            # Calculate coupling to find most connected files
            coupling = self.dep_parser.calculate_coupling(unique_edges)
            most_connected = sorted(
                coupling.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Calculate repository metrics
            repo_stats = self.metrics_analyzer.calculate_repository_stats(all_metrics)
            
            metrics = RepositoryMetrics(
                total_files=repo_stats['total_files'],
                total_loc=repo_stats['total_loc'],
                avg_complexity=round(repo_stats['avg_complexity'], 2),
                max_complexity=round(repo_stats['max_complexity'], 2),
                languages=dict(language_counts),
                most_connected=[file for file, _ in most_connected]
            )
            
            return nodes_data, edges_data, metrics
        
        finally:
            # Always cleanup
            self.git_handler.cleanup()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.git_handler.cleanup()
