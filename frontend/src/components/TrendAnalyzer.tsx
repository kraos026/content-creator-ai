import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { trends } from '../api/client'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const TrendAnalyzer: React.FC = () => {
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all')
  const [timeRange, setTimeRange] = useState<number>(7) // jours

  const { data: historyData } = useQuery({
    queryKey: ['trends', 'history', selectedPlatform, timeRange],
    queryFn: () =>
      trends.getHistory({
        platform: selectedPlatform === 'all' ? undefined : selectedPlatform,
        days: timeRange,
      }),
  })

  const { data: topTrendsData } = useQuery({
    queryKey: ['trends', 'top', selectedPlatform],
    queryFn: () =>
      trends.getTop({
        platform: selectedPlatform === 'all' ? undefined : selectedPlatform,
        limit: 10,
      }),
  })

  // Préparation des données pour le graphique
  const chartData = {
    labels:
      historyData?.map((item: any) =>
        format(new Date(item.detected_at), 'dd MMM', { locale: fr })
      ) || [],
    datasets: [
      {
        label: 'Engagement',
        data: historyData?.map((item: any) => item.engagement) || [],
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.5)',
        tension: 0.4,
      },
      {
        label: 'Volume',
        data: historyData?.map((item: any) => item.volume) || [],
        borderColor: 'rgb(244, 63, 94)',
        backgroundColor: 'rgba(244, 63, 94, 0.5)',
        tension: 0.4,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Évolution des Tendances',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* En-tête */}
        <div className="text-center">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-gray-900"
          >
            Analyse des Tendances
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mt-4 text-xl text-gray-600"
          >
            Découvrez les tendances qui façonnent les réseaux sociaux
          </motion.p>
        </div>

        {/* Filtres */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Sélection de la plateforme */}
            <div>
              <label
                htmlFor="platform"
                className="block text-sm font-medium text-gray-700"
              >
                Plateforme
              </label>
              <select
                id="platform"
                value={selectedPlatform}
                onChange={(e) => setSelectedPlatform(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="all">Toutes les plateformes</option>
                <option value="tiktok">TikTok</option>
                <option value="youtube">YouTube</option>
                <option value="instagram">Instagram</option>
              </select>
            </div>

            {/* Sélection de la période */}
            <div>
              <label
                htmlFor="timeRange"
                className="block text-sm font-medium text-gray-700"
              >
                Période
              </label>
              <select
                id="timeRange"
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value={7}>7 derniers jours</option>
                <option value={14}>14 derniers jours</option>
                <option value={30}>30 derniers jours</option>
              </select>
            </div>
          </div>
        </div>

        {/* Graphique */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 bg-white rounded-lg shadow p-6"
        >
          <Line data={chartData} options={chartOptions} />
        </motion.div>

        {/* Top Tendances */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 bg-white rounded-lg shadow overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Top Tendances</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {topTrendsData?.map((trend: any, index: number) => (
              <TrendRow key={trend.id} trend={trend} rank={index + 1} />
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

interface TrendRowProps {
  trend: any
  rank: number
}

const TrendRow: React.FC<TrendRowProps> = ({ trend, rank }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: rank * 0.1 }}
    className="px-6 py-4 flex items-center hover:bg-gray-50"
  >
    <div className="w-8 text-lg font-bold text-gray-400">#{rank}</div>
    <div className="flex-1">
      <h3 className="text-sm font-medium text-gray-900">{trend.keyword}</h3>
      <p className="text-sm text-gray-500">{trend.platform}</p>
    </div>
    <div className="text-right">
      <p className="text-sm font-medium text-gray-900">
        {trend.engagement.toLocaleString()} interactions
      </p>
      <p
        className={`text-sm ${
          trend.growth_rate > 0 ? 'text-green-600' : 'text-red-600'
        }`}
      >
        {trend.growth_rate > 0 ? '+' : ''}
        {trend.growth_rate.toFixed(1)}%
      </p>
    </div>
  </motion.div>
)

export default TrendAnalyzer
