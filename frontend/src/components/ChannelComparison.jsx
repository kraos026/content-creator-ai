import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const ChannelComparison = () => {
  const [channelIds, setChannelIds] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    const ids = channelIds.split(',').map(id => id.trim()).filter(Boolean);
    
    if (ids.length < 2) {
      toast.error('Veuillez entrer au moins 2 IDs de chaînes');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/youtube/compare/channels', {
        channel_ids: ids
      });
      setComparison(response.data);
      toast.success('Comparaison terminée');
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de la comparaison des chaînes');
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = (comparisons) => {
    return comparisons.map(comp => ({
      name: comp.channel_id,
      subscribers: parseInt(comp.metrics.channel_stats.total_subscribers),
      views: parseInt(comp.metrics.channel_stats.total_views),
      videos: parseInt(comp.metrics.channel_stats.total_videos),
      engagement: comp.content_analysis.avg_engagement
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4">Comparaison de chaînes</h3>
      
      <div className="mb-4">
        <textarea
          value={channelIds}
          onChange={(e) => setChannelIds(e.target.value)}
          placeholder="Entrez les IDs des chaînes à comparer (séparés par des virgules)"
          className="w-full p-2 border rounded-md h-24"
        />
      </div>

      <button
        onClick={handleCompare}
        disabled={loading}
        className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
      >
        {loading ? 'Comparaison en cours...' : 'Comparer'}
      </button>

      {comparison && (
        <div className="mt-6">
          <h4 className="font-semibold mb-4">Insights</h4>
          <ul className="list-disc pl-5 mb-6">
            {comparison.insights.map((insight, index) => (
              <li key={index} className="text-gray-700 mb-2">{insight}</li>
            ))}
          </ul>

          <div className="mb-8">
            <h4 className="font-semibold mb-4">Statistiques comparatives</h4>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={prepareChartData(comparison.channel_comparisons)}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="subscribers" fill="#FF0000" name="Abonnés" />
                  <Bar dataKey="views" fill="#00C49F" name="Vues totales" />
                  <Bar dataKey="videos" fill="#FFBB28" name="Vidéos" />
                  <Bar dataKey="engagement" fill="#0088FE" name="Engagement moyen" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {comparison.channel_comparisons.map((channel, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <h5 className="font-medium mb-2">Chaîne {channel.channel_id}</h5>
                
                <div className="space-y-2">
                  <p>Abonnés: {parseInt(channel.metrics.channel_stats.total_subscribers).toLocaleString()}</p>
                  <p>Vues totales: {parseInt(channel.metrics.channel_stats.total_views).toLocaleString()}</p>
                  <p>Nombre de vidéos: {channel.metrics.channel_stats.total_videos}</p>
                  
                  <div className="mt-4">
                    <p className="font-medium">Types de contenu populaires:</p>
                    <ul className="list-disc pl-5 mt-1">
                      {Object.entries(channel.content_analysis.most_common_types).map(([type, count], i) => (
                        <li key={i}>{type}: {count} vidéos</li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-4">
                    <p className="font-medium">Tendances d'engagement:</p>
                    <p>Taux moyen: {channel.metrics.engagement_trends.average_engagement_rate.toFixed(2)}%</p>
                    <p>Tendance: {channel.metrics.engagement_trends.engagement_trend}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChannelComparison;
