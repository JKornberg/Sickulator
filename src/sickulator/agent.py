import pygame as pg
from enum import Enum
vec = pg.math.Vector2

class HealthState(Enum):
    HEALTHY = 0
    INFECTED = 1
    IMMUNE = 2
    DEAD = 3

class Agent(pg.sprite.Sprite):
    def __init__(self, game, family, x, y, health_state=HealthState.HEALTHY):
        self._pos = vec(x,y)
        self.game = game
        self.groups = game.all_sprites
        self.family = family
        pg.sprite.Sprite.__init__(self, self.groups)
        self._birth_tick = game.clock.get_ticks()
        self._health_state = health_state

    @property
    def health_state(self):
        return self._health_state
    
    @health_state.setter
    def health_state(self, hs : HealthState):
        self._health_state = hs

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, x, y):
        self._pos = vec(x,y)


class Family():
    """
    Represents a family unit of agents.
    
    Arguments:
    
    game -- Game object which contains all world info (clock etc)
    """
    count = 0

    def __init__(self, game):
        self.game = game
        self.agents = []
        self.work = 0
        Family.count += 1
    
    def add_agent(self, agent : Agent):
        """Add agent to a family's agents list"""
        self.agents.append(agent)

