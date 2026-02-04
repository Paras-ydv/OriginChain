"""
JSON Schema validation for News Ingestion Service.
Defines Pydantic models matching the articles.json contract.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class Article(BaseModel):
    """Individual article schema."""
    article_id: str = Field(..., description="Unique identifier for the article")
    title: str = Field(..., description="Article title")
    source_name: str = Field(..., description="Publisher/source name")
    url: str = Field(..., description="Article URL")
    published_at: str = Field(..., description="Publication timestamp in ISO format")
    author: Optional[str] = Field(None, description="Article author, null if unavailable")
    language: str = Field(default="en", description="Article language code")
    clean_text: str = Field(..., description="Cleaned article content")
    raw_text: Optional[str] = Field(None, description="Raw HTML/original text")

    @validator('published_at')
    def validate_iso_time(cls, v):
        """Ensure published_at is valid ISO 8601 format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid ISO timestamp: {v}")
        return v

    @validator('language')
    def validate_language(cls, v):
        """Ensure language is a valid code."""
        if not v or len(v) < 2:
            return "en"
        return v.lower()


class ArticlesOutput(BaseModel):
    """Complete output schema for articles.json."""
    case_id: str = Field(..., description="Unique case identifier")
    query: str = Field(..., description="Search query used")
    generated_at: str = Field(..., description="Generation timestamp in ISO format")
    articles: List[Article] = Field(default_factory=list, description="List of articles")

    @validator('generated_at')
    def validate_iso_time(cls, v):
        """Ensure generated_at is valid ISO 8601 format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid ISO timestamp: {v}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case_001",
                "query": "climate change",
                "generated_at": "2026-02-03T10:04:05Z",
                "articles": [
                    {
                        "article_id": "art_001",
                        "title": "Climate Change Impact on Agriculture",
                        "source_name": "BBC News",
                        "url": "https://example.com/article",
                        "published_at": "2026-02-01T12:00:00Z",
                        "author": "John Doe",
                        "language": "en",
                        "clean_text": "Article content here...",
                        "raw_text": "<html>...</html>"
                    }
                ]
            }
        }
