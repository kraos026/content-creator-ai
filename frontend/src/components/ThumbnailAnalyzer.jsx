import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const ThumbnailAnalyzer = () => {
  const [channelId, setChannelId] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!channelId.trim()) {
      toast.error('Veuillez entrer un ID de chaîne');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/youtube/thumbnails/analyze', {
        channel_id: channelId
      });
      setAnalysis(response.data);
      toast.success('Analyse des miniatures terminée');
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de l\'analyse des miniatures');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4">Analyse des miniatures</h3>
      
      <div className="mb-4">
        <input
          type="text"
          value={channelId}
          onChange={(e) => setChannelId(e.target.value)}
          placeholder="ID de la chaîne YouTube"
          className="w-full p-2 border rounded-md"
        />
      </div>

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
      >
        {loading ? 'Analyse en cours...' : 'Analyser les miniatures'}
      </button>

      {analysis && (
        <div className="mt-6">
          <h4 className="font-semibold mb-4">Meilleures pratiques</h4>
          <ul className="list-disc pl-5 mb-6">
            {analysis.best_practices.map((practice, index) => (
              <li key={index} className="text-gray-700 mb-2">{practice}</li>
            ))}
          </ul>

          <h4 className="font-semibold mb-4">Analyse des miniatures performantes</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysis.thumbnails_analysis.map((thumbnail, index) => (
              <div key={index} className="bg-gray-50 rounded-lg overflow-hidden">
                <img
                  src={thumbnail.thumbnail_url}
                  alt={thumbnail.title}
                  className="w-full h-48 object-cover"
                />
                <div className="p-4">
                  <h5 className="font-medium mb-2 line-clamp-2">{thumbnail.title}</h5>
                  <div className="text-sm text-gray-600">
                    <p>Vues: {thumbnail.views.toLocaleString()}</p>
                    <div className="mt-2">
                      <p>Éléments détectés:</p>
                      <ul className="list-disc pl-5 mt-1">
                        {thumbnail.elements.has_text && (
                          <li>Texte présent</li>
                        )}
                        {thumbnail.elements.has_face && (
                          <li>Visage présent</li>
                        )}
                        {thumbnail.elements.has_bright_colors && (
                          <li>Couleurs vives</li>
                        )}
                        <li>Composition: {thumbnail.elements.composition}</li>
                      </ul>
                    </div>
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

export default ThumbnailAnalyzer;
