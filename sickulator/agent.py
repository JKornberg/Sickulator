import math
import pygame as pg
from enum import Enum
import numpy as np

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

def generate_days(count = 1):
    """Return a list of numpy arrays containing which buildings an agent will visit."""
    buildings = 9
    rng = np.random.default_rng()
    number_of_visits = rng.lognormal(1,.444,(count)) #has mean of 2
    number_of_visits[number_of_visits < 1] = 1 #minimum visits is 1
    number_of_visits = np.round(number_of_visits).astype('int16')
    buildings = rng.integers(low=0,high=buildings-1,size=np.sum(number_of_visits)) #get list of buildings for visits
    agent_visits = []
    j = 0
    #loop can be optimized, assigns buildings to visits
    for i in number_of_visits:
        agent_visits.append(buildings[j:j+i])
        j += i
    return agent_visits


