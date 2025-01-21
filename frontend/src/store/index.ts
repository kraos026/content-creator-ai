import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  username: string
  email: string
  contentNiche: string
  preferredPlatforms: string[]
  postingFrequency: string
}

interface AuthState {
  user: User | null
  token: string | null
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
)

interface Trend {
  id: number
  platform: string
  keyword: string
  category: string
  volume: number
  engagement: number
  growthRate: number
  sentimentScore: number
  hashtags: string[]
  relatedKeywords: string[]
  peakHours: Record<string, number>
}

interface TrendState {
  trends: Trend[]
  setTrends: (trends: Trend[]) => void
  addTrend: (trend: Trend) => void
  clearTrends: () => void
}

export const useTrendStore = create<TrendState>()((set) => ({
  trends: [],
  setTrends: (trends) => set({ trends }),
  addTrend: (trend) => set((state) => ({ trends: [...state.trends, trend] })),
  clearTrends: () => set({ trends: [] }),
}))

interface ContentIdea {
  id: number
  userId: number
  title: string
  description: string
  targetPlatform: string
  estimatedVirality: number
  script: string
  thumbnailUrl: string
  musicSuggestions: any[]
  tags: string[]
  isUsed: boolean
  performanceScore: number | null
}

interface ContentState {
  ideas: ContentIdea[]
  setIdeas: (ideas: ContentIdea[]) => void
  addIdea: (idea: ContentIdea) => void
  updateIdea: (id: number, updates: Partial<ContentIdea>) => void
  removeIdea: (id: number) => void
}

export const useContentStore = create<ContentState>()((set) => ({
  ideas: [],
  setIdeas: (ideas) => set({ ideas }),
  addIdea: (idea) => set((state) => ({ ideas: [...state.ideas, idea] })),
  updateIdea: (id, updates) =>
    set((state) => ({
      ideas: state.ideas.map((idea) =>
        idea.id === id ? { ...idea, ...updates } : idea
      ),
    })),
  removeIdea: (id) =>
    set((state) => ({
      ideas: state.ideas.filter((idea) => idea.id !== id),
    })),
}))
