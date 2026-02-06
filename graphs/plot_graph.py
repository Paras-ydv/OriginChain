import json
import plotly.graph_objects as go
from datetime import datetime
import networkx as nx

def load_timeline(json_path="outputs/timeline.json"):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_timeline_graph(timeline_data):
    events = timeline_data.get('events', [])
    
    # Sort events by timestamp
    events = sorted(events, key=lambda x: x['timestamp'])
    
    timestamps = []
    titles = []
    event_types = []
    confidences = []
    sources = []
    
    for event in events:
        dt = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        timestamps.append(dt)
        titles.append(event['title'][:25] + '...' if len(event['title']) > 25 else event['title'])
        event_types.append(event['event_type'])
        confidences.append(event['confidence'])
        sources.append(event['source'])
    
    color_map = {
        'initial_claim': '#FF6B6B',
        'amplification': '#4ECDC4', 
        'official_response': '#45B7D1',
        'correction': '#FFA07A',
        'counter_claim': '#98D8C8',
        'consequence': '#F7DC6F'
    }
    
    fig = go.Figure()
    
    # Main timeline line
    if timestamps:
        fig.add_trace(go.Scatter(
            x=[min(timestamps), max(timestamps)],
            y=[0, 0],
            mode='lines',
            line=dict(color='#2C3E50', width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Distribute events with varied Y positions to avoid overlap
    y_positions = [0.8, -0.8, 0.6, -0.6, 1.0, -1.0, 0.5, -0.5, 0.9, -0.9, 0.7, -0.7]
    
    for i, (ts, title, et, conf, source) in enumerate(zip(timestamps, titles, event_types, confidences, sources)):
        y_pos = y_positions[i % len(y_positions)]
        
        # Connecting line
        fig.add_trace(go.Scatter(
            x=[ts, ts],
            y=[0, y_pos],
            mode='lines',
            line=dict(color='#BDC3C7', width=1.5),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Event marker
        time_str = ts.strftime('%m/%d %H:%M')
        text_pos = 'top center' if y_pos > 0 else 'bottom center'
        
        fig.add_trace(go.Scatter(
            x=[ts],
            y=[y_pos],
            mode='markers+text',
            marker=dict(
                size=15,
                color=color_map.get(et, '#95A5A6'),
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            text=[title],
            textposition=text_pos,
            textfont=dict(size=8, color='#2C3E50'),
            hovertemplate=f'<b>{title}</b><br>' +
                         f'Type: {et}<br>' +
                         f'Source: {source}<br>' +
                         f'Confidence: {conf:.0%}<br>' +
                         f'Time: {ts.strftime("%Y-%m-%d %H:%M")}<br>' +
                         '<extra></extra>',
            showlegend=False
        ))
    
    # Root origin marker
    root = timeline_data.get('root_origin', {})
    if root and timestamps:
        fig.add_trace(go.Scatter(
            x=[min(timestamps)],
            y=[0],
            mode='markers+text',
            marker=dict(size=25, color='#FFD700', symbol='star', line=dict(width=3, color='#FF8C00')),
            text=['ROOT'],
            textposition='middle center',
            textfont=dict(size=10, color='#2C3E50', family='Arial Black'),
            hovertemplate=f'<b>Root Origin</b><br>{root.get("title", "")[:60]}<br>' +
                         f'Confidence: {root.get("confidence", 0):.0%}<extra></extra>',
            showlegend=False
        ))
    
    fig.update_layout(
        title=dict(
            text='<b>📰 News Event Timeline</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color='#2C3E50')
        ),
        xaxis=dict(
            title='Timeline',
            showgrid=True,
            gridcolor='#ECF0F1',
            tickformat='%m/%d %H:%M'
        ),
        yaxis=dict(
            visible=False,
            range=[-1.3, 1.3]
        ),
        height=700,
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='#F8F9FA',
        margin=dict(l=50, r=50, t=80, b=150)
    )
    
    return fig

def create_neo4j_graph(timeline_data):
    try:
        with open('graphs/relationships.json', 'r', encoding='utf-8') as f:
            rel_data = json.load(f)
    except FileNotFoundError:
        return None
    
    events = timeline_data.get('events', [])
    root = timeline_data.get('root_origin', {})
    
    # Create articles dict
    articles = {}
    for i, event in enumerate(events):
        articles[f'art_{i:04d}'] = {
            'title': event['title'][:50],
            'source': event['source'],
            'event_type': event['event_type']
        }
    
    if root:
        articles['root_origin'] = {
            'title': root['title'][:50],
            'source': root['source'],
            'event_type': 'root'
        }
    
    relationships = rel_data.get('relationships', [])
    
    G = nx.DiGraph()
    
    for rel in relationships:
        src_id = rel['source_article_id']
        tgt_id = rel['target_article_id']
        
        if src_id in articles:
            G.add_node(src_id, **articles[src_id])
        if tgt_id in articles:
            G.add_node(tgt_id, **articles[tgt_id])
        
        G.add_edge(src_id, tgt_id, relation=rel['relationship_type'],
                  justification=rel['justification'])
    
    if len(G.nodes()) == 0:
        return None
    
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    edge_trace = go.Scatter(x=[], y=[], line=dict(width=1, color='#888'), 
                           hoverinfo='none', mode='lines')
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    node_x, node_y, node_text, node_customdata = [], [], [], []
    color_map = {'AMPLIFIES': '#4ECDC4', 'CORRECTS': '#FFA07A', 'COUNTERS': '#FF6B6B',
                 'OFFICIAL_RESPONSE': '#45B7D1', 'CONSEQUENCE_OF': '#F7DC6F', 
                 'root': '#FFD700', 'initial_claim': '#98D8C8', 'amplification': '#4ECDC4'}
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_data = G.nodes[node]
        node_text.append(node_data['event_type'])
        node_customdata.append([node_data['title'], node_data['source'], node_data['event_type']])
    
    node_colors = [color_map.get(G.nodes[n]['event_type'], '#95A5A6') for n in G.nodes()]
    
    node_trace = go.Scatter(x=node_x, y=node_y, text=node_text, mode='markers+text',
                           hovertemplate='<b>%{customdata[0]}</b><br>Source: %{customdata[1]}<br>Type: %{customdata[2]}<extra></extra>',
                           marker=dict(size=20, color=node_colors, line=dict(width=2, color='white')),
                           textposition='top center', customdata=node_customdata)
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(title=dict(text='<b>Article Relationship Network</b>', font=dict(size=24)),
                                   showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=40),
                                   xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                   yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                   plot_bgcolor='white', height=600))
    return fig