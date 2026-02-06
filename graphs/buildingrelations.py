import json
import os
import google.generativeai as genai

# Read API key from .env.example
with open(".env.example", "r") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]
            break

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def load_timeline():
    with open("outputs/timeline.json", "r", encoding="utf-8") as f:
        return json.load(f)

def generate_relationships(timeline_data):
    events = timeline_data.get('events', [])
    root = timeline_data.get('root_origin', {})
    
    # Create article list with IDs
    articles = []
    for i, event in enumerate(events):
        articles.append({
            'id': f'art_{i:04d}',
            'title': event['title'],
            'timestamp': event['timestamp'],
            'source': event['source'],
            'event_type': event['event_type']
        })
    
    if root:
        articles.append({
            'id': 'root_origin',
            'title': root['title'],
            'timestamp': '2026-02-01T00:00:00Z',
            'source': root['source'],
            'event_type': 'root'
        })
    
    prompt = f"""Analyze these news articles and generate relationships between them.

Articles:
{json.dumps(articles, indent=2)}

Generate relationships showing how articles are connected:
- AMPLIFIES: Later article reinforces/expands earlier claim
- CORRECTS: Later article corrects earlier misinformation
- COUNTERS: Later article contradicts earlier claim
- OFFICIAL_RESPONSE: Official statement responding to earlier report
- CONSEQUENCE_OF: Later article reports consequences of earlier event

Return JSON format:
{{
  "relationships": [
    {{
      "source_article_id": "art_0001",
      "target_article_id": "art_0002", 
      "relationship_type": "AMPLIFIES",
      "justification": "Brief explanation"
    }}
  ]
}}

Focus on meaningful connections. Return only valid JSON."""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        if content.startswith('```json'):
            content = content.split('\n', 1)[1].rsplit('\n```', 1)[0]
        elif content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('\n```', 1)[0]
        
        return json.loads(content)
    except Exception as e:
        print(f"Error generating relationships: {e}")
        return {"relationships": []}

def save_relationships(relationships_data):
    with open("graphs/relationships.json", "w", encoding="utf-8") as f:
        json.dump(relationships_data, f, indent=2)

if __name__ == "__main__":
    timeline = load_timeline()
    print("Generating relationships from timeline...")
    
    relationships = generate_relationships(timeline)
    print(f"Generated {len(relationships.get('relationships', []))} relationships")
    
    save_relationships(relationships)
    print("Relationships saved to graphs/relationships.json")
