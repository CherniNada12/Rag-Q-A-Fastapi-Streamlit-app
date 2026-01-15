# src/modules/generation.py
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict
import logging
from .config import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ResponseGenerator:
    """Génération de réponses avec LLM pour le système RAG"""
    
    def __init__(self, model_name: str = None, use_openai: bool = False):
        self.model_name = model_name or config.LLM_MODEL
        self.use_openai = use_openai
        
        if use_openai and config.OPENAI_API_KEY:
            self._init_openai()
        else:
            self._init_local_model()
    
    def _init_openai(self):
        """Initialise le client OpenAI"""
        try:
            import openai
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai.OpenAI()
            logger.info("Client OpenAI initialisé")
        except Exception as e:
            logger.error(f"Erreur OpenAI : {e}")
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialise un modèle local"""
        logger.info(f"Chargement du modèle local : {self.model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=200,
                temperature=0.7
            )
            logger.info("Modèle local chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur chargement modèle : {e}")
            raise
    
    def generate_answer(
        self, 
        query: str, 
        context_chunks: List[Dict],
        max_chunks: int = 3,
        max_chars_per_chunk: int = 1000
    ) -> Dict[str, any]:
        """
        Génère une réponse basée sur le contexte

        Args:
            query: Question de l'utilisateur
            context_chunks: Chunks récupérés par FAISS
            max_chunks: Nombre maximum de chunks à inclure dans le prompt
            max_chars_per_chunk: Limite de caractères par chunk pour éviter d'exploser le prompt

        Returns:
            Dict avec 'answer', 'sources' et 'context_used'
        """
        # Limiter le nombre de chunks
        limited_chunks = context_chunks[:max_chunks]

        # Construire le contexte (tronquer si nécessaire)
        context = "\n\n".join([
            f"[Document: {chunk['document_name']}]\n{chunk['content'][:max_chars_per_chunk]}"
            for chunk in limited_chunks
        ])

        # Construire le prompt
        prompt = self._build_prompt(query, context)

        logger.debug(f"Prompt envoyé au modèle:\n{prompt}")

        # Générer la réponse
        if self.use_openai and hasattr(self, 'client'):
            answer = self._generate_with_openai(prompt)
        else:
            answer = self._generate_with_local(prompt)

        # Retour structuré
        return {
            'answer': answer,
            'sources': [
                {
                    'document': chunk['document_name'],
                    'chunk_id': chunk['chunk_id'],
                    'score': chunk.get('score', 0)
                }
                for chunk in limited_chunks
            ],
            'context_used': len(limited_chunks)
        }
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Construit le prompt pour le LLM"""
        return (
            f"Contexte :\n{context}\n\n"
            f"Question : {query}\n\n"
            "Réponds uniquement en te basant sur le contexte fourni. "
            "Si la réponse n'est pas dans le contexte, dis-le clairement.\n"
            "Réponse :"
        )
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Génère avec OpenAI GPT"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui répond aux questions basées sur des documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Erreur OpenAI : {e}")
            return "Erreur lors de la génération de la réponse."
    
    def _generate_with_local(self, prompt: str) -> str:
        """Génère avec un modèle local (GPT-2 par défaut)"""
        try:
            result = self.generator(prompt)[0]['generated_text']
            # Extraire seulement la nouvelle génération
            answer = result.replace(prompt, "").strip()
            return answer
        except Exception as e:
            logger.error(f"Erreur génération locale : {e}")
            return "Erreur lors de la génération de la réponse."
