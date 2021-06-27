import math
from os import curdir
from settings import BLACK, BLUE, GREEN, PLAYER_SPEED, RED, SimulationSettings, TILESIZE, DAILY_MORTALITY_CHANCE, DAY_LENGTH
import pygame as pg
from enum import Enum
import numpy as np
from path_finder import PathFinder
from math import ceil
from buildings import building_addresses, home_addresses


vec = pg.math.Vector2


class HealthState(Enum):
    HEALTHY = 0
    INFECTED = 1
    IMMUNE = 2
    DEAD = 3


health_colors = [GREEN, RED, BLUE, BLACK]


class Agent(pg.sprite.Sprite):
    """
    An individual agent from the simulation

    Arguments:

    simulation -- Simulation object the agent exists in
    family -- integer id of family this agent belongs to
    x, y -- initial position of agent
    health_state -- HealthState value

    Class Variables:

    health_counts -- Array which keeps track of how many agents of each health state exist
                     Order is [healthy,infected,immune,dead] (same as HealthState enum values)

    """

    health_counts = [0, 0, 0, 0]

    def __init__(
        self,
        simulation,
        family,
        x,
        y,
        home_id,
        health_state=HealthState.HEALTHY,
    ):
        self.pos = vec(x,y)
        self.home = home_id
        self.simulation = simulation
        self.groups = simulation.all_sprites
        self.family = family
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(health_colors[health_state.value])
        self.rect = self.image.get_rect()
        self._birthday = simulation.day
        self._health_state = health_state
        # Update counts of
        Agent.health_counts[health_state.value] += 1
        self._inside = False
        self.schedule = []
        self.current_visit = 0
        self.time_on_current_visit = 0
        self.infected_duration = 0

    def _find_path(self, start, end):
        return self.simulation.path_finder.find_path(start, end)

    @property
    def health_state(self):
        return self._health_state

    @health_state.setter
    def health_state(self, hs: HealthState):
        Agent.health_counts[self.health_state.value] -= 1
        Agent.health_counts[hs.value] += 1
        self._health_state = hs
        self.image.fill(health_colors[hs.value])

    @property
    def inside(self):
        return self._inside

    @inside.setter
    def inside(self, val):
        self._inside = val
        if val:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

    def daily_update(self):
        if self.health_state == HealthState.INFECTED:
            if np.random.randint(0,100) < 5:
                self.health_state = HealthState.DEAD
            if self.infected_duration >= self.simulation.simulation_settings.illness_period:
                self.health_state = HealthState.IMMUNE
            else:
                self.infected_duration += 1
        self.setup_path(self)

    def setup_path(self):
        #Get current scheduled task and create path
        pass

    def update(self):
        """
        Per path in schedule:
            1. Get current step of path
            2. Move by pixels according to speed, time passed and direction towards next step
            3. If on new tile, reset position to exact tile, update current step.
            4. repeat until path is over
        """
        self.rect.center = self.pos * TILESIZE

        current_tile = vec(self.path[self.current_step][0], self.path[self.current_step][1])
        try:
            next_tile = self.path[self.current_step + 1]
        except IndexError:
            print("reached end of path")
            return

        next_tile = vec(next_tile[0],next_tile[1])
        dist = next_tile - self.pos
        v = dist * PLAYER_SPEED
        new_pos = self.pos + v * self.simulation.dt
        d1 = self.pos - next_tile
        d2 = new_pos - next_tile
        if not (ceil(d1[0]) ^ ceil(d2[0]) and ceil(d1[1]) ^ ceil(d2[1])):
            self.pos = next_tile
        else:
            self.pos = new_pos
        self.rect.center = self.pos * TILESIZE

        current_tile = vec(int(self.pos[0]), int(self.pos[1]))

        if current_tile == next_tile:
            self.current_step += 1

        if (
            self.simulation.simulation_settings.lifespan
            - (self.simulation.day - self._birthday)
        ) <= 0:
            self.health_state = HealthState.DEAD


class Family:
    """
    Represents a family unit of agents.

    Arguments:

    simulation -- simulation object which contains all world info (clock etc)
    home -- integer id of building family is assigned to

    Class Variables:

    count -- number of instances of family, used for generating id
    """

    count = 0

    def __init__(self, simulation, home):
        self.id = Family.count
        self.simulation = simulation
        self.agents = []
        self.work = 0
        self.home = home
        Family.count += 1

    def add_agent(self, agent: Agent):
        """Add agent to a family's agents list"""
        self.agents.append(agent)


def generate_schedules(agents):
    """
    Set Agent.schedule for all agents in agents list

    Args:
    agents - list of all agents to generate schedules for

    Sets schedule to a list of tuples where the first entry is a building number
    and the second entry is a proportion of the agent's day.

    Adding the proportions for an agent's day will always sum to 1
    """
    count = len(agents)
    building_ids = len(building_addresses)
    rng = np.random.default_rng()
    number_of_visits = rng.lognormal(1, 0.444, (count))  # has mean of 2
    number_of_visits[number_of_visits < 1] = 1  # minimum visits is 1
    number_of_visits = np.round(number_of_visits).astype("int16")

    # [ random(0-8) repeated for the total number of visits * 9]
    buildings = rng.integers(
        low=0, high=building_ids - 1, size=np.sum(number_of_visits)
    )  # get list of buildings for visits
    j = 0
    # loop can be optimized, assigns buildings to visits
    for agent, i in zip(agents, number_of_visits):
        #  first and last entry are how long they spend in home at start and end of each day
        #  times[1:-2] are the proportion of the day devoted to each building
        #  Sometimes travel time will exceed the proportion they should spend
        #  in this case, agent redirects path mid-travel to next target
        times = (y := rng.random(i + 2)) / np.sum(
            y
        )  #  this line just generates proportions from a uniform distribution
        visits = np.concatenate(
            (
                agent.home,
                buildings[j : j + i],
                agent.home,
            ),
            axis=None,
        )
        agent.schedule = list(zip(visits, times))
        j += i
    return
