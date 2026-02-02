"""
Main repository analyzer orchestrating all analysis components
"""
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from app.analyzer.git_handler import GitHandler
from app.analyzer.dependency_parser import DependencyParser
from app.analyzer.metrics import MetricsAnalyzer
from app.models.schemas import NodeData, EdgeData, RepositoryMetrics


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
        include_tests: bool = False
    ) -> Tuple[List[NodeData], List[EdgeData], RepositoryMetrics]:
        """
        Analyze a GitHub repository and return graph data
        
        Args:
            repo_url: GitHub repository URL
            max_files: Maximum files to analyze
            include_tests: Include test files
            
        Returns:
            Tuple of (nodes, edges, metrics)
        """
        try:
            # Clone repository
            repo_path = self.git_handler.clone_repository(repo_url)
            
            # Get Python files
            python_files = self.git_handler.get_python_files(max_files, include_tests)
            
            if not python_files:
                raise ValueError("No Python files found in repository")
            
            # Build module mapping
            module_map = self.dep_parser.build_module_map(python_files, repo_path)
            
            # Analyze each file
            nodes_data = []
            edges_list = []
            all_metrics = []
            language_counts = defaultdict(int)
            
            for py_file in python_files:
                # Read file content
                content = self.git_handler.get_file_content(py_file)
                if not content:
                    continue
                
                # Get relative path
                rel_path = self.git_handler.get_relative_path(py_file)
                
                # Analyze metrics
                metrics = self.metrics_analyzer.analyze_file(py_file, content)
                all_metrics.append(metrics)
                
                # Parse imports
                imports = self.dep_parser.parse_imports(py_file, content)
                
                # Resolve local imports
                local_imports = self.dep_parser.resolve_local_imports(
                    rel_path, imports, module_map
                )
                
                # Get language
                language = self.metrics_analyzer.get_file_language(py_file)
                language_counts[language] += 1
                
                # Create node
                node = NodeData(
                    id=rel_path,
                    name=py_file.name,
                    path=rel_path,
                    loc=metrics['loc'],
                    complexity=round(metrics['complexity'], 2),
                    language=language,
                    imports=imports,
                    size=self.metrics_analyzer.calculate_node_size(metrics['loc'])
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
