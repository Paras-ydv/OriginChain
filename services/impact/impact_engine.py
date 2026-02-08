"""
Impact Analysis Engine - Analyzes causal impact of news events on target entities using Gemini AI
"""

import json
import os
from datetime import datetime
from typing import List, Dict

# Import translation utilities
try:
    import sys
    ingestion_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ingestion')
    sys.path.insert(0, ingestion_path)
    from utils import translate_to_english, detect_language
    from config import TRANSLATION_ENABLED
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    TRANSLATION_ENABLED = False

def translate_event_text(text: str) -> str:
    """Translate text to English if not already in English."""
    if not text or not TRANSLATION_AVAILABLE or not TRANSLATION_ENABLED:
        return text
    try:
        lang = detect_language(text)
        if lang and lang != 'en':
            return translate_to_english(text, lang)
    except:
        pass
    return text

try:
    from google import genai
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break
    client = genai.Client(api_key=api_key)
    USE_GEMINI = True
except:
    USE_GEMINI = False

class ImpactEngine:
    def __init__(self):
        self.positive_keywords = ['surge', 'gain', 'rise', 'increase', 'profit', 'growth', 'success', 'breakthrough', 'record', 'high', 'boost', 'win', 'approval', 'deal']
        self.negative_keywords = ['fall', 'drop', 'decline', 'loss', 'crash', 'plunge', 'concern', 'investigation', 'lawsuit', 'recall', 'scandal', 'failure', 'cut']
        
    def analyze_impact(self, timeline_path: str, target_entity: str) -> str:
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline = json.load(f)
        
        events = timeline.get('events', [])
        root_origin = timeline.get('root_origin', {})
        
        if USE_GEMINI and len(events) > 0:
            return self._analyze_with_gemini(events, root_origin, target_entity, timeline_path)
        else:
            return self._analyze_with_keywords(events, root_origin, target_entity, timeline_path)
    
    def _analyze_with_gemini(self, events: List[Dict], root_origin: Dict, target_entity: str, timeline_path: str) -> str:
        batch_size = 10
        all_relevant_events = []
        
        for i in range(0, len(events), batch_size):
            batch = events[i:i+batch_size]
            
            prompt = f"""Analyze impact of these news events on {target_entity}.

Events:
{json.dumps([{'title': e['title'], 'source': e['source'], 'timestamp': e['timestamp']} for e in batch], indent=2)}

For each event, determine:
1. Is it relevant to {target_entity}? (yes/no)
2. Sentiment: positive, negative, or neutral
3. Brief impact (1 sentence)

Return JSON:
{{
  "events": [
    {{"title": "...", "relevant": true, "sentiment": "positive", "impact": "..."}}
  ]
}}"""
            
            try:
                response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=prompt)
                content = response.text.strip()
                
                if content.startswith('```json'):
                    content = content.split('\n', 1)[1].rsplit('\n```', 1)[0]
                elif content.startswith('```'):
                    content = content.split('\n', 1)[1].rsplit('\n```', 1)[0]
                
                result = json.loads(content)
                
                for j, event_analysis in enumerate(result.get('events', [])):
                    if event_analysis.get('relevant') and j < len(batch):
                        original_event = batch[j]
                        all_relevant_events.append({
                            'title': translate_event_text(original_event['title']),
                            'source': original_event['source'],
                            'timestamp': original_event['timestamp'],
                            'sentiment': event_analysis.get('sentiment', 'neutral'),
                            'event_type': original_event['event_type'],
                            'url': original_event.get('url', ''),
                            'summary': translate_event_text(original_event.get('summary', '')),
                            'raw_text': translate_event_text(original_event.get('clean_text', original_event.get('raw_text', ''))),
                            'impact_description': event_analysis.get('impact', '')
                        })
            except Exception as e:
                print(f"Gemini failed for batch {i}: {e}")
                for event in batch:
                    if target_entity.lower() in event['title'].lower():
                        all_relevant_events.append({
                            'title': translate_event_text(event['title']),
                            'source': event['source'],
                            'timestamp': event['timestamp'],
                            'sentiment': self._analyze_sentiment(event['title'].lower()),
                            'event_type': event['event_type'],
                            'url': event.get('url', ''),
                            'summary': translate_event_text(event.get('summary', '')),
                            'raw_text': translate_event_text(event.get('clean_text', event.get('raw_text', '')))
                        })
        
        positive_count = sum(1 for e in all_relevant_events if e['sentiment'] == 'positive')
        negative_count = sum(1 for e in all_relevant_events if e['sentiment'] == 'negative')
        
        overall_polarity = 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'mixed'
        confidence = min(0.9, 0.5 + (len(all_relevant_events) * 0.05))
        impact_level = 'high' if len(all_relevant_events) > 5 else 'moderate' if len(all_relevant_events) > 2 else 'low'
        
        impact_analysis = {
            'target_entity': target_entity,
            'direct_impact': {
                'description': f"AI analysis identified {len(all_relevant_events)} relevant events. Sentiment: {positive_count} positive, {negative_count} negative.",
                'polarity': overall_polarity,
                'impact_level': impact_level,
                'relevant_events_count': len(all_relevant_events),
                'positive_mentions': positive_count,
                'negative_mentions': negative_count
            },
            'second_order_effects': self._generate_second_order_effects(target_entity, overall_polarity, impact_level, all_relevant_events),
            'overall_polarity': overall_polarity,
            'confidence_score': confidence,
            'relevant_events': all_relevant_events,
            'root_origin_impact': self._analyze_root_impact(root_origin, target_entity),
            'uncertainty_notes': [],
            'generated_at': datetime.now().isoformat()
        }
        
        output_path = os.path.join(os.path.dirname(timeline_path), "impact.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(impact_analysis, f, indent=2)
        
        return output_path
    
    def _analyze_with_keywords(self, events: List[Dict], root_origin: Dict, target_entity: str, timeline_path: str) -> str:
        relevant_events = []
        positive_count = 0
        negative_count = 0
        
        for event in events:
            title = event.get('title', '')
            if target_entity.lower() in title.lower():
                sentiment = self._analyze_sentiment(title.lower())
                relevant_events.append({
                    'title': translate_event_text(title),
                    'source': event.get('source', 'Unknown'),
                    'timestamp': event.get('timestamp'),
                    'sentiment': sentiment,
                    'event_type': event.get('event_type', 'unknown'),
                    'url': event.get('url', ''),
                    'summary': translate_event_text(event.get('summary', '')),
                    'raw_text': translate_event_text(event.get('clean_text', event.get('raw_text', '')))
                })
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
        
        overall_polarity = 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'mixed'
        confidence = 0.9 if len(relevant_events) > 5 else 0.7 if len(relevant_events) > 2 else 0.4
        impact_level = 'high' if len(relevant_events) > 5 else 'moderate' if len(relevant_events) > 2 else 'low'
        
        impact_analysis = {
            'target_entity': target_entity,
            'direct_impact': {
                'description': f"Found {len(relevant_events)} relevant events. Sentiment: {positive_count} positive, {negative_count} negative.",
                'polarity': overall_polarity,
                'impact_level': impact_level,
                'relevant_events_count': len(relevant_events),
                'positive_mentions': positive_count,
                'negative_mentions': negative_count
            },
            'second_order_effects': self._generate_second_order_effects(target_entity, overall_polarity, impact_level, relevant_events),
            'overall_polarity': overall_polarity,
            'confidence_score': confidence,
            'relevant_events': relevant_events,
            'root_origin_impact': self._analyze_root_impact(root_origin, target_entity),
            'uncertainty_notes': [],
            'generated_at': datetime.now().isoformat()
        }
        
        output_path = os.path.join(os.path.dirname(timeline_path), "impact.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(impact_analysis, f, indent=2)
        
        return output_path
    
    def _analyze_sentiment(self, text: str) -> str:
        pos = sum(1 for k in self.positive_keywords if k in text)
        neg = sum(1 for k in self.negative_keywords if k in text)
        return 'positive' if pos > neg else 'negative' if neg > pos else 'neutral'
    
    def _generate_second_order_effects(self, target_entity: str, polarity: str, impact_level: str, events: List[Dict]) -> List[str]:
        effects = []
        if impact_level in ['moderate', 'high']:
            if polarity == 'positive':
                effects = [f"Investor confidence in {target_entity} likely to increase", f"Market valuation may see upward pressure"]
            elif polarity == 'negative':
                effects = [f"Investor sentiment toward {target_entity} may deteriorate", f"Stock price could face downward pressure"]
            else:
                effects = [f"Market uncertainty around {target_entity} likely to persist"]
        if len(events) > 3:
            effects.append(f"Industry-wide implications for {target_entity}'s sector")
        return effects
    
    def _analyze_root_impact(self, root_origin: Dict, target_entity: str) -> Dict:
        if not root_origin:
            return {'identified': False, 'description': 'No root origin identified'}
        title = root_origin.get('title', '')
        if target_entity.lower() in title.lower():
            return {'identified': True, 'description': f"Root event directly involves {target_entity}", 'source': root_origin.get('source', 'Unknown'), 'confidence': root_origin.get('confidence', 0.5)}
        return {'identified': True, 'description': f"Root event indirectly affects {target_entity}", 'source': root_origin.get('source', 'Unknown'), 'confidence': root_origin.get('confidence', 0.5) * 0.7}
