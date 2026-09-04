"""
FastAPI REST API for LangGraph Blog Generator

Endpoints:
- POST /api/generate-blog - Generate blog post from topic
- GET /health - Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from src.graph import build_graph
from src.state import BlogState

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Blog Generator API",
    description="AI-powered blog post generator using LangGraph and Groq",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Models
class BlogGenerationRequest(BaseModel):
    """Request model for blog generation"""
    topic: str = Field(..., min_length=5, max_length=200, description="Blog topic title")
    category: str = Field(default="troubleshooting", description="Blog category")
    keywords: List[str] = Field(..., min_items=1, max_items=10, description="Target keywords")
    target_audience: str = Field(default="homeowners", description="Target audience")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Why Circuit Breakers Trip",
                "category": "troubleshooting",
                "keywords": ["circuit breaker", "electrical", "safety"],
                "target_audience": "homeowners"
            }
        }


# Response Models
class BlogGenerationResponse(BaseModel):
    """Response model for generated blog"""
    success: bool = Field(..., description="Whether generation succeeded")
    title: str = Field(..., description="SEO-optimized blog title")
    content: str = Field(..., description="Full markdown blog content")
    meta_description: str = Field(..., description="Meta description for SEO")
    category: str = Field(..., description="Blog category")
    keywords: List[str] = Field(..., description="Target keywords")
    outline: str = Field(..., description="Blog outline used for generation")
    word_count: int = Field(..., description="Total word count")
    revisions: int = Field(..., description="Number of revisions made")
    review_status: str = Field(..., description="Final review status")
    review_feedback: Optional[str] = Field(None, description="Reviewer feedback")
    generated_at: str = Field(..., description="Generation timestamp (ISO 8601)")
    target_audience: str = Field(..., description="Target audience")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "title": "Why Circuit Breakers Trip: 7 Common Causes",
                "content": "# Why Circuit Breakers Trip...",
                "meta_description": "Learn the 7 common reasons...",
                "category": "troubleshooting",
                "keywords": ["circuit breaker", "electrical"],
                "outline": "## Introduction\n## Common Causes...",
                "word_count": 1523,
                "revisions": 1,
                "review_status": "APPROVED",
                "review_feedback": "Excellent quality, ready to publish",
                "generated_at": "2026-09-04T10:35:11.480100",
                "target_audience": "homeowners"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None


# Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "blog-generator-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/generate-blog", response_model=BlogGenerationResponse)
def generate_blog(request: BlogGenerationRequest):
    """
    Generate AI blog post from topic

    - **topic**: Blog topic/title (5-200 chars)
    - **category**: Blog category (default: troubleshooting)
    - **keywords**: List of target keywords (1-10)
    - **target_audience**: Target audience (default: homeowners)

    Returns complete blog with title, content, metadata
    """
    try:
        # Validate API key
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY not configured"
            )

        # Build LangGraph workflow
        graph = build_graph()

        # Prepare initial state
        initial_state = BlogState(
            topic_title=request.topic,
            category=request.category,
            keywords=request.keywords,
            target_audience=request.target_audience,
            outline=None,
            draft_title=None,
            draft_content=None,
            draft_meta=None,
            review_approved=False,
            review_feedback=None,
            revision_count=0,
            final_title=None,
            final_content=None,
            final_meta=None,
            final_keywords=None
        )

        # Execute workflow
        result = graph.invoke(initial_state)

        # Calculate word count
        word_count = len(result["final_content"].split())

        # Determine review status
        review_status = "APPROVED" if result["review_approved"] else "ACCEPTED (max revisions)"

        # Build response
        response = BlogGenerationResponse(
            success=True,
            title=result["final_title"],
            content=result["final_content"],
            meta_description=result["final_meta"],
            category=result["category"],
            keywords=result["final_keywords"],
            outline=result["outline"],
            word_count=word_count,
            revisions=result["revision_count"],
            review_status=review_status,
            review_feedback=result.get("review_feedback"),
            generated_at=datetime.utcnow().isoformat(),
            target_audience=result["target_audience"]
        )

        return response

    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error generating blog: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Blog generation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
