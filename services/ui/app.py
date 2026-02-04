"""  
OriginChain UI - Minimal Streamlit App
"""

import streamlit as st
import sys
import os
import json
import importlib.util

# Get the root directory (two levels up from ui/)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'services', 'ingestion'))

# Import ingestion functions directly
from ingestor import ingest_news

# Import other services with absolute paths

# Load timeline builder
timeline_spec = importlib.util.spec_from_file_location(
    "timeline_builder", 
    os.path.join(root_dir, 'services', 'timeline', 'timeline_builder.py')
)
timeline_module = importlib.util.module_from_spec(timeline_spec)
timeline_spec.loader.exec_module(timeline_module)
TimelineBuilder = timeline_module.TimelineBuilder

# Load impact engine
impact_spec = importlib.util.spec_from_file_location(
    "impact_engine", 
    os.path.join(root_dir, 'services', 'impact', 'impact_engine.py')
)
impact_module = importlib.util.module_from_spec(impact_spec)
impact_spec.loader.exec_module(impact_module)
ImpactEngine = impact_module.ImpactEngine

st.title("🔗 OriginChain - NewsTrace AI")

query = st.text_input("News Query", "Tesla stock price")
target_entity = st.text_input("Target Entity", "Tesla")
max_articles = st.number_input("Max Articles", value=20, min_value=1, max_value=100)

if st.button("🚀 Run Analysis"):
    with st.spinner("Processing..."):
        # Ingest news
        result = ingest_news(query, max_articles, output_path=os.path.join(root_dir, "outputs", "articles.json"))
        st.success(f"Fetched {len(result.articles)} articles")
        
        # Build timeline
        timeline_builder = TimelineBuilder()
        timeline_path = timeline_builder.build_timeline(os.path.join(root_dir, "outputs", "articles.json"))
        
        # Analyze impact
        impact_engine = ImpactEngine()
        impact_path = impact_engine.analyze_impact(timeline_path, target_entity)
        
        st.success("Analysis complete!")
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📰 Articles")
            for article in result.articles[:5]:
                st.write(f"**{article.title}**")
                st.write(f"Source: {article.source_name}")
                st.write("---")
        
        with col2:
            st.subheader("📊 Impact Analysis")
            if os.path.exists(impact_path):
                with open(impact_path, 'r', encoding='utf-8') as f:
                    impact_data = json.load(f)
                
                st.write(f"**Target:** {impact_data['target_entity']}")
                st.write(f"**Impact Level:** {impact_data['direct_impact']['polarity'].title()}")
                st.write(f"**Confidence:** {impact_data['confidence_score']:.0%}")
                st.write(f"**Relevant Events:** {impact_data['direct_impact'].get('relevant_events', 0)}")
                
                if impact_data['second_order_effects']:
                    st.write("**Second-order Effects:**")
                    for effect in impact_data['second_order_effects']:
                        st.write(f"• {effect}")
            else:
                st.write(f"Target: {target_entity}")
                st.write("Impact: Analysis pending")
                st.write("Confidence: N/A")