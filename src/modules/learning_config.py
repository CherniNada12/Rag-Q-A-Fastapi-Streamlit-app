"""
Configuration spécifique pour le Learning Assistant RAG
"""
from typing import Dict, List

class LearningAssistantConfig:
    """Configuration dédiée à l'assistant pédagogique"""
    
    # Types de questions pédagogiques
    QUESTION_TYPES = {
        'definition': ['c\'est quoi', 'qu\'est-ce que', 'définir', 'définition'],
        'explanation': ['comment', 'pourquoi', 'expliquer', 'fonctionnement'],
        'example': ['exemple', 'illustrer', 'cas pratique', 'démonstration'],
        'comparison': ['différence', 'comparer', 'versus', 'vs', 'distinction'],
        'procedure': ['étapes', 'procédure', 'comment faire', 'méthode'],
        'application': ['utiliser', 'appliquer', 'pratiquer', 'exercice']
    }
    
    # Formats de réponse selon le type de question
    RESPONSE_FORMATS = {
        'definition': {
            'intro': 'Selon les documents du cours :',
            'structure': ['définition', 'caractéristiques', 'importance']
        },
        'explanation': {
            'intro': 'Voici comment ça fonctionne :',
            'structure': ['principe', 'mécanisme', 'raisons']
        },
        'example': {
            'intro': 'Voici des exemples concrets :',
            'structure': ['exemple 1', 'exemple 2', 'cas pratique']
        },
        'comparison': {
            'intro': 'Comparaison des concepts :',
            'structure': ['similitudes', 'différences', 'usage']
        },
        'procedure': {
            'intro': 'Voici la procédure étape par étape :',
            'structure': ['préparation', 'étapes', 'vérification']
        },
        'application': {
            'intro': 'Application pratique :',
            'structure': ['contexte', 'méthode', 'résultat']
        }
    }
    
    # Prompts système pour différents niveaux
    LEARNING_PROMPTS = {
        'beginner': """Tu es un assistant pédagogique bienveillant pour débutants.
        
Tes réponses doivent :
- Utiliser un vocabulaire simple
- Définir tous les termes techniques
- Donner des analogies et exemples concrets
- Encourager l'apprenant
- Décomposer les concepts complexes

Contexte du cours :
{context}

Question de l'étudiant : {question}

Réponds de manière claire et pédagogique :""",
        
        'intermediate': """Tu es un assistant pédagogique pour étudiants de niveau intermédiaire.

Tes réponses doivent :
- Aller plus en profondeur
- Faire des liens entre concepts
- Donner des exemples variés
- Suggérer des pistes de réflexion

Contexte du cours :
{context}

Question de l'étudiant : {question}

Réponds de manière structurée :""",
        
        'advanced': """Tu es un assistant pédagogique pour étudiants avancés.

Tes réponses doivent :
- Être précises et techniques
- Citer les sources exactes
- Proposer des approfondissements
- Souligner les subtilités

Contexte du cours :
{context}

Question de l'étudiant : {question}

Réponds avec rigueur académique :"""
    }
    
    # Métadonnées pédagogiques à extraire
    EDUCATIONAL_METADATA = [
        'difficulty_level',  # débutant, intermédiaire, avancé
        'topic',            # sujet principal
        'subtopic',         # sous-sujet
        'learning_objective', # objectif pédagogique
        'prerequisites',    # prérequis
        'keywords'          # mots-clés
    ]
    
    # Suggestions de follow-up selon le type
    FOLLOW_UP_SUGGESTIONS = {
        'definition': [
            "Voulez-vous un exemple pratique ?",
            "Souhaitez-vous comprendre pourquoi c'est important ?",
            "Dois-je comparer avec un concept similaire ?"
        ],
        'explanation': [
            "Voulez-vous voir un cas d'application ?",
            "Puis-je détailler une étape en particulier ?",
            "Souhaitez-vous des schémas explicatifs ?"
        ],
        'example': [
            "Voulez-vous d'autres exemples ?",
            "Dois-je expliquer le principe sous-jacent ?",
            "Souhaitez-vous un exercice pratique ?"
        ]
    }
    
    @staticmethod
    def detect_question_type(question: str) -> str:
        """Détecte le type de question posée"""
        question_lower = question.lower()
        
        for qtype, keywords in LearningAssistantConfig.QUESTION_TYPES.items():
            if any(keyword in question_lower for keyword in keywords):
                return qtype
        
        return 'general'
    
    @staticmethod
    def get_learning_level(metadata: Dict) -> str:
        """Détermine le niveau d'apprentissage basé sur les métadonnées"""
        if 'difficulty_level' in metadata:
            return metadata['difficulty_level']
        return 'intermediate'  # par défaut

learning_config = LearningAssistantConfig()