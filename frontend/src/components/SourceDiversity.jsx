import { motion } from 'framer-motion';
import { PieChart, Shield } from 'lucide-react';

export default function SourceDiversity({ timeline }) {
  if (!timeline?.events?.length) return null;

  // Count sources and calculate credibility
  const sourceStats = timeline.events.reduce((acc, event) => {
    const source = event.source;
    if (!acc[source]) {
      acc[source] = { count: 0, credibility: event.credibility || 0.6 };
    }
    acc[source].count++;
    return acc;
  }, {});

  const sources = Object.entries(sourceStats)
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  const total = sources.reduce((sum, s) => sum + s.count, 0);
  const avgCredibility = sources.reduce((sum, s) => sum + s.credibility * s.count, 0) / total;

  const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#6366f1', '#a855f7'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <PieChart className="w-6 h-6 text-primary" />
          <h3 className="text-xl font-bold">Source Diversity</h3>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20">
          <Shield className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-semibold text-blue-400">
            {(avgCredibility * 100).toFixed(0)}% Credibility
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="relative">
          <svg viewBox="0 0 200 200" className="w-full">
            {sources.map((source, i) => {
              const percentage = (source.count / total) * 100;
              const startAngle = sources.slice(0, i).reduce((sum, s) => sum + (s.count / total) * 360, 0);
              const endAngle = startAngle + (percentage / 100) * 360;
              
              const startRad = (startAngle - 90) * Math.PI / 180;
              const endRad = (endAngle - 90) * Math.PI / 180;
              
              const x1 = 100 + 80 * Math.cos(startRad);
              const y1 = 100 + 80 * Math.sin(startRad);
              const x2 = 100 + 80 * Math.cos(endRad);
              const y2 = 100 + 80 * Math.sin(endRad);
              
              const largeArc = percentage > 50 ? 1 : 0;
              
              return (
                <g key={i}>
                  <path
                    d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`}
                    fill={colors[i]}
                    opacity="0.8"
                    stroke="#fff"
                    strokeWidth="2"
                  />
                </g>
              );
            })}
            <circle cx="100" cy="100" r="50" fill="#1e293b" />
            <text x="100" y="95" textAnchor="middle" fill="#fff" fontSize="20" fontWeight="bold">
              {sources.length}
            </text>
            <text x="100" y="110" textAnchor="middle" fill="#94a3b8" fontSize="12">
              Sources
            </text>
          </svg>
        </div>

        {/* Legend */}
        <div className="space-y-2">
          {sources.map((source, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center justify-between bg-white/5 rounded-lg p-2"
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: colors[i] }}
                />
                <span className="text-sm text-gray-300 truncate">{source.name}</span>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="text-xs text-gray-500">{source.count} articles</span>
                <div className="flex items-center gap-1">
                  <Shield className="w-3 h-3 text-blue-400" />
                  <span className="text-xs text-blue-400">{(source.credibility * 100).toFixed(0)}%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <p className="text-xs text-gray-300">
          <span className="font-semibold text-blue-400">Diversity Score: High</span> - 
          Analysis includes {sources.length} different sources with average credibility of {(avgCredibility * 100).toFixed(0)}%
        </p>
      </div>
    </motion.div>
  );
}
