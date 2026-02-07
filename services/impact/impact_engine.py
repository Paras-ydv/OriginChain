"""
Impact Analysis Engine - Analyzes causal impact of news events on target entities
"""

import json
import os
from datetime import datetime
from typing import List, Dict

class ImpactEngine:
    def __init__(self):
        # Define impact keywords for different polarities
        self.positive_keywords = [
            'surge', 'gain', 'rise', 'increase', 'profit', 'growth', 'success',
            'breakthrough', 'record', 'high', 'boost', 'win', 'approval', 'deal'
        ]
        self.negative_keywords = [
            'fall', 'drop', 'decline', 'loss', 'crash', 'plunge', 'concern',
            'investigation', 'lawsuit', 'recall', 'scandal', 'failure', 'cut'
        ]
        
    def analyze_impact(self, timeline_path: str, target_entity: str) -> str:
        """Analyze causal impact on target entity"""
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline = json.load(f)
        
        events = timeline.get('events', [])
        root_origin = timeline.get('root_origin', {})
        
        # Analyze each event for relevance and sentiment
        relevant_events = []
        positive_count = 0
        negative_count = 0
        
        for event in events:
            title = event.get('title', '')
            title_lower = title.lower()
            
            # Check if event mentions target entity
            if target_entity.lower() in title_lower:
                # Determine sentiment
                sentiment = self._analyze_sentiment(title_lower)
                
                relevant_events.append({
                    'title': title,
                    'source': event.get('source', 'Unknown'),
                    'timestamp': event.get('timestamp'),
                    'sentiment': sentiment,
                    'event_type': event.get('event_type', 'unknown')
                })
                
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
        
        # Determine overall impact
        impact_analysis = self._generate_impact_analysis(
            target_entity, relevant_events, events, 
            positive_count, negative_count, root_origin
        )
        
        # Save output
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "outputs", "impact.json"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(impact_analysis, f, indent=2)
        
        return output_path
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        pos_score = sum(1 for keyword in self.positive_keywords if keyword in text)
        neg_score = sum(1 for keyword in self.negative_keywords if keyword in text)
        
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_impact_analysis(
        self, target_entity: str, relevant_events: List[Dict], 
        all_events: List[Dict], positive_count: int, 
        negative_count: int, root_origin: Dict
    ) -> Dict:
        """Generate comprehensive impact analysis"""
        
        total_relevant = len(relevant_events)
        total_events = len(all_events)
        
        # Determine overall polarity
        if positive_count > negative_count:
            overall_polarity = 'positive'
            polarity_desc = 'favorable'
        elif negative_count > positive_count:
            overall_polarity = 'negative'
            polarity_desc = 'unfavorable'
        else:
            overall_polarity = 'mixed'
            polarity_desc = 'mixed'
        
        # Calculate confidence based on data quality
        if total_relevant == 0:
            confidence = 0.1
            impact_level = 'minimal'
        elif total_relevant < 3:
            confidence = 0.4
            impact_level = 'low'
        elif total_relevant < 6:
            confidence = 0.7
            impact_level = 'moderate'
        else:
            confidence = 0.9
            impact_level = 'high'
        
        # Generate direct impact description
        direct_impact = {
            'description': f"News coverage shows {impact_level} impact on {target_entity}. "
                          f"Out of {total_events} total events, {total_relevant} directly mention {target_entity}. "
                          f"Sentiment analysis indicates {polarity_desc} coverage with {positive_count} positive "
                          f"and {negative_count} negative mentions.",
            'polarity': overall_polarity,
            'impact_level': impact_level,
            'relevant_events_count': total_relevant,
            'positive_mentions': positive_count,
            'negative_mentions': negative_count
        }
        
        # Generate second-order effects based on analysis
        second_order_effects = self._generate_second_order_effects(
            target_entity, overall_polarity, impact_level, relevant_events
        )
        
        # Generate uncertainty notes
        uncertainty_notes = []
        if total_relevant < 3:
            uncertainty_notes.append("Limited data: Few events directly mention target entity")
        if positive_count == negative_count:
            uncertainty_notes.append("Mixed signals: Equal positive and negative sentiment")
        if not root_origin:
            uncertainty_notes.append("Root cause unclear: No clear origin event identified")
        
        return {
            'target_entity': target_entity,
            'direct_impact': direct_impact,
            'second_order_effects': second_order_effects,
            'overall_polarity': overall_polarity,
            'confidence_score': confidence,
            'relevant_events': relevant_events,
            'root_origin_impact': self._analyze_root_impact(root_origin, target_entity),
            'uncertainty_notes': uncertainty_notes,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_second_order_effects(
        self, target_entity: str, polarity: str, 
        impact_level: str, events: List[Dict]
    ) -> List[str]:
        """Generate second-order effects based on impact analysis"""
        effects = []
        
        if impact_level in ['moderate', 'high']:
            if polarity == 'positive':
                effects.extend([
                    f"Investor confidence in {target_entity} likely to increase",
                    f"Market valuation of {target_entity} may see upward pressure",
                    f"Competitive positioning of {target_entity} could strengthen"
                ])
            elif polarity == 'negative':
                effects.extend([
                    f"Investor sentiment toward {target_entity} may deteriorate",
                    f"Stock price of {target_entity} could face downward pressure",
                    f"Regulatory scrutiny of {target_entity} might increase"
                ])
            else:
                effects.extend([
                    f"Market uncertainty around {target_entity} likely to persist",
                    f"Stakeholders may adopt wait-and-see approach regarding {target_entity}"
                ])
        
        # Add sector-specific effects if multiple events
        if len(events) > 3:
            effects.append(f"Industry-wide implications for {target_entity}'s sector")
        
        return effects
    
    def _analyze_root_impact(self, root_origin: Dict, target_entity: str) -> Dict:
        """Analyze impact of root origin event"""
        if not root_origin:
            return {'identified': False, 'description': 'No root origin identified'}
        
        title = root_origin.get('title', '')
        if target_entity.lower() in title.lower():
            return {
                'identified': True,
                'description': f"Root event directly involves {target_entity}",
                'source': root_origin.get('source', 'Unknown'),
                'confidence': root_origin.get('confidence', 0.5)
            }
        else:
            return {
                'identified': True,
                'description': f"Root event indirectly affects {target_entity}",
                'source': root_origin.get('source', 'Unknown'),
                'confidence': root_origin.get('confidence', 0.5) * 0.7
            }
