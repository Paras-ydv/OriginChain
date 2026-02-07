"""
FastAPI Backend for OriginChain
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'services', 'ingestion'))
sys.path.insert(0, os.path.join(root_dir, 'graphs'))

from services.ingestion.ingestor import ingest_news
from services.timeline.timeline_builder import TimelineBuilder
from services.impact.impact_engine import ImpactEngine

def generate_relationships(timeline_data):
    """Generate relationships between articles based on timeline"""
    events = timeline_data.get('events', [])
    root = timeline_data.get('root_origin', {})
    
    relationships = []
    
    # Connect root to first few events
    if root and len(events) > 0:
        for i in range(min(3, len(events))):
            relationships.append({
                'source_article_id': 'root_origin',
                'target_article_id': f'art_{i:04d}',
                'relationship_type': 'AMPLIFIES',
                'justification': 'Initial event amplification'
            })
    
    # Connect sequential events
    for i in range(len(events) - 1):
        rel_type = 'AMPLIFIES' if events[i]['event_type'] == events[i+1]['event_type'] else 'CONSEQUENCE_OF'
        relationships.append({
            'source_article_id': f'art_{i:04d}',
            'target_article_id': f'art_{i+1:04d}',
            'relationship_type': rel_type,
            'justification': 'Sequential event connection'
        })
    
    # Add cross-connections for similar event types
    event_type_groups = {}
    for i, event in enumerate(events):
        et = event['event_type']
        if et not in event_type_groups:
            event_type_groups[et] = []
        event_type_groups[et].append(i)
    
    for et, indices in event_type_groups.items():
        if len(indices) > 1:
            for i in range(len(indices) - 1):
                if indices[i+1] - indices[i] > 1:
                    relationships.append({
                        'source_article_id': f'art_{indices[i]:04d}',
                        'target_article_id': f'art_{indices[i+1]:04d}',
                        'relationship_type': 'AMPLIFIES',
                        'justification': f'Similar {et} events'
                    })
    
    return {'relationships': relationships}

app = FastAPI(title="OriginChain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    query: str
    target_entity: str
    max_articles: int = 20

@app.post("/api/analyze")
async def analyze_news(request: AnalysisRequest):
    try:
        outputs_dir = os.path.join(root_dir, "outputs")
        
        result = ingest_news(
            request.query, 
            request.max_articles, 
            output_path=os.path.join(outputs_dir, "articles.json")
        )
        
        timeline_builder = TimelineBuilder()
        timeline_path = timeline_builder.build_timeline(
            os.path.join(outputs_dir, "articles.json")
        )
        
        impact_engine = ImpactEngine()
        impact_path = impact_engine.analyze_impact(timeline_path, request.target_entity)
        
        # Generate relationships
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline_data = json.load(f)
        relationships = generate_relationships(timeline_data)
        
        # Save relationships to file
        rel_path = os.path.join(outputs_dir, "relationships.json")
        with open(rel_path, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2)
        
        # Generate case ID for sharing
        import hashlib
        case_id = hashlib.md5(f"{request.query}_{request.target_entity}".encode()).hexdigest()[:12]
        
        print(f"Generated {len(relationships.get('relationships', []))} relationships")
        print(f"Case ID: {case_id}")
        
        with open(os.path.join(outputs_dir, "articles.json"), 'r', encoding='utf-8') as f:
            articles = json.load(f)
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline = json.load(f)
        with open(impact_path, 'r', encoding='utf-8') as f:
            impact = json.load(f)
        
        # Save complete analysis for sharing
        analysis_data = {
            "case_id": case_id,
            "query": request.query,
            "target_entity": request.target_entity,
            "articles": articles,
            "timeline": timeline,
            "impact": impact,
            "relationships": relationships,
            "generated_at": timeline.get("generated_at")
        }
        
        case_path = os.path.join(outputs_dir, f"case_{case_id}.json")
        with open(case_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)
        
        return {
            "success": True,
            "case_id": case_id,
            "articles": articles,
            "timeline": timeline,
            "impact": impact,
            "relationships": relationships
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/case/{case_id}")
async def get_case(case_id: str):
    """Get shared analysis by case ID"""
    try:
        case_path = os.path.join(root_dir, "outputs", f"case_{case_id}.json")
        if not os.path.exists(case_path):
            raise HTTPException(status_code=404, detail="Case not found")
        
        with open(case_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/{case_id}")
async def export_pdf(case_id: str):
    """Export analysis as PDF"""
    from fastapi.responses import FileResponse
    try:
        case_path = os.path.join(root_dir, "outputs", f"case_{case_id}.json")
        if not os.path.exists(case_path):
            raise HTTPException(status_code=404, detail="Case not found")
        
        with open(case_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generate simple text report (PDF generation requires reportlab)
        report_path = os.path.join(root_dir, "outputs", f"report_{case_id}.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"OriginChain Analysis Report\n")
            f.write(f"="*50 + "\n\n")
            f.write(f"Query: {data['query']}\n")
            f.write(f"Target Entity: {data['target_entity']}\n")
            f.write(f"Generated: {data['generated_at']}\n\n")
            
            f.write(f"Root Origin:\n")
            f.write(f"  Title: {data['timeline']['root_origin']['title']}\n")
            f.write(f"  Source: {data['timeline']['root_origin']['source']}\n")
            f.write(f"  Credibility: {data['timeline']['root_origin'].get('credibility', 0)*100:.0f}%\n\n")
            
            f.write(f"Impact Analysis:\n")
            f.write(f"  Overall Polarity: {data['impact']['overall_polarity'].upper()}\n")
            f.write(f"  Confidence: {data['impact']['confidence_score']*100:.0f}%\n")
            f.write(f"  Relevant Events: {data['impact']['direct_impact']['relevant_events_count']}\n\n")
            
            f.write(f"Timeline Events: {len(data['timeline']['events'])}\n")
            f.write(f"Network Connections: {len(data['relationships']['relationships'])}\n")
        
        return FileResponse(report_path, filename=f"originchain_report_{case_id}.txt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
