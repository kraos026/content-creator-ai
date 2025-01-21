import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import KeywordAnalyzer from './KeywordAnalyzer';
import ThumbnailAnalyzer from './ThumbnailAnalyzer';
import ChannelComparison from './ChannelComparison';
import VideoDownloader from './VideoDownloader';

const YouTubeAnalytics = () => {
  // États
  const [trends, setTrends] = useState([]);
  const [videoId, setVideoId] = useState('');
  const [channelId, setChannelId] = useState('');
  const [category, setCategory] = useState('general');
  const [videoAnalysis, setVideoAnalysis] = useState(null);
  const [channelAnalysis, setChannelAnalysis] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState({
    trends: false,
    video: false,
    channel: false,
    suggestions: false
  });
  const [activeTab, setActiveTab] = useState('trends');

  const tabs = [
    { id: 'trends', label: 'Tendances' },
    { id: 'keywords', label: 'Mots-clés' },
    { id: 'thumbnails', label: 'Miniatures' },
    { id: 'comparison', label: 'Comparaison' },
    { id: 'download', label: 'Téléchargement' }
  ];

  // Gestionnaires d'événements
  const getTrends = async () => {
    setLoading(prev => ({ ...prev, trends: true }));
    try {
      const response = await axios.get('/api/youtube/trending');
      setTrends(response.data);
      toast.success('Tendances récupérées avec succès');
    } catch (error) {
      console.error('Erreur lors de la récupération des tendances:', error);
      toast.error('Erreur lors de la récupération des tendances');
    } finally {
      setLoading(prev => ({ ...prev, trends: false }));
    }
  };

  const analyzeVideo = async () => {
    if (!videoId) {
      toast.error('Veuillez entrer un ID de vidéo');
      return;
    }
    setLoading(prev => ({ ...prev, video: true }));
    try {
      const response = await axios.get(`/api/youtube/analyze/video/${videoId}`);
      setVideoAnalysis(response.data);
      toast.success('Analyse de la vidéo terminée');
    } catch (error) {
      console.error('Erreur lors de l\'analyse de la vidéo:', error);
      toast.error('Erreur lors de l\'analyse de la vidéo');
    } finally {
      setLoading(prev => ({ ...prev, video: false }));
    }
  };

  const analyzeChannel = async () => {
    if (!channelId) {
      toast.error('Veuillez entrer un ID de chaîne');
      return;
    }
    setLoading(prev => ({ ...prev, channel: true }));
    try {
      const response = await axios.get(`/api/youtube/analyze/channel/${channelId}`);
      setChannelAnalysis(response.data);
      toast.success('Analyse de la chaîne terminée');
    } catch (error) {
      console.error('Erreur lors de l\'analyse de la chaîne:', error);
      toast.error('Erreur lors de l\'analyse de la chaîne');
    } finally {
      setLoading(prev => ({ ...prev, channel: false }));
    }
  };

  const getSuggestions = async () => {
    setLoading(prev => ({ ...prev, suggestions: true }));
    try {
      const response = await axios.get(`/api/youtube/suggestions?category=${category}`);
      setSuggestions(response.data);
      toast.success('Suggestions générées avec succès');
    } catch (error) {
      console.error('Erreur lors de la récupération des suggestions:', error);
      toast.error('Erreur lors de la récupération des suggestions');
    } finally {
      setLoading(prev => ({ ...prev, suggestions: false }));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold text-red-600 text-center mb-8">YouTube Analytics</h2>

      {/* Navigation */}
      <div className="mb-8">
        <nav className="flex space-x-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md ${
                activeTab === tab.id
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Contenu des onglets */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.2 }}
      >
        {activeTab === 'trends' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Section Tendances */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-6 mb-8"
            >
              <h3 className="text-xl font-semibold mb-4">Tendances YouTube</h3>
              <button
                onClick={getTrends}
                disabled={loading.trends}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
              >
                {loading.trends ? 'Chargement...' : 'Voir les tendances'}
              </button>

              {trends.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                  {trends.map((video) => (
                    <div key={video.id} className="border rounded-lg p-4">
                      <h4 className="font-medium">{video.title}</h4>
                      <p>Vues: {video.views}</p>
                      <p>Engagement: {video.engagementRate}%</p>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>

            {/* Section Analyse de vidéo */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-6 mb-8"
            >
              <h3 className="text-xl font-semibold mb-4">Analyser une vidéo</h3>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={videoId}
                  onChange={(e) => setVideoId(e.target.value)}
                  placeholder="ID de la vidéo YouTube"
                  className="flex-1 border rounded-md px-3 py-2"
                />
                <button
                  onClick={analyzeVideo}
                  disabled={loading.video}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
                >
                  {loading.video ? 'Analyse...' : 'Analyser'}
                </button>
              </div>

              {videoAnalysis && (
                <div className="mt-4 bg-gray-50 rounded-lg p-4">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(videoAnalysis, null, 2)}
                  </pre>
                </div>
              )}
            </motion.div>

            {/* Section Analyse de chaîne */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-6 mb-8"
            >
              <h3 className="text-xl font-semibold mb-4">Analyser une chaîne</h3>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={channelId}
                  onChange={(e) => setChannelId(e.target.value)}
                  placeholder="ID de la chaîne YouTube"
                  className="flex-1 border rounded-md px-3 py-2"
                />
                <button
                  onClick={analyzeChannel}
                  disabled={loading.channel}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
                >
                  {loading.channel ? 'Analyse...' : 'Analyser'}
                </button>
              </div>

              {channelAnalysis && (
                <div className="mt-4 bg-gray-50 rounded-lg p-4">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(channelAnalysis, null, 2)}
                  </pre>
                </div>
              )}
            </motion.div>

            {/* Section Suggestions */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-6"
            >
              <h3 className="text-xl font-semibold mb-4">Suggestions de contenu</h3>
              <div className="flex gap-4">
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="flex-1 border rounded-md px-3 py-2"
                >
                  <option value="general">Général</option>
                  <option value="gaming">Gaming</option>
                  <option value="education">Education</option>
                  <option value="entertainment">Divertissement</option>
                </select>
                <button
                  onClick={getSuggestions}
                  disabled={loading.suggestions}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
                >
                  {loading.suggestions ? 'Génération...' : 'Obtenir des suggestions'}
                </button>
              </div>

              {suggestions.length > 0 && (
                <div className="mt-4 space-y-2">
                  {suggestions.map((suggestion, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      {suggestion}
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </div>
        )}

        {activeTab === 'keywords' && <KeywordAnalyzer />}
        
        {activeTab === 'thumbnails' && <ThumbnailAnalyzer />}
        
        {activeTab === 'comparison' && <ChannelComparison />}
        
        {activeTab === 'download' && <VideoDownloader />}
      </motion.div>
    </div>
  );
};

export default YouTubeAnalytics;
