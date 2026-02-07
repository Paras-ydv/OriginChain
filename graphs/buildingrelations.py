import json
import os

try:
    from google import genai
    # Read API key from .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break
    client = genai.Client(api_key=api_key)
    USE_LLM = True
except:
    USE_LLM = False

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
    
    # Generate basic relationships based on timeline order
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
        if i < len(events) - 1:
            rel_type = 'AMPLIFIES' if events[i]['event_type'] == events[i+1]['event_type'] else 'CONSEQUENCE_OF'
            relationships.append({
                'source_article_id': f'art_{i:04d}',
                'target_article_id': f'art_{i+1:04d}',
                'relationship_type': rel_type,
                'justification': 'Sequential event connection'
            })
    
    # Add some cross-connections for similar event types
    event_type_groups = {}
    for i, event in enumerate(events):
        et = event['event_type']
        if et not in event_type_groups:
            event_type_groups[et] = []
        event_type_groups[et].append(i)
    
    for et, indices in event_type_groups.items():
        if len(indices) > 1:
            for i in range(len(indices) - 1):
                if indices[i+1] - indices[i] > 1:  # Not sequential
                    relationships.append({
                        'source_article_id': f'art_{indices[i]:04d}',
                        'target_article_id': f'art_{indices[i+1]:04d}',
                        'relationship_type': 'AMPLIFIES',
                        'justification': f'Similar {et} events'
                    })
    
    return {'relationships': relationships}

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
