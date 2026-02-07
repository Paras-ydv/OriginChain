import { motion } from 'framer-motion';
import { LineChart, TrendingUp, TrendingDown } from 'lucide-react';

export default function SentimentChart({ impact }) {
  if (!impact?.relevant_events?.length) return null;

  // Group events by date and calculate sentiment score
  const sentimentData = impact.relevant_events.reduce((acc, event) => {
    const date = new Date(event.timestamp).toLocaleDateString();
    if (!acc[date]) {
      acc[date] = { date, positive: 0, negative: 0, neutral: 0, total: 0 };
    }
    acc[date][event.sentiment]++;
    acc[date].total++;
    return acc;
  }, {});

  const chartData = Object.values(sentimentData).map(d => ({
    date: d.date,
    score: ((d.positive - d.negative) / d.total) * 100,
    positive: d.positive,
    negative: d.negative,
    neutral: d.neutral
  }));

  const maxScore = Math.max(...chartData.map(d => Math.abs(d.score)));
  const overallTrend = chartData[chartData.length - 1]?.score > chartData[0]?.score ? 'up' : 'down';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <LineChart className="w-6 h-6 text-primary" />
          <h3 className="text-xl font-bold">Sentiment Timeline</h3>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${overallTrend === 'up' ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
          {overallTrend === 'up' ? <TrendingUp className="w-4 h-4 text-green-400" /> : <TrendingDown className="w-4 h-4 text-red-400" />}
          <span className={`text-sm font-semibold ${overallTrend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
            {overallTrend === 'up' ? 'Improving' : 'Declining'}
          </span>
        </div>
      </div>

      <div className="relative h-64 mb-4">
        <svg className="w-full h-full">
          {/* Grid lines */}
          <line x1="40" y1="32" x2="40" y2="224" stroke="#374151" strokeWidth="2" />
          <line x1="40" y1="224" x2="100%" y2="224" stroke="#374151" strokeWidth="2" />
          <line x1="40" y1="128" x2="100%" y2="128" stroke="#374151" strokeWidth="1" strokeDasharray="4" opacity="0.3" />
          
          {/* Y-axis labels */}
          <text x="10" y="36" fill="#9ca3af" fontSize="12">+100</text>
          <text x="20" y="132" fill="#9ca3af" fontSize="12">0</text>
          <text x="10" y="228" fill="#9ca3af" fontSize="12">-100</text>

          {/* Line chart */}
          <polyline
            points={chartData.map((d, i) => {
              const x = 60 + (i * (window.innerWidth * 0.8 - 100) / (chartData.length - 1));
              const y = 128 - (d.score / 100) * 96;
              return `${x},${y}`;
            }).join(' ')}
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Gradient */}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
          </defs>

          {/* Data points */}
          {chartData.map((d, i) => {
            const x = 60 + (i * (window.innerWidth * 0.8 - 100) / (chartData.length - 1));
            const y = 128 - (d.score / 100) * 96;
            const color = d.score > 0 ? '#10b981' : d.score < 0 ? '#ef4444' : '#f59e0b';
            return (
              <g key={i}>
                <circle cx={x} cy={y} r="5" fill={color} stroke="#fff" strokeWidth="2" />
                <text x={x} y="245" fill="#9ca3af" fontSize="10" textAnchor="middle">
                  {d.date.split('/').slice(0, 2).join('/')}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-green-500/10 rounded-lg p-3 border border-green-500/30">
          <p className="text-xs text-gray-400 mb-1">Positive</p>
          <p className="text-2xl font-bold text-green-400">
            {chartData.reduce((sum, d) => sum + d.positive, 0)}
          </p>
        </div>
        <div className="bg-gray-500/10 rounded-lg p-3 border border-gray-500/30">
          <p className="text-xs text-gray-400 mb-1">Neutral</p>
          <p className="text-2xl font-bold text-gray-400">
            {chartData.reduce((sum, d) => sum + d.neutral, 0)}
          </p>
        </div>
        <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/30">
          <p className="text-xs text-gray-400 mb-1">Negative</p>
          <p className="text-2xl font-bold text-red-400">
            {chartData.reduce((sum, d) => sum + d.negative, 0)}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
