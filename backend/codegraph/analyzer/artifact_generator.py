import os
from pathlib import Path
from typing import Dict, List, Any

class ArtifactGenerator:
    """Generates markdown artifacts from analysis data"""
    
    def __init__(self, codegraph_dir: str):
        self.output_dir = Path(codegraph_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_all(self, analysis_data: Dict[str, Any]):
        """Generate all artifacts based on the analysis data"""
        self.generate_architecture(analysis_data)
        self.generate_modules(analysis_data)
        self.generate_hotspots(analysis_data)
        
    def generate_architecture(self, data: Dict[str, Any]):
        """Generate architecture.md with Mermaid diagram"""
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        metrics = data.get("metrics", {})
        
        content = [
            "# Codebase Architecture Summary",
            "",
            "## Repository Stats",
            f"- **Total Files**: {metrics.get('total_files', 0)}",
            f"- **Total Lines of Code**: {metrics.get('total_loc', 0)}",
            f"- **Average Complexity**: {metrics.get('avg_complexity', 0):.2f}",
            "",
            "## Dependency Graph",
            "```mermaid",
            "graph TD;"
        ]
        
        # Add edges to Mermaid graph
        for edge in edges:
            source = edge.get("source", "").replace("/", "_").replace(".", "_")
            target = edge.get("target", "").replace("/", "_").replace(".", "_")
            source_label = edge.get("source", "").split("/")[-1]
            target_label = edge.get("target", "").split("/")[-1]
            
            if source and target:
                content.append(f'    {source}["{source_label}"] --> {target}["{target_label}"];')
                
        content.append("```")
        content.append("")
        
        with open(self.output_dir / "architecture.md", "w") as f:
            f.write("\n".join(content))
            
    def generate_modules(self, data: Dict[str, Any]):
        """Generate modules.md detailing classes and functions per file"""
        nodes = data.get("nodes", [])
        
        content = ["# Modules Breakdown\n"]
        
        for node in sorted(nodes, key=lambda x: x.get('path', '')):
            path = node.get('path', '')
            symbols = node.get('symbols', {})
            classes = symbols.get('classes', [])
            functions = symbols.get('functions', [])
            
            if not classes and not functions:
                continue
                
            content.append(f"## `{path}`")
            
            if classes:
                content.append("### Classes")
                for cls in classes:
                    name = cls.get('name')
                    doc = cls.get('docstring')
                    doc_fmt = f" - *{doc.split(chr(10))[0]}*" if doc else ""
                    content.append(f"- **{name}**{doc_fmt}")
                    for method in cls.get('methods', []):
                        m_name = method.get('name')
                        m_args = ", ".join(method.get('args', []))
                        content.append(f"  - `def {m_name}({m_args})`")
                        
            if functions:
                content.append("### Functions")
                for func in functions:
                    name = func.get('name')
                    args = ", ".join(func.get('args', []))
                    doc = func.get('docstring')
                    doc_fmt = f" - *{doc.split(chr(10))[0]}*" if doc else ""
                    content.append(f"- `def {name}({args})`{doc_fmt}")
                    
            content.append("")
            
        with open(self.output_dir / "modules.md", "w") as f:
            f.write("\n".join(content))
            
    def generate_hotspots(self, data: Dict[str, Any]):
        """Generate hotspots.md highlighting highly complex files and functions"""
        nodes = data.get("nodes", [])
        
        content = [
            "# Complexity Hotspots",
            "",
            "This document lists the most complex files and functions in the repository.",
            "High complexity usually indicates areas that are difficult to maintain and could benefit from refactoring.",
            "",
            "## Complex Files (Top 10)",
            "| File | Complexity |",
            "|------|------------|"
        ]
        
        # Sort files by complexity
        sorted_files = sorted(nodes, key=lambda x: x.get('complexity', 0), reverse=True)
        for node in sorted_files[:10]:
            if node.get('complexity', 0) > 0:
                content.append(f"| `{node.get('path')}` | {node.get('complexity'):.2f} |")
                
        content.extend([
            "",
            "## Complex Functions & Methods (Top 20)",
            "| Function/Method | File | Complexity |",
            "|-----------------|------|------------|"
        ])
        
        # Aggregate all functions
        all_functions = []
        for node in nodes:
            path = node.get('path', '')
            func_details = node.get('function_details', [])
            for func in func_details:
                all_functions.append({
                    'name': func.get('name'),
                    'path': path,
                    'type': func.get('type'),
                    'complexity': func.get('complexity', 0)
                })
                
        sorted_funcs = sorted(all_functions, key=lambda x: x.get('complexity', 0), reverse=True)
        for func in sorted_funcs[:20]:
            if func.get('complexity', 0) > 0:
                prefix = "cls:" if func.get('type') == 'class' else "func:"
                content.append(f"| `{prefix}{func.get('name')}` | `{func.get('path')}` | {func.get('complexity'):.2f} |")
                
        with open(self.output_dir / "hotspots.md", "w") as f:
            f.write("\n".join(content))
