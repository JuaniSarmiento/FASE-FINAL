from enum import Enum

class MessageRole(str, Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    SYSTEM = "system"
