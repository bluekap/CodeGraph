"""
Python dependency parser using AST
"""
import ast
import re
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict


class DependencyParser:
    """Parse Python imports and build dependency graph"""

    SOURCE_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte'}
    
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
        suffix = file_path.suffix.lower()

        if suffix in {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}:
            imports.update(self.JS_IMPORT_RE.findall(content))
            imports.update(self.JS_REQUIRE_RE.findall(content))
            return list(imports)
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Handle 'import module'
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                
                # Handle 'from module import something'
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return list(imports)
    
    def parse_symbols(self, file_path: Path, content: str) -> Dict[str, List[Dict]]:
        """
        Extract classes and functions with their docstrings and signatures.
        
        Args:
            file_path: Path to the Python file
            content: File content as string
            
        Returns:
            Dict containing lists of 'classes' and 'functions'
        """
        symbols = {'classes': [], 'functions': []}
        suffix = file_path.suffix.lower()

        if suffix in {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}:
            for class_match in self.JS_CLASS_RE.finditer(content):
                class_name = class_match.group(1) or class_match.group(2)
                if class_name:
                    symbols['classes'].append({
                        'name': class_name,
                        'docstring': "",
                        'methods': []
                    })
            for fn_name in self.JS_EXPORT_RE.findall(content):
                symbols['functions'].append({
                    'name': fn_name,
                    'docstring': "",
                    'args': []
                })
            for fn_name in self.JS_FUNCTION_RE.findall(content):
                symbols['functions'].append({
                    'name': fn_name,
                    'docstring': "",
                    'args': []
                })
            return symbols
        
        try:
            tree = ast.parse(content)
            
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.append({
                                'name': child.name,
                                'docstring': ast.get_docstring(child) or "",
                                'args': [arg.arg for arg in child.args.args]
                            })
                    
                    symbols['classes'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "",
                        'methods': methods
                    })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols['functions'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "",
                        'args': [arg.arg for arg in node.args.args]
                    })
        
        except SyntaxError:
            pass
        except Exception as e:
            print(f"Error parsing symbols {file_path}: {e}")
            
        return symbols
    
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
        current_dir = Path(file_path).parent
        file_path_index = set(all_files.keys())
        module_to_path = {module_name: rel_path for rel_path, module_name in all_files.items()}
        
        for imp in imports:
            # Resolve JS/TS-style relative imports: ./foo, ../bar/baz
            if imp.startswith(("./", "../")):
                normalized = self._resolve_relative_import(current_dir, imp, file_path_index)
                if normalized:
                    local_imports.append(normalized)
                continue

            # Python/module-style match
            if imp in module_to_path:
                local_imports.append(module_to_path[imp])
                continue

            # Conservative fallback for module names such as package.submodule.
            # We intentionally avoid broad substring matching to reduce false edges.
            for target_path, module_name in all_files.items():
                if module_name.endswith(f".{imp}"):
                    local_imports.append(target_path)
        
        # Preserve order while removing duplicates
        return list(dict.fromkeys(local_imports))

    def _resolve_relative_import(self, current_dir: Path, import_path: str, file_path_index: Set[str]) -> str:
        """Resolve relative import to a known repository file path."""
        base_path = (current_dir / import_path).as_posix()
        path_obj = Path(base_path)

        candidates = []
        if path_obj.suffix:
            candidates.append(path_obj.as_posix())
        else:
            for suffix in self.SOURCE_SUFFIXES:
                candidates.append(path_obj.with_suffix(suffix).as_posix())
            for suffix in self.SOURCE_SUFFIXES:
                candidates.append((path_obj / f"index{suffix}").as_posix())

        for candidate in candidates:
            normalized = str(Path(candidate))
            if normalized in file_path_index:
                return normalized

        return ""
    
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
    JS_IMPORT_RE = re.compile(r'^\s*import\s+(?:.+?\s+from\s+)?[\'"]([^\'"]+)[\'"]', re.MULTILINE)
    JS_REQUIRE_RE = re.compile(r'require\(\s*[\'"]([^\'"]+)[\'"]\s*\)')
    JS_EXPORT_RE = re.compile(r'^\s*export\s+(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)', re.MULTILINE)
    JS_CLASS_RE = re.compile(r'^\s*export\s+(?:default\s+)?class\s+([A-Za-z_]\w*)|^\s*class\s+([A-Za-z_]\w*)', re.MULTILINE)
    JS_FUNCTION_RE = re.compile(r'^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\(', re.MULTILINE)
