"""Configuration pédagogique"""
class LearningAssistantConfig:
    QUESTION_TYPES = {
        'definition': ['c\'est quoi', 'définir'],
        'explanation': ['comment', 'pourquoi'],
        'example': ['exemple', 'illustrer'],
        'comparison': ['différence', 'comparer'],
        'procedure': ['étapes', 'comment faire'],
        'application': ['utiliser', 'appliquer']
    }
    
    @staticmethod
    def detect_question_type(question: str) -> str:
        question_lower = question.lower()
        for qtype, keywords in LearningAssistantConfig.QUESTION_TYPES.items():
            if any(kw in question_lower for kw in keywords):
                return qtype
        return 'general'

learning_config = LearningAssistantConfig()