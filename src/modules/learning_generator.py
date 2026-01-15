"""
Générateur de réponses spécialisé pour l'assistant pédagogique
"""
from typing import List, Dict
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from .config import config
from .learning_config import learning_config

logger = logging.getLogger(__name__)

class LearningResponseGenerator:
    """Générateur de réponses pédagogiques adaptatif"""
    
    def __init__(self, model_name: str = None, use_openai: bool = False):
        self.model_name = model_name or config.LLM_MODEL
        self.use_openai = use_openai
        
        if use_openai and config.OPENAI_API_KEY:
            self._init_openai()
        else:
            self._init_local_model()
    
    def _init_openai(self):
        """Initialise OpenAI"""
        try:
            import openai
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai.OpenAI()
            logger.info("✅ Client OpenAI initialisé")
        except Exception as e:
            logger.error(f"Erreur OpenAI : {e}")
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialise un modèle local"""
        logger.info(f"Chargement du modèle : {self.model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=300,
                temperature=0.7
            )
            logger.info("✅ Modèle local chargé")
        except Exception as e:
            logger.error(f"Erreur chargement : {e}")
            raise
    
    def generate_pedagogical_answer(
        self,
        question: str,
        context_chunks: List[Dict],
        learning_level: str = 'intermediate',
        max_chunks: int = 5
    ) -> Dict[str, any]:
        """
        Génère une réponse pédagogique adaptée au niveau
        
        Args:
            question: Question de l'étudiant
            context_chunks: Chunks récupérés
            learning_level: Niveau (beginner/intermediate/advanced)
            max_chunks: Nombre max de chunks
            
        Returns:
            Dict avec answer, sources, question_type, suggestions
        """
        logger.info(f"📚 Génération pédagogique (niveau: {learning_level})")
        
        if not context_chunks:
            return self._handle_no_context(question)
        
        # Détecter le type de question
        question_type = learning_config.detect_question_type(question)
        logger.info(f"Type de question détecté : {question_type}")
        
        # Limiter et formater le contexte
        limited_chunks = context_chunks[:max_chunks]
        context = self._format_educational_context(limited_chunks)
        
        # Construire le prompt pédagogique
        prompt = self._build_pedagogical_prompt(
            question, 
            context, 
            learning_level,
            question_type
        )
        
        # Générer la réponse
        if self.use_openai and hasattr(self, 'client'):
            answer = self._generate_with_openai_pedagogical(prompt, learning_level)
        else:
            answer = self._generate_with_local(prompt)
        
        # Ajouter des suggestions de suivi
        suggestions = self._get_follow_up_suggestions(question_type)
        
        return {
            'answer': answer,
            'sources': self._format_sources(limited_chunks),
            'context_used': len(limited_chunks),
            'question_type': question_type,
            'learning_level': learning_level,
            'follow_up_suggestions': suggestions
        }
    
    def _format_educational_context(self, chunks: List[Dict]) -> str:
        """Formate le contexte de manière pédagogique"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            # Extraire les métadonnées pédagogiques si disponibles
            doc_name = chunk.get('document_name', 'Document inconnu')
            content = chunk.get('content', '')
            
            # Formater avec numérotation claire
            context_parts.append(
                f"[Source {i} - {doc_name}]\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_pedagogical_prompt(
        self,
        question: str,
        context: str,
        level: str,
        question_type: str
    ) -> str:
        """Construit un prompt pédagogique adapté"""
        
        # Obtenir le template du niveau
        base_prompt = learning_config.LEARNING_PROMPTS.get(
            level, 
            learning_config.LEARNING_PROMPTS['intermediate']
        )
        
        # Ajouter des instructions spécifiques selon le type
        type_instructions = {
            'definition': "\n- Commence par une définition claire\n- Donne les caractéristiques principales\n- Explique l'importance",
            'explanation': "\n- Explique le principe de base\n- Décris le fonctionnement\n- Donne les raisons sous-jacentes",
            'example': "\n- Fournis 2-3 exemples concrets\n- Illustre avec des cas pratiques\n- Montre l'application",
            'comparison': "\n- Compare les concepts point par point\n- Souligne similitudes et différences\n- Indique quand utiliser chacun",
            'procedure': "\n- Présente les étapes de manière ordonnée\n- Explique chaque étape\n- Donne des conseils pratiques"
        }
        
        specific_instructions = type_instructions.get(question_type, "")
        
        # Assembler le prompt complet
        full_prompt = base_prompt.format(
            context=context,
            question=question
        ) + specific_instructions
        
        return full_prompt
    
    def _generate_with_openai_pedagogical(self, prompt: str, level: str) -> str:
        """Génère avec OpenAI en mode pédagogique"""
        try:
            system_messages = {
                'beginner': "Tu es un professeur patient qui explique simplement aux débutants.",
                'intermediate': "Tu es un professeur qui guide les étudiants vers une compréhension approfondie.",
                'advanced': "Tu es un expert académique qui partage des connaissances avancées."
            }
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_messages.get(level, system_messages['intermediate'])},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Erreur OpenAI : {e}")
            return self._create_extractive_answer_educational(prompt)
    
    def _generate_with_local(self, prompt: str) -> str:
        """Génère avec modèle local"""
        try:
            result = self.generator(prompt, max_length=500)[0]['generated_text']
            # Extraire seulement la réponse générée
            answer = result.replace(prompt, "").strip()
            
            if len(answer) < 30:
                return self._create_extractive_answer_educational(prompt)
            
            return answer
        except Exception as e:
            logger.error(f"Erreur génération : {e}")
            return self._create_extractive_answer_educational(prompt)
    
    def _create_extractive_answer_educational(self, context: str) -> str:
        """Crée une réponse extractive éducative"""
        # Extraire les phrases les plus pertinentes
        lines = context.split('\n')
        relevant_lines = [l for l in lines if l.strip() and not l.startswith('[')]
        
        if relevant_lines:
            return f"D'après le cours :\n\n" + "\n".join(relevant_lines[:5])
        return "Les informations demandées ne sont pas disponibles dans le cours."
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Formate les sources de manière éducative"""
        return [
            {
                'document': chunk.get('document_name', 'Inconnu'),
                'chunk_id': chunk.get('chunk_id', ''),
                'score': chunk.get('score', 0),
                'page': chunk.get('page_number', 'N/A'),
                'topic': chunk.get('topic', 'Général')
            }
            for chunk in chunks
        ]
    
    def _get_follow_up_suggestions(self, question_type: str) -> List[str]:
        """Obtient des suggestions de questions de suivi"""
        suggestions = learning_config.FOLLOW_UP_SUGGESTIONS.get(
            question_type,
            [
                "Voulez-vous plus de détails ?",
                "Souhaitez-vous voir un exemple ?",
                "Puis-je clarifier un point ?"
            ]
        )
        return suggestions[:3]  # Limiter à 3 suggestions
    
    def _handle_no_context(self, question: str) -> Dict:
        """Gère le cas où aucun contexte n'est trouvé"""
        return {
            'answer': (
                "Je n'ai pas trouvé d'information pertinente dans le cours pour répondre à cette question. "
                "Essayez de reformuler votre question ou vérifiez que le sujet est couvert dans les documents fournis."
            ),
            'sources': [],
            'context_used': 0,
            'question_type': 'general',
            'learning_level': 'intermediate',
            'follow_up_suggestions': [
                "Reformulez votre question",
                "Vérifiez l'orthographe",
                "Précisez le sujet"
            ]
        }