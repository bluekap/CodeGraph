import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class ArtifactGenerator:
    """Generates markdown artifacts from analysis data"""
    MAX_FILE_LEVEL_EDGES = 80
    MAX_HIGH_LEVEL_EDGES = 40
    MAX_LAYERED_EDGES = 24
    MAX_ENTRYPOINTS = 6
    MAX_CONNECTED = 6
    MAX_CACHE_FILES = 12
    MAX_SYMBOLS_PER_FILE = 10
    
    def __init__(self, codegraph_dir: str):
        self.output_dir = Path(codegraph_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_all(self, analysis_data: Dict[str, Any]):
        """Generate all artifacts based on the analysis data"""
        self.generate_architecture_overview(analysis_data)
        self.generate_architecture_high_level(analysis_data)
        self.generate_architecture_layered(analysis_data)
        self.generate_architecture_file_level(analysis_data)
        self.generate_modules(analysis_data)
        self.generate_hotspots(analysis_data)
        self.generate_context(analysis_data)
        
    def generate_architecture_overview(self, data: Dict[str, Any]):
        """Generate architecture.md with reading guidance."""
        metrics = data.get("metrics", {})
        edges = data.get("edges", [])
        content = [
            "# Architecture Index",
            f"- Files: {metrics.get('total_files', 0)} | LOC: {metrics.get('total_loc', 0)} | Avg Cpx: {metrics.get('avg_complexity', 0):.2f} | Edges: {len(edges)}",
            "- Read order:",
            "1. Start with `architecture-high-level.md` to understand layers and folder boundaries.",
            "2. Read `architecture-layered.md` for app-layer flow (`ui`, `api`, `domain`, `infra`).",
            "3. Drill down into `architecture-file-level.md` for concrete file-to-file dependencies.",
            "4. Use `modules.md` and `hotspots.md` only when needed."
        ]
        with open(self.output_dir / "architecture.md", "w") as f:
            f.write("\n".join(content))

    def generate_architecture_file_level(self, data: Dict[str, Any]):
        """Generate architecture-file-level.md with detailed Mermaid graph."""
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        metrics = data.get("metrics", {})
        
        content = [
            "# File-Level Architecture",
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
        for edge in edges[:self.MAX_FILE_LEVEL_EDGES]:
            source = edge.get("source", "").replace("/", "_").replace(".", "_")
            target = edge.get("target", "").replace("/", "_").replace(".", "_")
            source_label = edge.get("source", "").split("/")[-1]
            target_label = edge.get("target", "").split("/")[-1]
            
            if source and target:
                content.append(f'    {source}["{source_label}"] --> {target}["{target_label}"];')
                
        content.append("```")
        content.append("")
        
        with open(self.output_dir / "architecture-file-level.md", "w") as f:
            f.write("\n".join(content))

    def generate_architecture_high_level(self, data: Dict[str, Any]):
        """Generate architecture-high-level.md with folder/layer Mermaid graph."""
        edges = data.get("edges", [])
        layer_edges = defaultdict(int)

        for edge in edges:
            source_layer = self._path_to_layer(edge.get("source", ""))
            target_layer = self._path_to_layer(edge.get("target", ""))
            if source_layer and target_layer and source_layer != target_layer:
                layer_edges[(source_layer, target_layer)] += 1

        content = [
            "# High-Level Architecture",
            "## Layer Dependency Graph",
            "```mermaid",
            "graph TD;"
        ]

        if layer_edges:
            sorted_edges = sorted(layer_edges.items(), key=lambda item: item[1], reverse=True)[:self.MAX_HIGH_LEVEL_EDGES]
            for (source, target), weight in sorted_edges:
                source_id = source.replace("/", "_").replace(".", "_")
                target_id = target.replace("/", "_").replace(".", "_")
                content.append(
                    f'    {source_id}["{source}"] -->|{weight}| {target_id}["{target}"];'
                )
        else:
            content.append('    repo["repo"] --> repo["repo"];')

        content.extend(["```", ""])

        with open(self.output_dir / "architecture-high-level.md", "w") as f:
            f.write("\n".join(content))

    def generate_architecture_layered(self, data: Dict[str, Any]):
        """Generate architecture-layered.md grouped by app-layer heuristics."""
        edges = data.get("edges", [])
        layer_edges = defaultdict(int)

        for edge in edges:
            source_layer = self._path_to_app_layer(edge.get("source", ""))
            target_layer = self._path_to_app_layer(edge.get("target", ""))
            if source_layer != target_layer:
                layer_edges[(source_layer, target_layer)] += 1

        content = [
            "# Layered Architecture",
            "## Layer Dependency Graph",
            "```mermaid",
            "graph TD;"
        ]

        if layer_edges:
            sorted_edges = sorted(layer_edges.items(), key=lambda item: item[1], reverse=True)[:self.MAX_LAYERED_EDGES]
            for (source, target), weight in sorted_edges:
                content.append(f'    {source}["{source}"] -->|{weight}| {target}["{target}"];')
        else:
            content.append('    unknown["unknown"] --> unknown["unknown"];')

        content.extend(["```"])

        with open(self.output_dir / "architecture-layered.md", "w") as f:
            f.write("\n".join(content))

    def _path_to_layer(self, path: str) -> str:
        """Convert a file path to a folder/layer label."""
        parts = [part for part in Path(path).parts if part]
        if not parts:
            return "root"
        # Group by containing directory, not file name.
        parent_parts = parts[:-1]
        if not parent_parts:
            return "root"
        # Keep first 3 parent segments for useful layering in monorepos.
        return "/".join(parent_parts[:3])

    def _path_to_app_layer(self, path: str) -> str:
        """Map file path to app layer using pragmatic heuristics."""
        lowered = path.lower()
        tokens = set(part for part in Path(lowered).parts if part)

        def has_any(candidates: List[str]) -> bool:
            return any(candidate in lowered or candidate in tokens for candidate in candidates)

        if has_any(["ui", "frontend", "web", "components", "pages", "views", "screens"]):
            return "ui"
        if has_any(["api", "routes", "controllers", "handlers", "endpoints"]):
            return "api"
        if has_any(["domain", "core", "models", "entities", "business", "services"]):
            return "domain"
        if has_any(["infra", "infrastructure", "db", "database", "repository", "repositories", "adapters", "clients", "gateway"]):
            return "infra"
        if has_any(["shared", "common", "utils", "helpers", "lib"]):
            return "shared"
        if has_any(["test", "tests", "spec"]):
            return "tests"
        if has_any(["config", "settings", "env"]):
            return "config"
        return "unknown"
            
    def generate_modules(self, data: Dict[str, Any]):
        """Generate a compact modules.md as an agent-facing symbol cache."""
        nodes = data.get("nodes", [])
        metrics = data.get("metrics", {})
        most_connected = set(metrics.get("most_connected", []))

        entrypoint_keywords = ("main", "app", "server", "index", "routes", "api")
        cache_candidates = []
        for node in nodes:
            path = node.get("path", "")
            symbols = node.get("symbols", {})
            classes = symbols.get("classes", [])
            functions = symbols.get("functions", [])
            if not classes and not functions:
                continue

            lowered = path.lower()
            entrypoint_bonus = 2 if any(keyword in lowered for keyword in entrypoint_keywords) else 0
            connected_bonus = 3 if path in most_connected else 0
            symbol_count = len(classes) + len(functions)
            score = connected_bonus + entrypoint_bonus + min(symbol_count, 5)
            cache_candidates.append((score, path, node))

        selected = [item[2] for item in sorted(cache_candidates, key=lambda x: (-x[0], x[1]))[:self.MAX_CACHE_FILES]]

        content = [
            "# Modules Cache",
            f"- Scope: top {len(selected)} high-value files (entrypoints + connected modules).",
            f"- Cap: {self.MAX_SYMBOLS_PER_FILE} symbols per file.",
            "",
        ]

        for node in selected:
            path = node.get("path", "")
            symbols = node.get("symbols", {})
            classes = symbols.get("classes", [])
            functions = symbols.get("functions", [])

            content.append(f"## `{path}`")

            emitted = 0
            for cls in classes:
                if emitted >= self.MAX_SYMBOLS_PER_FILE:
                    break
                content.append(f"- class `{cls.get('name', 'Unknown')}`")
                emitted += 1
                for method in cls.get("methods", []):
                    if emitted >= self.MAX_SYMBOLS_PER_FILE:
                        break
                    m_name = method.get("name", "unknown")
                    m_args = ", ".join(method.get("args", []))
                    content.append(f"  - `{m_name}({m_args})`")
                    emitted += 1

            for func in functions:
                if emitted >= self.MAX_SYMBOLS_PER_FILE:
                    break
                name = func.get("name", "unknown")
                args = ", ".join(func.get("args", []))
                content.append(f"- fn `{name}({args})`")
                emitted += 1

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

    def generate_context(self, data: Dict[str, Any]):
        """Generate context.md to help AI agents onboard quickly."""
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        metrics = data.get("metrics", {})

        most_connected = metrics.get("most_connected", [])
        languages = metrics.get("languages", {})

        # Pick likely entrypoints and runtime-critical files.
        entrypoint_keywords = ("main", "app", "server", "index", "routes", "api")
        likely_entrypoints = []
        for node in nodes:
            path = node.get("path", "")
            lowered = path.lower()
            if any(keyword in lowered for keyword in entrypoint_keywords):
                likely_entrypoints.append(path)
        likely_entrypoints = sorted(set(likely_entrypoints))[:self.MAX_ENTRYPOINTS]

        content = [
            "# Agent Context",
            "## Snapshot",
            f"- Total files analyzed: {metrics.get('total_files', 0)}",
            f"- Total LOC: {metrics.get('total_loc', 0)}",
            f"- Average complexity: {metrics.get('avg_complexity', 0):.2f}",
            f"- Dependency edges: {len(edges)}",
            "",
            "## Languages",
        ]

        if languages:
            for language, count in sorted(languages.items(), key=lambda item: item[1], reverse=True):
                content.append(f"- {language}: {count}")
        else:
            content.append("- None detected")

        content.extend([
            "",
            "## Likely Entrypoints",
        ])
        if likely_entrypoints:
            for path in likely_entrypoints:
                content.append(f"- `{path}`")
        else:
            content.append("- Could not infer entrypoints from file names")

        content.extend([
            "",
            "## Most Connected Files",
        ])
        if most_connected:
            for path in most_connected[:self.MAX_CONNECTED]:
                content.append(f"- `{path}`")
        else:
            content.append("- No connected files detected")

        with open(self.output_dir / "context.md", "w") as f:
            f.write("\n".join(content))
