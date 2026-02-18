from enum import Enum

class TutorMode(str, Enum):
    SOCRATIC = "socratic"
    DIRECT = "direct"
    HINT = "hint"
