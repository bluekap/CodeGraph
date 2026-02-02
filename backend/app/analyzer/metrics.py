"""
Code metrics analysis using Radon
"""
from pathlib import Path
from typing import Dict, Optional
from radon.complexity import cc_visit
from radon.raw import analyze


class MetricsAnalyzer:
    """Analyze code metrics for Python files"""
    
    def analyze_file(self, file_path: Path, content: str) -> Dict:
        """
        Analyze a Python file for various metrics
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            Dict containing metrics
        """
        metrics = {
            'path': str(file_path),
            'loc': 0,
            'sloc': 0,  # Source lines of code (excluding comments/blanks)
            'comments': 0,
            'blank': 0,
            'complexity': 0,
            'functions': 0,
            'classes': 0
        }
        
        try:
            # Get raw metrics (lines of code, comments, etc.)
            raw_metrics = analyze(content)
            metrics['loc'] = raw_metrics.loc
            metrics['sloc'] = raw_metrics.sloc
            metrics['comments'] = raw_metrics.comments
            metrics['blank'] = raw_metrics.blank
            
            # Get complexity metrics
            complexity_results = cc_visit(content)
            
            if complexity_results:
                # Calculate average complexity
                total_complexity = sum(item.complexity for item in complexity_results)
                metrics['complexity'] = total_complexity / len(complexity_results)
                
                # Count functions and classes
                for item in complexity_results:
                    # Radon items have a 'letter' attribute: C for Class, F for Function, M for Method
                    letter = getattr(item, 'letter', None)
                    if letter == 'C':
                        metrics['classes'] += 1
                    elif letter in ('F', 'M'):
                        metrics['functions'] += 1
            
        except Exception as e:
            import traceback
            print(f"Error analyzing {file_path}: {e}")
            traceback.print_exc()
        
        return metrics
    
    def calculate_complexity_color(self, complexity: float) -> str:
        """
        Get color code based on complexity score
        
        Args:
            complexity: Cyclomatic complexity value
            
        Returns:
            Color string for visualization
        """
        if complexity <= 5:
            return '#22c55e'  # Green - low complexity
        elif complexity <= 10:
            return '#84cc16'  # Light green
        elif complexity <= 15:
            return '#eab308'  # Yellow - moderate
        elif complexity <= 20:
            return '#f97316'  # Orange
        else:
            return '#ef4444'  # Red - high complexity
    
    def calculate_node_size(self, loc: int, min_size: int = 10, max_size: int = 50) -> int:
        """
        Calculate node size for visualization based on LOC
        
        Args:
            loc: Lines of code
            min_size: Minimum node size
            max_size: Maximum node size
            
        Returns:
            Node size value
        """
        # Logarithmic scaling for better visualization
        import math
        
        if loc <= 0:
            return min_size
        
        # Use log scale to prevent huge differences
        size = min_size + (math.log(loc + 1) * 5)
        
        return min(int(size), max_size)
    
    def get_file_language(self, file_path: Path) -> str:
        """
        Determine programming language from file extension
        
        Args:
            file_path: Path to file
            
        Returns:
            Language name
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        return extension_map.get(file_path.suffix, 'unknown')
    
    def calculate_repository_stats(self, all_metrics: list) -> Dict:
        """
        Calculate aggregate statistics for the repository
        
        Args:
            all_metrics: List of metrics dicts for all files
            
        Returns:
            Repository-level statistics
        """
        if not all_metrics:
            return {
                'total_files': 0,
                'total_loc': 0,
                'avg_complexity': 0,
                'max_complexity': 0,
                'total_functions': 0,
                'total_classes': 0
            }
        
        total_loc = sum(m['loc'] for m in all_metrics)
        complexities = [m['complexity'] for m in all_metrics if m['complexity'] > 0]
        
        return {
            'total_files': len(all_metrics),
            'total_loc': total_loc,
            'avg_complexity': sum(complexities) / len(complexities) if complexities else 0,
            'max_complexity': max(complexities) if complexities else 0,
            'total_functions': sum(m['functions'] for m in all_metrics),
            'total_classes': sum(m['classes'] for m in all_metrics)
        }
