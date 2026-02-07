import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Network, Zap, GitBranch, Info } from 'lucide-react';

export default function NetworkGraph({ timeline, relationships }) {
  const canvasRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });

  useEffect(() => {
    if (!canvasRef.current || !timeline || !relationships?.relationships) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    ctx.scale(2, 2);

    const nodes = [];
    const nodeMap = {};
    
    timeline.events.forEach((event, i) => {
      const id = `art_${String(i).padStart(4, '0')}`;
      const node = {
        id, title: event.title, source: event.source, type: event.event_type,
        x: Math.random() * rect.width, y: Math.random() * rect.height, vx: 0, vy: 0
      };
      nodes.push(node);
      nodeMap[id] = node;
    });

    if (timeline.root_origin) {
      const rootNode = {
        id: 'root_origin', title: timeline.root_origin.title, source: timeline.root_origin.source,
        type: 'root', x: rect.width / 2, y: rect.height / 2, vx: 0, vy: 0
      };
      nodes.push(rootNode);
      nodeMap['root_origin'] = rootNode;
    }

    const edges = [];
    relationships.relationships?.forEach(rel => {
      if (nodeMap[rel.source_article_id] && nodeMap[rel.target_article_id]) {
        edges.push({
          source: nodeMap[rel.source_article_id],
          target: nodeMap[rel.target_article_id],
          type: rel.relationship_type
        });
      }
    });

    setStats({ nodes: nodes.length, edges: edges.length });

    const typeColors = {
      root: '#FFD700', initial_claim: '#ef4444', amplification: '#3b82f6',
      official_response: '#10b981', correction: '#f59e0b', counter_claim: '#a855f7', consequence: '#6366f1'
    };

    const edgeColors = {
      AMPLIFIES: '#3b82f6', CORRECTS: '#f59e0b', COUNTERS: '#ef4444',
      OFFICIAL_RESPONSE: '#10b981', CONSEQUENCE_OF: '#6366f1'
    };

    const simulate = () => {
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 1500 / (dist * dist);
          nodes[i].vx -= (dx / dist) * force;
          nodes[i].vy -= (dy / dist) * force;
          nodes[j].vx += (dx / dist) * force;
          nodes[j].vy += (dy / dist) * force;
        }
      }

      edges.forEach(edge => {
        const dx = edge.target.x - edge.source.x;
        const dy = edge.target.y - edge.source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = dist * 0.015;
        edge.source.vx += (dx / dist) * force;
        edge.source.vy += (dy / dist) * force;
        edge.target.vx -= (dx / dist) * force;
        edge.target.vy -= (dy / dist) * force;
      });

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      nodes.forEach(node => {
        node.vx += (centerX - node.x) * 0.002;
        node.vy += (centerY - node.y) * 0.002;
        node.vx *= 0.85;
        node.vy *= 0.85;
        node.x += node.vx;
        node.y += node.vy;
        node.x = Math.max(40, Math.min(rect.width - 40, node.x));
        node.y = Math.max(40, Math.min(rect.height - 40, node.y));
      });
    };

    const render = () => {
      ctx.clearRect(0, 0, rect.width, rect.height);

      edges.forEach(edge => {
        const color = edgeColors[edge.type] || '#64748b';
        ctx.shadowBlur = 8;
        ctx.shadowColor = color;
        ctx.beginPath();
        ctx.moveTo(edge.source.x, edge.source.y);
        ctx.lineTo(edge.target.x, edge.target.y);
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.globalAlpha = 0.6;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;

        const angle = Math.atan2(edge.target.y - edge.source.y, edge.target.x - edge.source.x);
        const arrowX = edge.target.x - Math.cos(angle) * 25;
        const arrowY = edge.target.y - Math.sin(angle) * 25;
        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - 10 * Math.cos(angle - Math.PI / 6), arrowY - 10 * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(arrowX - 10 * Math.cos(angle + Math.PI / 6), arrowY - 10 * Math.sin(angle + Math.PI / 6));
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
      });

      nodes.forEach(node => {
        const isRoot = node.type === 'root';
        const radius = isRoot ? 20 : 14;
        const color = typeColors[node.type] || '#94a3b8';
        ctx.shadowBlur = 15;
        ctx.shadowColor = color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 3;
        ctx.stroke();

        if (isRoot) {
          ctx.fillStyle = '#000';
          ctx.font = 'bold 14px Arial';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('★', node.x, node.y);
        }
      });
    };

    let frame = 0;
    const animate = () => {
      if (frame < 400) {
        simulate();
        render();
        frame++;
        requestAnimationFrame(animate);
      } else {
        render();
      }
    };
    animate();

    const handleMouseMove = (e) => {
      const x = e.offsetX;
      const y = e.offsetY;
      let found = null;
      nodes.forEach(node => {
        const dist = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
        if (dist < 20) found = node;
      });
      setHoveredNode(found);
      canvas.style.cursor = found ? 'pointer' : 'default';
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    return () => canvas.removeEventListener('mousemove', handleMouseMove);
  }, [timeline, relationships]);

  if (!timeline?.events?.length || !relationships?.relationships?.length) {
    return (
      <div className="glass rounded-2xl p-12 text-center">
        <Network className="w-16 h-16 mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400">No relationships to display</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <GitBranch className="w-6 h-6 text-primary" />
            <h3 className="text-xl font-bold">Article Relationship Network</h3>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-primary" />
              <span className="text-gray-400">{stats.nodes} Nodes</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-secondary" />
              <span className="text-gray-400">{stats.edges} Connections</span>
            </div>
          </div>
        </div>

        <canvas ref={canvasRef} className="w-full h-[600px] rounded-xl bg-gradient-to-br from-slate-950/80 to-purple-950/80 border border-white/10" />

        {hoveredNode && (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
            className="absolute top-24 right-8 glass rounded-xl p-4 max-w-sm border border-white/30 shadow-2xl">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-4 h-4 rounded-full shadow-lg" style={{
                background: { root: '#FFD700', initial_claim: '#ef4444', amplification: '#3b82f6',
                  official_response: '#10b981', correction: '#f59e0b', counter_claim: '#a855f7', consequence: '#6366f1'
                }[hoveredNode.type] || '#94a3b8'
              }} />
              <span className="text-xs font-bold text-gray-300 uppercase tracking-wide">
                {hoveredNode.type.replace('_', ' ')}
              </span>
            </div>
            <h4 className="font-semibold text-sm mb-2 leading-relaxed">{hoveredNode.title}</h4>
            <p className="text-xs text-gray-400">{hoveredNode.source}</p>
          </motion.div>
        )}

        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Node Types</p>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-yellow-400 shadow-lg" />
                <span className="text-gray-300">Root Origin</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-gray-300">Initial Claim</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-gray-300">Amplification</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-300">Official Response</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Relationship Types</p>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <Zap className="w-3 h-3 text-blue-400" />
                <span className="text-gray-300">Amplifies</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Zap className="w-3 h-3 text-yellow-400" />
                <span className="text-gray-300">Corrects</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Zap className="w-3 h-3 text-red-400" />
                <span className="text-gray-300">Counters</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Zap className="w-3 h-3 text-indigo-400" />
                <span className="text-gray-300">Consequence</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-start gap-2 bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-300 leading-relaxed">
            Hover over nodes to see article details. The graph shows how news articles are interconnected through amplification, corrections, and consequences.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
