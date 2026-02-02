"""
Pydantic models for request/response validation
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    """Request model for repository analysis"""
    repo_url: str = Field(..., description="GitHub repository URL")
    max_files: Optional[int] = Field(100, description="Maximum files to analyze")
    include_tests: Optional[bool] = Field(False, description="Include test files")


class NodeData(BaseModel):
    """Graph node representing a file/module"""
    id: str = Field(..., description="Unique identifier (file path)")
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Full file path")
    loc: int = Field(..., description="Lines of code")
    complexity: float = Field(..., description="Cyclomatic complexity")
    language: str = Field(..., description="Programming language")
    imports: List[str] = Field(default_factory=list, description="List of imported modules")
    size: int = Field(..., description="Node size for visualization")


class EdgeData(BaseModel):
    """Graph edge representing a dependency"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    weight: int = Field(1, description="Dependency strength")


class RepositoryMetrics(BaseModel):
    """Overall repository metrics"""
    total_files: int
    total_loc: int
    avg_complexity: float
    max_complexity: float
    languages: Dict[str, int]
    most_connected: List[str]


class AnalyzeResponse(BaseModel):
    """Response model with graph data"""
    nodes: List[NodeData]
    edges: List[EdgeData]
    metrics: RepositoryMetrics
    repo_name: str
    repo_url: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
