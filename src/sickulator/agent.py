import pygame as pg
from enum import Enum
vec = pg.math.Vector2

class HealthState(Enum):
    HEALTHY = 0
    INFECTED = 1
    IMMUNE = 2
    DEAD = 3


class Agent(pg.sprite.Sprite):
    def __init__(self,game,x,y,health_state=HealthState.HEALTHY):
        self.pos = vec(x,y)
        self.game = game
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.birth_tick = game.clock.get_ticks()
        self.health_state = health_state



    

