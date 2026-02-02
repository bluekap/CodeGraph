"""
API router for repository analysis
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ErrorResponse
)
from app.analyzer.repository_analyzer import RepositoryAnalyzer

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest):
    """
    Analyze a GitHub repository and return dependency graph data
    
    Args:
        request: AnalyzeRequest containing repo_url and options
        
    Returns:
        AnalyzeResponse with nodes, edges, and metrics
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Validate URL
        if not request.repo_url.startswith(('https://github.com', 'http://github.com')):
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL. Must start with https://github.com"
            )
        
        # Create analyzer
        analyzer = RepositoryAnalyzer()
        
        # Perform analysis
        nodes, edges, metrics = await analyzer.analyze_repository(
            repo_url=request.repo_url,
            max_files=request.max_files or 100,
            include_tests=request.include_tests or False
        )
        
        # Extract repo name
        repo_name = request.repo_url.rstrip('/').rstrip('.git').split('/')[-1]
        
        return AnalyzeResponse(
            nodes=nodes,
            edges=edges,
            metrics=metrics,
            repo_name=repo_name,
            repo_url=request.repo_url
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/status")
async def get_status():
    """Get API status"""
    return {
        "status": "operational",
        "version": "0.1.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "status": "/api/status"
        }
    }
