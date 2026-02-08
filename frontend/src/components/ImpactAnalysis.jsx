import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Target, AlertTriangle, ExternalLink } from 'lucide-react';
import { useState } from 'react';

// Helper function to clean raw text: remove HTML, links, and truncate to 150 chars
const cleanAndTruncateText = (text, maxLength = 150) => {
  if (!text) return '';
  // Remove HTML tags
  let cleaned = text.replace(/<[^>]*>/g, '');
  // Remove URLs (http/https links and markdown links)
  cleaned = cleaned.replace(/https?:\/\/[^\s]+/g, '');
  cleaned = cleaned.replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');
  // Remove markdown formatting
  cleaned = cleaned.replace(/[*_#`]/g, '');
  // Remove extra whitespace
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  // Truncate to maxLength
  if (cleaned.length > maxLength) {
    cleaned = cleaned.substring(0, maxLength).trim() + '...';
  }
  return cleaned;
};

export default function ImpactAnalysis({ impact }) {
  const [hoveredEvent, setHoveredEvent] = useState(null);

  const polarityConfig = {
    positive: { icon: TrendingUp, color: 'from-green-400 to-emerald-600', bg: 'bg-green-500/20' },
    negative: { icon: TrendingDown, color: 'from-red-400 to-rose-600', bg: 'bg-red-500/20' },
    mixed: { icon: Minus, color: 'from-yellow-400 to-orange-600', bg: 'bg-yellow-500/20' },
    neutral: { icon: Minus, color: 'from-gray-400 to-gray-600', bg: 'bg-gray-500/20' },
  };

  const config = polarityConfig[impact.overall_polarity] || polarityConfig.neutral;
  const Icon = config.icon;

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${config.color} flex items-center justify-center`}>
              <Icon className="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold">{impact.target_entity}</h3>
              <p className="text-gray-400">Impact Analysis</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{(impact.confidence_score * 100).toFixed(0)}%</div>
            <p className="text-sm text-gray-400">Confidence</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className={`${config.bg} rounded-xl p-4`}>
            <p className="text-sm text-gray-400 mb-1">Polarity</p>
            <p className="text-xl font-bold capitalize">{impact.overall_polarity}</p>
          </div>
          <div className="bg-blue-500/20 rounded-xl p-4">
            <p className="text-sm text-gray-400 mb-1">Impact Level</p>
            <p className="text-xl font-bold capitalize">{impact.direct_impact.impact_level}</p>
          </div>
          <div className="bg-purple-500/20 rounded-xl p-4">
            <p className="text-sm text-gray-400 mb-1">Events</p>
            <p className="text-xl font-bold">{impact.direct_impact.relevant_events_count}</p>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Target className="w-5 h-5" />
            Direct Impact
          </h4>
          <p className="text-gray-300 text-sm leading-relaxed">{impact.direct_impact.description}</p>
        </div>

        {impact.second_order_effects?.length > 0 && (
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Second-Order Effects
            </h4>
            <div className="space-y-2">
              {impact.second_order_effects.map((effect, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="flex items-start gap-3 bg-white/5 rounded-lg p-3"
                >
                  <div className="w-2 h-2 rounded-full bg-secondary mt-1.5" />
                  <p className="text-sm text-gray-300">{effect}</p>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {impact.relevant_events?.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold mb-3">Relevant Events</h4>
            <div className="space-y-2">
              {impact.relevant_events.map((event, idx) => {
                const sentimentColors = {
                  positive: 'from-green-500 to-emerald-500',
                  negative: 'from-red-500 to-rose-500',
                  neutral: 'from-gray-500 to-gray-600'
                };
                const sentColor = sentimentColors[event.sentiment] || sentimentColors.neutral;

                // Get cleaned text from raw_text, summary, or description
                const rawText = event.raw_text || event.summary || event.description || '';
                const cleanedText = cleanAndTruncateText(rawText, 150);

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onHoverStart={() => setHoveredEvent(idx)}
                    onHoverEnd={() => setHoveredEvent(null)}
                    onClick={() => event.url && window.open(event.url, '_blank')}
                    className="bg-white/5 rounded-lg p-3 cursor-pointer hover:bg-white/10 transition group"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold bg-gradient-to-r ${sentColor} text-white`}>
                            {event.sentiment}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(event.timestamp).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300 font-medium">{event.title}</p>
                        {cleanedText && (
                          <p className="text-xs text-gray-400 leading-relaxed mt-2">{cleanedText}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">{event.source}</p>
                      </div>
                      {event.url && (
                        <ExternalLink className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition flex-shrink-0" />
                      )}
                    </div>

                    <AnimatePresence>
                      {hoveredEvent === idx && cleanedText && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-3 pt-3 border-t border-white/10 overflow-hidden"
                        >
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <span>Click to read full article</span>
                            <ExternalLink className="w-3 h-3" />
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
