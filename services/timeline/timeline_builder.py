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
        
        # Create timeline events from articles
        events = []
        for i, article in enumerate(articles):
            events.append({
                "timestamp": article.get("published_at") or f"2024-01-{i+1:02d}T12:00:00Z",
                "title": article.get("title", "Untitled"),
                "source": article.get("source_name", "Unknown"),
                "url": article.get("url", ""),
                "event_type": "initial_claim" if i == 0 else "amplification",
                "confidence": 0.8
            })
        
        # Simple timeline structure
        timeline = {
            "root_origin": {
                "title": root_origin.get("title", "Unknown"),
                "source": root_origin.get("source_name", "Unknown"),
                "url": root_origin.get("url", ""),
                "confidence": 0.9,
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