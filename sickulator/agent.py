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
    """
    An individual agent from the simulation

    Arguments:

    game -- Simulation object the agent exists in
    family -- integer id of family this agent belongs to
    x, y -- initial position of agent
    health_state -- HealthState value

    Class Variables:

    health_counts -- Array which keeps track of how many agents of each health state exist
                     Order is [healthy,infected,immune,dead] (same as HealthState enum values)

    """

    health_counts = []

    def __init__(self, game, family, x, y, health_state=HealthState.HEALTHY):
        self._pos = vec(x,y)
        self.game = game
        self.groups = game.all_sprites
        self.family = family
        pg.sprite.Sprite.__init__(self, self.groups)
        self._birth_tick = game.clock.get_ticks()
        self._health_state = health_state
        Agent.health_counts[health_state.value] += 1

    @property
    def health_state(self):
        return self._health_state
    
    @health_state.setter
    def health_state(self, hs : HealthState):
        Agent.health_counts[self.health_state.value] -= 1
        Agent.health_counts[hs.value] += 1
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
    home -- integer id of building family is assigned to

    Class Variables:

    count -- number of instances of family, used for generating id
    """
    count = 0

    def __init__(self, game, home):
        self.id = Family.count
        self.game = game
        self.agents = []
        self.work = 0
        self.home
        Family.count += 1
    
    def add_agent(self, agent : Agent):
        """Add agent to a family's agents list"""
        self.agents.append(agent)

def generate_days(count = 1):
    """
    Return a list of tuples containing which buildings an agent will visit and how long they will spend.
    
    First entry of each tuple contains numbers of buildings the agent will visit
    
    Second entry contains the proportion of their day for each building, with the first
    and last entry containing the amount of time spent at home in the morning and evening
    respectively
    """
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
        #  first and last entry are how long they spend in home at start and end of each day
        #  times[1:-2] are the proportion of the day devoted to each building
        #  Sometimes travel time will exceed the proportion they should spend
        #  in this case, agent redirects path mid-travel to next target
        times = (y:=rng.random(i+2))/np.sum(y) #  this line just generates proportions from a uniform distribution
        agent_visits.append((buildings[j:j+i], times))
        j += i
    return agent_visits


