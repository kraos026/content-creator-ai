import axios from 'axios'
import { useAuthStore } from '../store'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur pour ajouter le token d'authentification
client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// API Authentication
export const auth = {
  register: async (data: {
    username: string
    email: string
    password: string
    contentNiche?: string
    preferredPlatforms?: string[]
    postingFrequency?: string
  }) => {
    const response = await client.post('/auth/register', data)
    return response.data
  },

  login: async (data: { email: string; password: string }) => {
    const response = await client.post('/auth/login', data)
    return response.data
  },

  getProfile: async () => {
    const response = await client.get('/auth/profile')
    return response.data
  },

  updateProfile: async (data: any) => {
    const response = await client.put('/auth/profile', data)
    return response.data
  },
}

// API Trends
export const trends = {
  analyze: async (data: { platforms: string[] }) => {
    const response = await client.post('/trends/analyze', data)
    return response.data
  },

  getHistory: async (params: {
    platform?: string
    category?: string
    days?: number
  }) => {
    const response = await client.get('/trends/history', { params })
    return response.data
  },

  getTop: async (params: { platform?: string; limit?: number }) => {
    const response = await client.get('/trends/top', { params })
    return response.data
  },

  getRecommendations: async () => {
    const response = await client.get('/trends/recommendations')
    return response.data
  },
}

// API Content
export const content = {
  generate: async (data: { trends: any[]; count?: number }) => {
    const response = await client.post('/content/generate', data)
    return response.data
  },

  getIdeas: async (params: { platform?: string; used?: boolean }) => {
    const response = await client.get('/content/ideas', { params })
    return response.data
  },

  updateIdea: async (id: number, data: any) => {
    const response = await client.put(`/content/ideas/${id}`, data)
    return response.data
  },

  regenerateThumbnail: async (id: number) => {
    const response = await client.post(`/content/ideas/${id}/thumbnail`)
    return response.data
  },

  regenerateScript: async (id: number) => {
    const response = await client.post(`/content/ideas/${id}/script`)
    return response.data
  },
}

export default client
