"""
Python dependency parser using AST
"""
import ast
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict


class DependencyParser:
    """Parse Python imports and build dependency graph"""
    
    def __init__(self):
        self.file_imports: Dict[str, Set[str]] = defaultdict(set)
    
    def parse_imports(self, file_path: Path, content: str) -> List[str]:
        """
        Extract all imports from a Python file using AST
        
        Args:
            file_path: Path to the Python file
            content: File content as string
            
        Returns:
            List of imported module names
        """
        imports = set()
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Handle 'import module'
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                
                # Handle 'from module import something'
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return list(imports)
    
    def resolve_local_imports(
        self,
        file_path: str,
        imports: List[str],
        all_files: Dict[str, str]
    ) -> List[str]:
        """
        Resolve which imports are from local files vs external packages
        
        Args:
            file_path: Current file path
            imports: List of imported modules
            all_files: Dict mapping file paths to module names
            
        Returns:
            List of local file paths that are imported
        """
        local_imports = []
        
        # Get current file's directory
        current_dir = Path(file_path).parent
        
        for imp in imports:
            # Check if this import matches any local file
            for target_path, module_name in all_files.items():
                # Check if the module name matches
                if module_name == imp or module_name.endswith(f".{imp}"):
                    local_imports.append(target_path)
                # Check for relative imports
                elif imp in module_name:
                    local_imports.append(target_path)
        
        return local_imports
    
    def build_module_map(self, files: List[Path], repo_root: Path) -> Dict[str, str]:
        """
        Build a mapping of file paths to Python module names
        
        Args:
            files: List of Python files
            repo_root: Repository root directory
            
        Returns:
            Dict mapping file paths to module names
        """
        module_map = {}
        
        for file_path in files:
            try:
                # Get relative path from repo root
                rel_path = file_path.relative_to(repo_root)
                
                # Convert path to module name
                # e.g., src/app/main.py -> src.app.main
                module_name = str(rel_path.with_suffix('')).replace('/', '.')
                
                module_map[str(rel_path)] = module_name
            except ValueError:
                # File is outside repo root
                continue
        
        return module_map
    
    def calculate_coupling(self, edges: List[tuple]) -> Dict[str, int]:
        """
        Calculate coupling metrics (how many connections each file has)
        
        Args:
            edges: List of (source, target) tuples
            
        Returns:
            Dict mapping file paths to connection counts
        """
        coupling = defaultdict(int)
        
        for source, target in edges:
            coupling[source] += 1
            coupling[target] += 1
        
        return dict(coupling)
    
    def find_circular_dependencies(
        self,
        edges: List[tuple]
    ) -> List[List[str]]:
        """
        Detect circular dependencies in the graph
        
        Args:
            edges: List of (source, target) tuples
            
        Returns:
            List of circular dependency chains
        """
        # Build adjacency list
        graph = defaultdict(list)
        for source, target in edges:
            graph[source].append(target)
        
        cycles = []
        visited = set()
        path = []
        
        def dfs(node: str):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            
            path.pop()
        
        # Check all nodes
        for node in graph.keys():
            if node not in visited:
                dfs(node)
        
        return cycles
