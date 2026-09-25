from enum import Enum, auto

class CatState(Enum):
    IDLE = auto()
    WALK_LEFT = auto()
    WALK_RIGHT = auto()
    SLEEP = auto()
    SIT = auto()
    JUMP = auto()
    FALL = auto()
    LAND = auto()
    CHASE_CURSOR = auto()
    DRAGGED = auto()
    HAPPY = auto()
    ANGRY = auto()
