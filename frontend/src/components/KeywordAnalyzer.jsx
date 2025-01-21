import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const KeywordAnalyzer = () => {
  const [keywords, setKeywords] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!keywords.trim()) {
      toast.error('Veuillez entrer des mots-clés');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/youtube/keywords/analyze', {
        keywords: keywords.split(',').map(k => k.trim())
      });
      setAnalysis(response.data);
      toast.success('Analyse des mots-clés terminée');
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de l\'analyse des mots-clés');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4">Analyse de mots-clés</h3>
      
      <div className="mb-4">
        <textarea
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Entrez vos mots-clés séparés par des virgules"
          className="w-full p-2 border rounded-md h-24"
        />
      </div>

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
      >
        {loading ? 'Analyse en cours...' : 'Analyser'}
      </button>

      {analysis && (
        <div className="mt-6">
          <h4 className="font-semibold mb-2">Résultats de l'analyse</h4>
          <div className="space-y-4">
            {analysis.keywords_analysis.map((keyword, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium">{keyword.keyword}</h5>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div>Nombre de vidéos: {keyword.video_count}</div>
                  <div>Vues moyennes: {Math.round(keyword.avg_views)}</div>
                  <div>Engagement moyen: {Math.round(keyword.avg_engagement)}</div>
                  <div>Niveau de concurrence: {keyword.competition_level}</div>
                  <div>Score potentiel: {keyword.potential_score.toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>

          {analysis.recommendations.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Recommandations</h4>
              <ul className="list-disc pl-5">
                {analysis.recommendations.map((rec, index) => (
                  <li key={index} className="text-gray-700">{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KeywordAnalyzer;
