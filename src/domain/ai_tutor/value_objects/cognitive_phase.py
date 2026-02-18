from enum import Enum

class CognitivePhase(str, Enum):
    ENGAGEMENT = "engagement"
    EXPLORATION = "exploration"
    EXPLANATION = "explanation"
    ELABORATION = "elaboration"
    EVALUATION = "evaluation"
