import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2, Sparkles, Share2, Download } from 'lucide-react';
import axios from 'axios';
import Timeline from './components/Timeline';
import ImpactAnalysis from './components/ImpactAnalysis';
import NetworkGraph from './components/NetworkGraph';
import SentimentChart from './components/SentimentChart';
import SourceDiversity from './components/SourceDiversity';

export default function App() {
  const [query, setQuery] = useState('Tesla stock price');
  const [targetEntity, setTargetEntity] = useState('Tesla');
  const [maxArticles, setMaxArticles] = useState(20);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [caseId, setCaseId] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/analyze', {
        query,
        target_entity: targetEntity,
        max_articles: maxArticles,
      });
      setData(response.data);
      setCaseId(response.data.case_id);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    if (!caseId) return;
    const shareUrl = `${window.location.origin}?case=${caseId}`;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setShowShareModal(true);
      setTimeout(() => setShowShareModal(false), 3000);
    } catch (err) {
      alert(`Share this link: ${shareUrl}`);
    }
  };

  const handleExport = () => {
    window.open(`/api/export/${caseId}`, '_blank');
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-10 h-10 text-primary" />
            <h1 className="text-6xl font-bold bg-gradient-to-r from-primary via-secondary to-pink-500 bg-clip-text text-transparent pb-1">
              OriginChain
            </h1>
          </div>
          <p className="text-xl text-gray-400">NewsTrace AI - Trace the Origin of Any News</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-3xl p-8 mb-12"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium mb-2">News Query</label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:border-primary focus:outline-none transition"
                placeholder="e.g., Tesla stock price"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Target Entity</label>
              <input
                type="text"
                value={targetEntity}
                onChange={(e) => setTargetEntity(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:border-primary focus:outline-none transition"
                placeholder="e.g., Tesla"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Max Articles</label>
              <input
                type="number"
                value={maxArticles}
                onChange={(e) => setMaxArticles(parseInt(e.target.value))}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 focus:border-primary focus:outline-none transition"
                min="1"
                max="100"
              />
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition font-semibold text-lg flex items-center justify-center gap-3 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="w-6 h-6" />
                Run Analysis
              </>
            )}
          </button>
        </motion.div>

        {data && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="space-y-12"
          >
            <div className="flex justify-end gap-3">
              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition border border-white/20"
              >
                <Share2 className="w-4 h-4" />
                Share Analysis
              </button>
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:opacity-90 transition"
              >
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>

            {showShareModal && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="fixed top-8 right-8 glass rounded-lg p-4 border border-green-500/50 shadow-2xl z-50"
              >
                <p className="text-sm text-green-400 font-semibold">✓ Link copied to clipboard!</p>
              </motion.div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SentimentChart impact={data.impact} />
              <SourceDiversity timeline={data.timeline} />
            </div>

            <div>
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
                <div className="w-2 h-8 bg-gradient-to-b from-primary to-secondary rounded-full" />
                Timeline Analysis
              </h2>
              <Timeline
                events={data.timeline.events}
                rootOrigin={data.timeline.root_origin}
                impact={data.impact}
              />
            </div>

            <div>
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
                <div className="w-2 h-8 bg-gradient-to-b from-secondary to-pink-500 rounded-full" />
                Network Graph
              </h2>
              <NetworkGraph
                timeline={data.timeline}
                relationships={data.relationships}
              />
            </div>

            <div>
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
                <div className="w-2 h-8 bg-gradient-to-b from-pink-500 to-purple-500 rounded-full" />
                Impact Analysis
              </h2>
              <ImpactAnalysis impact={data.impact} />
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
