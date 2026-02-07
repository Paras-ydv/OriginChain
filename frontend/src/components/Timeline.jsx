import { motion, AnimatePresence } from 'framer-motion';
import { Clock, TrendingUp, AlertCircle, CheckCircle, Radio, ExternalLink } from 'lucide-react';
import { useState } from 'react';

const eventTypeConfig = {
  initial_claim: { icon: AlertCircle, color: 'from-red-500 to-orange-500', label: 'Initial Claim' },
  amplification: { icon: Radio, color: 'from-blue-500 to-cyan-500', label: 'Amplification' },
  official_response: { icon: CheckCircle, color: 'from-green-500 to-emerald-500', label: 'Official Response' },
  correction: { icon: TrendingUp, color: 'from-yellow-500 to-amber-500', label: 'Correction' },
  counter_claim: { icon: AlertCircle, color: 'from-purple-500 to-pink-500', label: 'Counter Claim' },
  consequence: { icon: TrendingUp, color: 'from-indigo-500 to-violet-500', label: 'Consequence' },
};

export default function Timeline({ events, rootOrigin, impact }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  // Create sentiment map from impact data
  const sentimentMap = {};
  if (impact?.relevant_events) {
    impact.relevant_events.forEach(event => {
      sentimentMap[event.title] = event.sentiment;
    });
  }

  return (
    <div className="relative py-12">
      <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gradient-to-b from-primary via-secondary to-primary opacity-30" />
      
      {rootOrigin && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-16 relative"
        >
          <div className="flex justify-center">
            <div className="glass glow rounded-2xl p-6 max-w-2xl w-full">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-yellow-400">Root Origin</h3>
                  <p className="text-sm text-gray-300">Confidence: {(rootOrigin.confidence * 100).toFixed(0)}%</p>
                </div>
              </div>
              <h4 className="font-semibold text-lg mb-2">{rootOrigin.title}</h4>
              <p className="text-sm text-gray-400">{rootOrigin.source} • {rootOrigin.why_root}</p>
            </div>
          </div>
        </motion.div>
      )}

      <div className="space-y-12">
        {events.map((event, idx) => {
          const config = eventTypeConfig[event.event_type] || eventTypeConfig.amplification;
          const Icon = config.icon;
          const isLeft = idx % 2 === 0;

          // Override color based on sentiment if available
          const sentiment = sentimentMap[event.title];
          let displayColor = config.color;
          if (sentiment === 'positive') {
            displayColor = 'from-green-500 to-emerald-500';
          } else if (sentiment === 'negative') {
            displayColor = 'from-red-500 to-rose-500';
          }

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: isLeft ? -50 : 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`flex items-center ${isLeft ? 'flex-row' : 'flex-row-reverse'} gap-8`}
            >
              <div className={`flex-1 ${isLeft ? 'text-right' : 'text-left'}`}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  onHoverStart={() => setHoveredIndex(idx)}
                  onHoverEnd={() => setHoveredIndex(null)}
                  onClick={() => event.url && window.open(event.url, '_blank')}
                  className="glass rounded-xl p-5 inline-block max-w-lg cursor-pointer relative group"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${displayColor} text-white`}>
                      {config.label}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(event.timestamp).toLocaleDateString()}
                    </span>
                    {event.url && (
                      <ExternalLink className="w-3 h-3 text-gray-400 ml-auto opacity-0 group-hover:opacity-100 transition" />
                    )}
                  </div>
                  <h4 className="font-semibold mb-2 text-sm leading-relaxed">{event.title}</h4>
                  <p className="text-xs text-gray-400">{event.source}</p>
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    <div className="w-full bg-gray-700 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full bg-gradient-to-r ${displayColor}`}
                        style={{ width: `${event.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-gray-400">{(event.confidence * 100).toFixed(0)}%</span>
                  </div>
                  
                  <AnimatePresence>
                    {hoveredIndex === idx && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute z-50 bottom-full mb-2 left-0 right-0 glass rounded-lg p-3 border border-white/30 max-w-xs shadow-2xl"
                      >
                        <h5 className="font-semibold text-xs mb-2 line-clamp-2">{event.title}</h5>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-400">{event.source}</span>
                          <div className="flex items-center gap-1 text-primary">
                            <span>Read more</span>
                            <ExternalLink className="w-3 h-3" />
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </div>

              <div className="relative z-10">
                <motion.div
                  whileHover={{ scale: 1.2, rotate: 360 }}
                  transition={{ duration: 0.5 }}
                  className={`w-14 h-14 rounded-full bg-gradient-to-br ${displayColor} flex items-center justify-center shadow-lg`}
                >
                  <Icon className="w-7 h-7 text-white" />
                </motion.div>
              </div>

              <div className="flex-1" />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
