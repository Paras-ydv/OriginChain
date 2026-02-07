#!/usr/bin/env python3
import sys
import os
import json

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'services', 'ingestion'))

# Test relationship generation
def generate_relationships(timeline_data):
    events = timeline_data.get('events', [])
    root = timeline_data.get('root_origin', {})
    
    relationships = []
    
    if root and len(events) > 0:
        for i in range(min(3, len(events))):
            relationships.append({
                'source_article_id': 'root_origin',
                'target_article_id': f'art_{i:04d}',
                'relationship_type': 'AMPLIFIES',
                'justification': 'Initial event amplification'
            })
    
    for i in range(len(events) - 1):
        rel_type = 'AMPLIFIES' if events[i]['event_type'] == events[i+1]['event_type'] else 'CONSEQUENCE_OF'
        relationships.append({
            'source_article_id': f'art_{i:04d}',
            'target_article_id': f'art_{i+1:04d}',
            'relationship_type': rel_type,
            'justification': 'Sequential event connection'
        })
    
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

# Load timeline and test
timeline_path = os.path.join(root_dir, 'outputs', 'timeline.json')
if os.path.exists(timeline_path):
    with open(timeline_path, 'r') as f:
        timeline = json.load(f)
    
    result = generate_relationships(timeline)
    print(f"Generated {len(result['relationships'])} relationships")
    print(json.dumps(result, indent=2))
    
    # Save to file
    out_path = os.path.join(root_dir, 'outputs', 'relationships.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {out_path}")
else:
    print("No timeline.json found")
