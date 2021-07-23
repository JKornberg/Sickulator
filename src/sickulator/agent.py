import math
from os import curdir
from sickulator.settings import (
    BLACK,
    BLUE,
    GREEN,
    PLAYER_SPEED,
    RED,
    SimulationSettings,
    TILESIZE,
    DAILY_MORTALITY_CHANCE,
    DAY_LENGTH,
    work_building_ids,
    food_building_ids,
    social_building_ids
)
import pygame as pg
from enum import Enum
import numpy as np
from sickulator.path_finder import PathFinder
from math import ceil
from sickulator.settings import building_addresses, home_addresses
import names

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
        id,
        health_state=HealthState.HEALTHY,
        preferences=np.array([1/3,1/3,1/3]) * DAY_LENGTH
    ):
        self.id = id
        self.pos = vec(x, y)
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
        self.visit_index = 0
        self.time_on_current_visit = 0
        self.arrived = False
        self.infected_duration = 0
        self.preferences=preferences
        self.active_building = None
        self.name = names.get_full_name()

    def _find_path(self, start, end):
        return self.simulation.path_finder.find_path(start, end)

    def health_state_but_works(self):
            if self._health_state == HealthState.HEALTHY:
                return 0
            elif self._health_state == HealthState.INFECTED:
                return 1
            elif self._health_state == HealthState.IMMUNE:
                return 2
            elif self._health_state == HealthState.DEAD:
                return 3

    @property
    def birthday(self):
        return self._birthday

    @property
    def health_state(self):
        return self._health_state

    @health_state.setter
    def health_state(self, hs: HealthState):
        Agent.health_counts[self.health_state.value] -= 1
        Agent.health_counts[hs.value] += 1
        self._health_state = hs
        self.image.fill(health_colors[hs.value])
        if hs == HealthState.INFECTED:
            self.simulation.infected_today += 1
        elif hs == HealthState.DEAD:
            self.simulation.kill_agent()
            self.groups.remove(self)
            if self.active_building != None:
                self.active_building.agents.remove(self)
        elif hs == HealthState.IMMUNE:
            self.simulation.immunize_agent()

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

    def daily_update(self, firstDay = False):
        if (self.simulation.simulation_settings.lifespan - (self.simulation.day - self._birthday)) <= 0:
            self.health_state = HealthState.DEAD
        if firstDay == False:
            if self.health_state == HealthState.INFECTED:
                if np.random.rand() < self.simulation.simulation_settings.mortality/100:
                    self.health_state = HealthState.DEAD
                if (
                        self.infected_duration
                        >= self.simulation.simulation_settings.illness_period
                ):
                    self.health_state = HealthState.IMMUNE
                else:
                    self.infected_duration += 1

        self.visit_index = 0
        self.pos.x, self.pos.y = (
            home_addresses[self.home][0],
            home_addresses[self.home][1],
        )
        self.setup_path()

    def setup_path(self):
        if self.visit_index > len(self.schedule) - 1:
            return
        else:
            location_id = self.schedule[self.visit_index]
            if (
                    self.visit_index == 0
                    or self.visit_index == len(self.schedule) - 1
            ):
                destination = home_addresses[self.home]
            else:
                destination = building_addresses[location_id[0]]

            self.time_on_current_visit = 0
        self.path = self.simulation.path_finder.find_path(
            (int(self.pos.x), int(self.pos.y)), destination
        )
        if not self.path:
            self.path = [(int(self.pos.x), int(self.pos.y), "Goal")]
        self.current_step = 0
        self.distance_traveled_along_path = 0

    def update(self):
        self.rect.center = self.pos * TILESIZE

        if self.schedule and self.visit_index < len(self.schedule):
            current_visit = self.schedule[self.visit_index]
            self.time_on_current_visit += self.simulation.dt
        else:
            return

        if self.time_on_current_visit >= current_visit[1] * DAY_LENGTH:
            self.arrived = False
            if self.visit_index == 0 or self.visit_index == len(self.schedule) - 1:
                self.simulation.homes[current_visit[0]].remove_agent(self)
            else:
                self.simulation.buildings[current_visit[0]].remove_agent(self)
            if self.visit_index < len(self.schedule) - 1:
                self.visit_index += 1
                self.time_on_current_visit = 0
                self.setup_path()

        """
        1. Get current distance traveled on path
        2. Get the current tile the agent should be on given the distance traveled
        3. For example, if the path is 64 pixels (4 steps, 4 * 16 = 64), and you've traveled 16 pixels (1 step) the current tile index should be (16 / 64) * len of path - 1 = 1/4 * 4 = 1
           a. could also be, current distance traveled / 16 = 16 / 16 = 1
        """

        distance_traveled = self.time_on_current_visit * PLAYER_SPEED # pixels = seconds * (pixels / second)
        current_tile_index = math.floor(distance_traveled / TILESIZE) # constant = pixels / pixels


        if current_tile_index > len(self.path) - 1: # reached end of path
            if not self.arrived:
                self.arrived = True
                try:
                    if self.visit_index == 0 or self.visit_index == len(self.schedule) - 1:
                        self.simulation.homes[current_visit[0]].add_agent(self)
                    else:
                        self.simulation.buildings[current_visit[0]].add_agent(self)
                except Exception as e:
                    print(distance_traveled, path_distance, current_tile_index)

            return 

        # current tile based on distance traveled
        current_tile = self.path[current_tile_index]

        # reset position, could be improved since this causes slight glitches when the agent was almost at the end of the tile
        self.pos.x = current_tile[0]
        self.pos.y = current_tile[1]


        # Since we're at the start of the tile, I need to figure out how far along the tile the agent has moved. 
        # I take the distance traveld UP TO the current tile and then find the difference from the total distance
        floored_distance_traveled = current_tile_index * TILESIZE # pixels = n*pixels
        remaining_distance_traveled = distance_traveled - floored_distance_traveled # pixels = pixels - pixels


        # Then I need to check which direction to move the agent along the tile to make sure he continues moving along the path.  
        if current_tile[2] == "North":
            self.pos.y -= remaining_distance_traveled / TILESIZE
        elif current_tile[2] == "South":
            self.pos.y += remaining_distance_traveled / TILESIZE
        elif current_tile[2] == "East":
            self.pos.x +=  remaining_distance_traveled / TILESIZE
        else:
            self.pos.x -=  remaining_distance_traveled / TILESIZE


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


def gen_schedules(agents):
    '''New scheduling algorithm'''
    count = len(agents)
    rng = np.random.default_rng()
    #Work food social
    # [[2,10], [1, 7], [[2,3,4,5], 10], [4 , 3], [6 , 2.5]]
    # [(2,10), (1,7), (2,0), (3,0), (4,0)
    # 20
    # 5 3
    wb = rng.choice(work_building_ids, 1000)
    sb = rng.choice(social_building_ids, 1000)
    fb = rng.choice(food_building_ids, 1000)
    fv = rng.integers(5,10,1000)
    wakeup = rng.random(1000)/0.6
    index = 0
    work_threshold = 4
    social_threshold = 2
    for agent in agents:
        #generate work_buildings
        work_visits = 0
        if agent.preferences[0] >= work_threshold:
            if (work_visits:=int(agent.preferences[0]/(work_threshold))) > 1:
                work_visits = rng.integers(1,int(agent.preferences[0]/(work_threshold)))
        work_duration = [agent.preferences[0] / work_visits]
        work_ids = wb[index:index+work_visits]
        food_ids = fb[index: index+fv[index]]
        social_visits = 0
        if agent.preferences[2] > social_threshold:
             if (social_visits:=int(agent.preferences[2]/(social_threshold))) > 1:
                social_visits = rng.integers(1,int(agent.preferences[2]/(social_threshold)))
        social_duration = [agent.preferences[2]/social_visits]
        social_ids=sb[index:index+social_visits]
        social_ids = [[social_id] for social_id in social_ids]
        work_ids = [[work_id] for work_id in work_ids]
        sched = [(-1,wakeup[index])] + [(work_id, work_duration) for work_id in work_ids] + [(food_ids,agent.preferences[1])] + [(social_id, social_duration) for social_id in social_ids]
        np.random.shuffle(sched)
        agent.schedule = sched
        index += max(work_visits,social_visits)


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
        low=0, high=building_ids, size=np.sum(number_of_visits)
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
        )  # this line just generates proportions from a uniform distribution
        visits = np.concatenate(
            (
                agent.home,
                buildings[j: j + i],
                agent.home,
            ),
            axis=None,
        )
        agent.schedule = list(zip(visits, times))
        j += i
    return
