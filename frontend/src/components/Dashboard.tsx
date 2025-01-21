import React from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { trends, content } from '../api/client'
import { useAuthStore, useTrendStore, useContentStore } from '../store'
import {
  ChartBarIcon,
  VideoCameraIcon,
  RocketLaunchIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'

const Dashboard: React.FC = () => {
  const user = useAuthStore((state) => state.user)
  const setTrends = useTrendStore((state) => state.setTrends)
  const setIdeas = useContentStore((state) => state.setIdeas)

  // Récupération des tendances
  const { data: trendData } = useQuery({
    queryKey: ['trends'],
    queryFn: () => trends.getRecommendations(),
    onSuccess: (data) => setTrends(data.recommendations),
  })

  // Récupération des idées de contenu
  const { data: contentData } = useQuery({
    queryKey: ['content'],
    queryFn: () => content.getIdeas({}),
    onSuccess: (data) => setIdeas(data),
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Bonjour, {user?.username} 👋
          </h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Statistiques */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Tendances Actives"
            value={trendData?.recommendations.length || 0}
            icon={ChartBarIcon}
            color="bg-blue-500"
          />
          <StatsCard
            title="Idées Générées"
            value={contentData?.length || 0}
            icon={SparklesIcon}
            color="bg-purple-500"
          />
          <StatsCard
            title="Vidéos Publiées"
            value={user?.totalVideos || 0}
            icon={VideoCameraIcon}
            color="bg-green-500"
          />
          <StatsCard
            title="Score d'Engagement"
            value={user?.averageEngagementRate?.toFixed(1) || 0}
            icon={RocketLaunchIcon}
            color="bg-pink-500"
            suffix="%"
          />
        </div>

        {/* Contenu Principal */}
        <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
          {/* Tendances */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">
                  Tendances Recommandées
                </h2>
                <button className="text-sm text-primary-600 hover:text-primary-700">
                  Voir tout
                </button>
              </div>
              <div className="mt-4 space-y-4">
                {trendData?.recommendations.slice(0, 5).map((trend: any) => (
                  <TrendCard key={trend.id} trend={trend} />
                ))}
              </div>
            </div>
          </motion.div>

          {/* Idées de Contenu */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">
                  Dernières Idées
                </h2>
                <button className="text-sm text-primary-600 hover:text-primary-700">
                  Voir tout
                </button>
              </div>
              <div className="mt-4 space-y-4">
                {contentData?.slice(0, 5).map((idea: any) => (
                  <IdeaCard key={idea.id} idea={idea} />
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}

interface StatsCardProps {
  title: string
  value: number | string
  icon: React.ComponentType<any>
  color: string
  suffix?: string
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  icon: Icon,
  color,
  suffix = '',
}) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-white overflow-hidden shadow rounded-lg"
  >
    <div className="p-5">
      <div className="flex items-center">
        <div className={`${color} rounded-md p-3`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-5">
          <p className="text-sm font-medium text-gray-500 truncate">{title}</p>
          <p className="mt-1 text-3xl font-semibold text-gray-900">
            {value}
            {suffix}
          </p>
        </div>
      </div>
    </div>
  </motion.div>
)

interface TrendCardProps {
  trend: any
}

const TrendCard: React.FC<TrendCardProps> = ({ trend }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className="p-4 bg-gray-50 rounded-lg"
  >
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-sm font-medium text-gray-900">{trend.keyword}</h3>
        <p className="text-sm text-gray-500">{trend.platform}</p>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-gray-900">
          {trend.engagement.toLocaleString()} interactions
        </p>
        <p
          className={`text-sm ${
            trend.growthRate > 0 ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {trend.growthRate > 0 ? '+' : ''}
          {trend.growthRate.toFixed(1)}%
        </p>
      </div>
    </div>
  </motion.div>
)

interface IdeaCardProps {
  idea: any
}

const IdeaCard: React.FC<IdeaCardProps> = ({ idea }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className="p-4 bg-gray-50 rounded-lg"
  >
    <div className="flex items-center space-x-4">
      <div className="flex-shrink-0">
        <img
          src={idea.thumbnailUrl}
          alt=""
          className="h-12 w-12 rounded object-cover"
        />
      </div>
      <div className="flex-1">
        <h3 className="text-sm font-medium text-gray-900">{idea.title}</h3>
        <p className="text-sm text-gray-500">{idea.description}</p>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-gray-900">
          {idea.estimatedVirality * 100}% viral
        </p>
        <p className="text-sm text-gray-500">{idea.targetPlatform}</p>
      </div>
    </div>
  </motion.div>
)

export default Dashboard
