"""
Timeline Builder Service - Minimal Implementation
"""

import json
import os
from typing import List, Dict
from datetime import datetime

class TimelineBuilder:
    def build_timeline(self, articles_path: str) -> str:
        """Build timeline from articles"""
        with open(articles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data.get('articles', [])
        
        # Find root origin (earliest or most credible)
        root_origin = articles[0] if articles else {}
        
        # Calculate credibility based on source
        def get_credibility(source):
            trusted = ['Reuters', 'AP', 'Bloomberg', 'WSJ', 'BBC', 'CNN', 'The Guardian', 'NYT', 'Washington Post']
            if any(t.lower() in source.lower() for t in trusted):
                return 0.95
            if '.gov' in source.lower() or 'official' in source.lower():
                return 0.9
            if 'news' in source.lower():
                return 0.7
            return 0.6
        
        # Create timeline events from articles
        events = []
        for i, article in enumerate(articles):
            # Calculate confidence based on source credibility and content quality
            confidence = 0.5  # base
            if article.get("author"):
                confidence += 0.15
            if article.get("clean_text") and len(article.get("clean_text", "")) > 500:
                confidence += 0.2
            if article.get("published_at"):
                confidence += 0.15
            confidence = min(confidence, 1.0)
            
            # Calculate credibility based on source
            credibility = get_credibility(article.get("source_name", ""))
            
            events.append({
                "timestamp": article.get("published_at") or f"2024-01-{i+1:02d}T12:00:00Z",
                "title": article.get("title", "Untitled"),
                "source": article.get("source_name", "Unknown"),
                "url": article.get("url", ""),
                "summary": article.get("clean_text", "")[:300] + "..." if article.get("clean_text") else "No summary available",
                "event_type": "initial_claim" if i == 0 else "amplification",
                "confidence": round(confidence, 2),
                "credibility": round(credibility, 2)
            })
        
        # Calculate root confidence
        root_confidence = 0.6
        if root_origin.get("author"):
            root_confidence += 0.15
        if root_origin.get("clean_text") and len(root_origin.get("clean_text", "")) > 500:
            root_confidence += 0.15
        if root_origin.get("published_at"):
            root_confidence += 0.1
        root_confidence = min(root_confidence, 1.0)
        
        # Calculate credibility score
        def get_credibility(source):
            trusted = ['Reuters', 'AP', 'Bloomberg', 'WSJ', 'BBC', 'CNN', 'The Guardian', 'NYT', 'Washington Post']
            if any(t.lower() in source.lower() for t in trusted):
                return 0.95
            if '.gov' in source.lower() or 'official' in source.lower():
                return 0.9
            if 'news' in source.lower():
                return 0.7
            return 0.6
        
        root_credibility = get_credibility(root_origin.get("source_name", ""))
        
        # Simple timeline structure
        timeline = {
            "root_origin": {
                "title": root_origin.get("title", "Unknown"),
                "source": root_origin.get("source_name", "Unknown"),
                "url": root_origin.get("url", ""),
                "confidence": round(root_confidence, 2),
                "credibility": round(root_credibility, 2),
                "why_root": "Earliest credible source identified"
            },
            "events": sorted(events, key=lambda x: x["timestamp"]),
            "contradictions": [],
            "generated_at": datetime.now().isoformat()
        }
        
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs", "timeline.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2)
        
        return output_path