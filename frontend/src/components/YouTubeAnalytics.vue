<template>
  <div class="youtube-analytics">
    <h2>YouTube Analytics</h2>
    
    <!-- Tendances -->
    <div class="section">
      <h3>Tendances YouTube</h3>
      <button @click="getTrends" :disabled="loadingTrends">
        {{ loadingTrends ? 'Chargement...' : 'Voir les tendances' }}
      </button>
      <div v-if="trends.length" class="trends-grid">
        <div v-for="video in trends" :key="video.id" class="trend-card">
          <h4>{{ video.title }}</h4>
          <p>Vues: {{ video.views }}</p>
          <p>Engagement: {{ video.engagementRate }}%</p>
        </div>
      </div>
    </div>

    <!-- Analyse de vidéo -->
    <div class="section">
      <h3>Analyser une vidéo</h3>
      <input v-model="videoId" placeholder="ID de la vidéo YouTube">
      <button @click="analyzeVideo" :disabled="loadingVideo">
        {{ loadingVideo ? 'Analyse...' : 'Analyser' }}
      </button>
      <div v-if="videoAnalysis" class="analysis-card">
        <h4>Résultats de l'analyse</h4>
        <pre>{{ JSON.stringify(videoAnalysis, null, 2) }}</pre>
      </div>
    </div>

    <!-- Analyse de chaîne -->
    <div class="section">
      <h3>Analyser une chaîne</h3>
      <input v-model="channelId" placeholder="ID de la chaîne YouTube">
      <button @click="analyzeChannel" :disabled="loadingChannel">
        {{ loadingChannel ? 'Analyse...' : 'Analyser' }}
      </button>
      <div v-if="channelAnalysis" class="analysis-card">
        <h4>Analyse de la chaîne</h4>
        <pre>{{ JSON.stringify(channelAnalysis, null, 2) }}</pre>
      </div>
    </div>

    <!-- Suggestions de contenu -->
    <div class="section">
      <h3>Suggestions de contenu</h3>
      <select v-model="category">
        <option value="general">Général</option>
        <option value="gaming">Gaming</option>
        <option value="education">Education</option>
        <option value="entertainment">Divertissement</option>
      </select>
      <button @click="getSuggestions" :disabled="loadingSuggestions">
        {{ loadingSuggestions ? 'Génération...' : 'Obtenir des suggestions' }}
      </button>
      <div v-if="suggestions.length" class="suggestions-list">
        <div v-for="(suggestion, index) in suggestions" :key="index" class="suggestion-card">
          <p>{{ suggestion }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'YouTubeAnalytics',
  data() {
    return {
      trends: [],
      videoId: '',
      channelId: '',
      category: 'general',
      videoAnalysis: null,
      channelAnalysis: null,
      suggestions: [],
      loadingTrends: false,
      loadingVideo: false,
      loadingChannel: false,
      loadingSuggestions: false
    }
  },
  methods: {
    async getTrends() {
      this.loadingTrends = true;
      try {
        const response = await axios.get('/api/youtube/trending');
        this.trends = response.data;
      } catch (error) {
        console.error('Erreur lors de la récupération des tendances:', error);
      } finally {
        this.loadingTrends = false;
      }
    },
    async analyzeVideo() {
      if (!this.videoId) return;
      this.loadingVideo = true;
      try {
        const response = await axios.get(`/api/youtube/analyze/video/${this.videoId}`);
        this.videoAnalysis = response.data;
      } catch (error) {
        console.error('Erreur lors de l\'analyse de la vidéo:', error);
      } finally {
        this.loadingVideo = false;
      }
    },
    async analyzeChannel() {
      if (!this.channelId) return;
      this.loadingChannel = true;
      try {
        const response = await axios.get(`/api/youtube/analyze/channel/${this.channelId}`);
        this.channelAnalysis = response.data;
      } catch (error) {
        console.error('Erreur lors de l\'analyse de la chaîne:', error);
      } finally {
        this.loadingChannel = false;
      }
    },
    async getSuggestions() {
      this.loadingSuggestions = true;
      try {
        const response = await axios.get(`/api/youtube/suggestions?category=${this.category}`);
        this.suggestions = response.data;
      } catch (error) {
        console.error('Erreur lors de la récupération des suggestions:', error);
      } finally {
        this.loadingSuggestions = false;
      }
    }
  }
}
</script>

<style scoped>
.youtube-analytics {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h2 {
  color: #ff0000;
  text-align: center;
  margin-bottom: 30px;
}

h3 {
  color: #333;
  margin-bottom: 15px;
}

.trends-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.trend-card {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.analysis-card {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  overflow-x: auto;
}

.suggestions-list {
  margin-top: 20px;
}

.suggestion-card {
  padding: 10px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

button {
  background: #ff0000;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

input, select {
  padding: 8px;
  margin-right: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
