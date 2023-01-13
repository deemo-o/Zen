from dataclasses import dataclass

@dataclass
class Loop:
    NONE = "NONE"
    CURRENT = "CURRENT"
    QUEUE = "QUEUE"

    TYPES = [NONE, CURRENT, QUEUE]