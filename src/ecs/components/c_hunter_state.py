from enum import Enum

import pygame


class CHunterState:
    def __init__(self, init_pos:pygame.Vector2) -> None:
        self.state = HunterState.IDLE
        self.init_pos = init_pos

class HunterState(Enum):
    IDLE = 0
    CHASE = 1
    RETURN = 2