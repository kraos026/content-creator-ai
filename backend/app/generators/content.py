from typing import Dict, List, Optional
import random
from datetime import datetime

class ContentGenerator:
    def __init__(self):
        self.hook_templates = [
            "Vous ne croirez jamais ce qui arrive quand {action}...",
            "Le secret pour {goal} enfin révélé !",
            "Comment {action} en seulement {timeframe}",
            "3 astuces pour {goal} comme un pro",
            "{number} erreurs à éviter quand vous {action}",
        ]
        
        self.cta_templates = [
            "👉 Suivez-moi pour plus de {topic}",
            "❤️ Likez si vous aussi vous {action}",
            "💬 Commentez votre {topic} préféré(e)",
            "🔔 Activez les notifications pour ne rien rater",
            "⬇️ Plus d'infos dans les commentaires",
        ]
    
    def generate_content_brief(self, topic: str, platform: str, content_type: str) -> Dict:
        """Génère un brief détaillé pour la création de contenu."""
        hook = self._generate_hook(topic, content_type)
        structure = self._generate_structure(content_type)
        cta = self._generate_cta(topic)
        
        return {
            'hook': hook,
            'structure': structure,
            'cta': cta,
            'optimal_length': self._get_optimal_length(platform, content_type),
            'key_elements': self._get_key_elements(platform, content_type),
            'content_tips': self._generate_content_tips(platform, content_type)
        }
    
    def _generate_hook(self, topic: str, content_type: str) -> str:
        """Génère un hook accrocheur pour le contenu."""
        template = random.choice(self.hook_templates)
        
        # Personnaliser les variables selon le type de contenu
        if content_type == 'tutorial':
            return template.format(
                action=f"vous {topic.lower()}",
                goal=f"maîtriser {topic.lower()}",
                timeframe="5 minutes",
                number="5"
            )
        elif content_type == 'review':
            return template.format(
                action=f"vous utilisez {topic.lower()}",
                goal=f"choisir le meilleur {topic.lower()}",
                timeframe="24 heures",
                number="3"
            )
        else:
            return template.format(
                action=topic.lower(),
                goal=topic.lower(),
                timeframe="une semaine",
                number="7"
            )
    
    def _generate_structure(self, content_type: str) -> List[Dict]:
        """Génère une structure de contenu optimisée."""
        structures = {
            'tutorial': [
                {'section': 'Introduction', 'duration': '0:00-0:15', 'key_points': ['Problème', 'Solution promise']},
                {'section': 'Contexte', 'duration': '0:15-0:30', 'key_points': ['Pourquoi c\'est important']},
                {'section': 'Étapes', 'duration': '0:30-2:00', 'key_points': ['3-5 étapes clés']},
                {'section': 'Résultats', 'duration': '2:00-2:30', 'key_points': ['Démonstration']},
                {'section': 'Conclusion', 'duration': '2:30-3:00', 'key_points': ['Récapitulatif', 'Call-to-action']}
            ],
            'review': [
                {'section': 'Hook', 'duration': '0:00-0:15', 'key_points': ['Teaser du verdict']},
                {'section': 'Présentation', 'duration': '0:15-0:45', 'key_points': ['Caractéristiques', 'Prix']},
                {'section': 'Tests', 'duration': '0:45-2:00', 'key_points': ['Démonstration', 'Comparaison']},
                {'section': 'Verdict', 'duration': '2:00-2:30', 'key_points': ['Pour', 'Contre']},
                {'section': 'Recommandation', 'duration': '2:30-3:00', 'key_points': ['Pour qui?', 'Call-to-action']}
            ],
            'story': [
                {'section': 'Hook', 'duration': '0:00-0:15', 'key_points': ['Moment fort']},
                {'section': 'Contexte', 'duration': '0:15-0:45', 'key_points': ['Situation initiale']},
                {'section': 'Développement', 'duration': '0:45-2:00', 'key_points': ['Péripéties']},
                {'section': 'Climax', 'duration': '2:00-2:30', 'key_points': ['Moment décisif']},
                {'section': 'Conclusion', 'duration': '2:30-3:00', 'key_points': ['Leçon', 'Call-to-action']}
            ]
        }
        
        return structures.get(content_type, structures['story'])
    
    def _generate_cta(self, topic: str) -> str:
        """Génère un call-to-action engageant."""
        template = random.choice(self.cta_templates)
        return template.format(
            topic=topic.lower(),
            action=f"aimez {topic.lower()}"
        )
    
    def _get_optimal_length(self, platform: str, content_type: str) -> Dict:
        """Retourne la durée optimale selon la plateforme et le type de contenu."""
        lengths = {
            'youtube': {
                'tutorial': {'min': 180, 'max': 600, 'optimal': 300},
                'review': {'min': 300, 'max': 900, 'optimal': 480},
                'story': {'min': 180, 'max': 420, 'optimal': 240}
            },
            'tiktok': {
                'tutorial': {'min': 30, 'max': 60, 'optimal': 45},
                'review': {'min': 45, 'max': 90, 'optimal': 60},
                'story': {'min': 30, 'max': 60, 'optimal': 45}
            },
            'instagram': {
                'tutorial': {'min': 30, 'max': 60, 'optimal': 45},
                'review': {'min': 45, 'max': 90, 'optimal': 60},
                'story': {'min': 15, 'max': 45, 'optimal': 30}
            }
        }
        
        return lengths.get(platform, {}).get(content_type, {'min': 60, 'max': 180, 'optimal': 90})
    
    def _get_key_elements(self, platform: str, content_type: str) -> List[str]:
        """Retourne les éléments clés à inclure selon la plateforme et le type."""
        elements = {
            'youtube': [
                'Miniature accrocheuse',
                'Introduction < 15 secondes',
                'Chapitres dans la description',
                'Cards et end screens',
                'Description détaillée avec timestamps'
            ],
            'tiktok': [
                'Hook dans les 3 premières secondes',
                'Musique tendance',
                'Texte à l\'écran',
                'Transitions dynamiques',
                'Hashtags pertinents'
            ],
            'instagram': [
                'Image de couverture attrayante',
                'Sous-titres',
                'Effets visuels',
                'Story highlights',
                'Bio link'
            ]
        }
        
        return elements.get(platform, ['Hook', 'Contenu', 'Call-to-action'])
    
    def _generate_content_tips(self, platform: str, content_type: str) -> List[str]:
        """Génère des conseils spécifiques pour optimiser le contenu."""
        tips = {
            'youtube': {
                'tutorial': [
                    'Commencez par le résultat final',
                    'Montrez les étapes clairement',
                    'Ajoutez des timestamps dans la description',
                    'Incluez des ressources complémentaires',
                    'Terminez par une démonstration'
                ],
                'review': [
                    'Montrez le produit sous tous les angles',
                    'Comparez avec la concurrence',
                    'Testez en conditions réelles',
                    'Donnez un avis honnête',
                    'Précisez le rapport qualité/prix'
                ]
            },
            'tiktok': {
                'tutorial': [
                    'Gardez un rythme rapide',
                    'Utilisez des transitions créatives',
                    'Ajoutez du texte explicatif',
                    'Synchronisez avec la musique',
                    'Terminez par un before/after'
                ],
                'review': [
                    'Commencez par le verdict',
                    'Utilisez des effets pour les points clés',
                    'Montrez les tests en accéléré',
                    'Ajoutez des réactions authentiques',
                    'Terminez par une note sur 10'
                ]
            }
        }
        
        return tips.get(platform, {}).get(content_type, [
            'Créez un hook accrocheur',
            'Gardez un rythme dynamique',
            'Ajoutez des éléments visuels',
            'Interagissez avec votre audience',
            'Terminez par un call-to-action fort'
        ])
