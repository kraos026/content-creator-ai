import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { content } from '../api/client'
import { useContentStore } from '../store'
import toast from 'react-hot-toast'
import {
  SparklesIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  PhotoIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

const ContentGenerator: React.FC = () => {
  const [selectedTrends, setSelectedTrends] = useState<any[]>([])
  const [generating, setGenerating] = useState(false)
  const queryClient = useQueryClient()
  const addIdea = useContentStore((state) => state.addIdea)

  const generateMutation = useMutation({
    mutationFn: (data: { trends: any[]; count: number }) =>
      content.generate(data),
    onSuccess: (data) => {
      data.ideas.forEach((idea: any) => addIdea(idea))
      queryClient.invalidateQueries({ queryKey: ['content'] })
      toast.success('Nouvelles idées générées avec succès !')
      setGenerating(false)
    },
    onError: () => {
      toast.error('Erreur lors de la génération des idées')
      setGenerating(false)
    },
  })

  const handleGenerate = () => {
    if (selectedTrends.length === 0) {
      toast.error('Sélectionnez au moins une tendance')
      return
    }

    setGenerating(true)
    generateMutation.mutate({
      trends: selectedTrends,
      count: 3,
    })
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
            Générateur de Contenu AI
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mt-4 text-xl text-gray-600"
          >
            Transformez les tendances en idées de contenu viral
          </motion.p>
        </div>

        {/* Section principale */}
        <div className="mt-12">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-white shadow-xl rounded-2xl overflow-hidden"
          >
            {/* Étapes */}
            <div className="border-b border-gray-200">
              <div className="p-6">
                <h2 className="text-lg font-medium text-gray-900">
                  Processus de Génération
                </h2>
                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <ProcessStep
                    icon={SparklesIcon}
                    title="1. Sélection des Tendances"
                    description="Choisissez les tendances qui vous inspirent"
                    active={true}
                  />
                  <ProcessStep
                    icon={VideoCameraIcon}
                    title="2. Génération d'Idées"
                    description="L'IA crée des concepts uniques"
                    active={generating}
                  />
                  <ProcessStep
                    icon={DocumentTextIcon}
                    title="3. Création de Contenu"
                    description="Scripts et visuels optimisés"
                    active={false}
                  />
                </div>
              </div>
            </div>

            {/* Sélection des tendances */}
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900">
                Tendances Disponibles
              </h3>
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {/* Cartes de tendances */}
                <AnimatePresence>
                  {trends.map((trend) => (
                    <TrendCard
                      key={trend.id}
                      trend={trend}
                      selected={selectedTrends.includes(trend)}
                      onSelect={() => {
                        if (selectedTrends.includes(trend)) {
                          setSelectedTrends(
                            selectedTrends.filter((t) => t.id !== trend.id)
                          )
                        } else {
                          setSelectedTrends([...selectedTrends, trend])
                        }
                      }}
                    />
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Bouton de génération */}
            <div className="p-6 bg-gray-50">
              <div className="flex justify-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleGenerate}
                  disabled={generating || selectedTrends.length === 0}
                  className={`px-8 py-3 rounded-full text-white font-medium
                    ${
                      generating || selectedTrends.length === 0
                        ? 'bg-gray-400'
                        : 'bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600'
                    }
                    transition-all duration-200 ease-in-out`}
                >
                  {generating ? (
                    <div className="flex items-center space-x-2">
                      <SparklesIcon className="h-5 w-5 animate-spin" />
                      <span>Génération en cours...</span>
                    </div>
                  ) : (
                    'Générer des Idées'
                  )}
                </motion.button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

interface ProcessStepProps {
  icon: React.ComponentType<any>
  title: string
  description: string
  active: boolean
}

const ProcessStep: React.FC<ProcessStepProps> = ({
  icon: Icon,
  title,
  description,
  active,
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className={`p-4 rounded-lg ${
      active
        ? 'bg-gradient-to-r from-primary-50 to-secondary-50 border-2 border-primary-200'
        : 'bg-gray-50'
    }`}
  >
    <div className="flex items-center space-x-3">
      <div
        className={`p-2 rounded-full ${
          active
            ? 'bg-gradient-to-r from-primary-500 to-secondary-500'
            : 'bg-gray-200'
        }`}
      >
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div>
        <h4 className="text-sm font-medium text-gray-900">{title}</h4>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
    </div>
  </motion.div>
)

interface TrendCardProps {
  trend: any
  selected: boolean
  onSelect: () => void
}

const TrendCard: React.FC<TrendCardProps> = ({ trend, selected, onSelect }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    exit={{ opacity: 0, scale: 0.9 }}
    whileHover={{ scale: 1.02 }}
    onClick={onSelect}
    className={`p-4 rounded-lg cursor-pointer transition-all duration-200
      ${
        selected
          ? 'bg-gradient-to-r from-primary-50 to-secondary-50 border-2 border-primary-200'
          : 'bg-white border border-gray-200 hover:border-primary-200'
      }`}
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

// Données de test
const trends = [
  {
    id: 1,
    keyword: '#DanceChallenge',
    platform: 'TikTok',
    engagement: 150000,
    growthRate: 25.5,
  },
  {
    id: 2,
    keyword: 'Morning Routine',
    platform: 'YouTube',
    engagement: 85000,
    growthRate: 15.2,
  },
  {
    id: 3,
    keyword: 'Productivity Hacks',
    platform: 'Instagram',
    engagement: 95000,
    growthRate: -5.8,
  },
  // Ajoutez plus de tendances ici
]

export default ContentGenerator
