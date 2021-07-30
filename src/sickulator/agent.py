import math
import os
from os import curdir, path
from sickulator.settings import (
    BLACK,
    BLUE,
    GREEN,
    NIGHT_LENGTH,
    PLAYER_SPEED,
    RED,
    SimulationSettings,
    TILESIZE,
    DAILY_MORTALITY_CHANCE,
    DAY_LENGTH,
    work_building_ids,
    food_building_ids,
    social_building_ids,
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
        preferences=np.array([1 / 3, 1 / 3, 1 / 3]) * DAY_LENGTH,
    ):
        self.id = id
        self.pos = vec(x, y)
        self.home = home_id
        self.simulation = simulation
        self.groups = simulation.all_sprites
        self.family = family
        pg.sprite.Sprite.__init__(self, self.groups)
        location = path.dirname(path.realpath(__file__))
        self.glob_healthy = pg.image.load(os.path.join(location,"agent_sprites","healthyglob.png"))
        self.glob_healthy = pg.transform.scale(self.glob_healthy, (TILESIZE * 2, TILESIZE * 2))
        self.glob_infected = pg.image.load(os.path.join(location,"agent_sprites","sickglob.png"))
        self.glob_infected = pg.transform.scale(self.glob_infected, (TILESIZE * 2, TILESIZE * 2))
        self.glob_immune = pg.image.load(os.path.join(location,"agent_sprites","immuneglob.png"))
        self.glob_immune = pg.transform.scale(self.glob_immune, (TILESIZE * 2, TILESIZE * 2))

        self.glob_healthy_selected = pg.image.load(os.path.join(location,"agent_sprites","healthyglob_selected.png"))
        self.glob_healthy_selected = pg.transform.scale(self.glob_healthy_selected, (TILESIZE * 2, TILESIZE * 2))
        self.glob_infected_selected = pg.image.load(os.path.join(location,"agent_sprites","sickglob_selected.png"))
        self.glob_infected_selected = pg.transform.scale(self.glob_infected_selected, (TILESIZE * 2, TILESIZE * 2))
        self.glob_immune_selected = pg.image.load(os.path.join(location,"agent_sprites","immuneglob_selected.png"))
        self.glob_immune_selected = pg.transform.scale(self.glob_immune_selected, (TILESIZE * 2, TILESIZE * 2))
        self.image = self.glob_healthy.convert_alpha()
        self.rect = self.glob_healthy.get_rect()
        self._birthday = simulation.day
        self._health_state = health_state
        # Update counts of
        Agent.health_counts[health_state.value] += 1
        self._inside = False
        self.schedule = []
        self.visit_index = 0
        self.current_shopping_index = 0
        self.time_on_current_visit = 0
        self.time_on_path = 0
        self.arrived = False
        self.infected_duration = 0
        self.preferences = preferences
        self.active_building = None
        self.name = names.get_full_name()
        self._selected = False
        self.path = []
        self.is_going_home = False
        self.is_home = True

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
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, value):
        self._selected = value
        self.set_image()
        

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
        self.set_image()
        if hs == HealthState.INFECTED:
            self.simulation.infected_today += 1
        elif hs == HealthState.DEAD:
            self.simulation.kill_agent()
            self.groups.remove(self)
            if self.active_building != None:
                self.active_building.remove_agent(self)
        elif hs == HealthState.IMMUNE:
            self.simulation.immunize_agent()


    def set_image(self):
        if self._health_state == HealthState.INFECTED:
            if self.selected:
                self.image = self.glob_infected_selected.convert_alpha()
            else:
                self.image = self.glob_infected.convert_alpha()
        elif self._health_state == HealthState.HEALTHY:
            if self.selected:
                self.image = self.glob_healthy_selected.convert_alpha()
            else:
                self.image = self.glob_healthy.convert_alpha()
        elif self._health_state == HealthState.IMMUNE:
            if self.selected:
                self.image = self.glob_immune_selected.convert_alpha()
            else:
                self.image = self.glob_immune.convert_alpha()

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

    def daily_update(self, firstDay=False):
        if (
            self.simulation.simulation_settings.lifespan
            - (self.simulation.day - self._birthday)
        ) <= 0:
            self.health_state = HealthState.DEAD
        elif firstDay == False:
            if self.health_state == HealthState.INFECTED:
                if (
                    np.random.rand()
                    < self.simulation.simulation_settings.mortality / 100
                ):
                    self.health_state = HealthState.DEAD
                if (
                    self.infected_duration
                    >= self.simulation.simulation_settings.illness_period
                ):
                    self.health_state = HealthState.IMMUNE
                else:
                    self.infected_duration += 1

        self.is_going_home = False
        self.is_home = False
        self.visit_index = 0
        self.time_on_current_visit = 0
        self.current_shopping_index = 0
        self.pos.x, self.pos.y = (
            home_addresses[self.home][0],
            home_addresses[self.home][1],
        )
        self.setup_path()
        #print("first path", self.path)

    def setup_path(self):
        if self.visit_index > len(self.schedule):
            return
        else:
            if (
                self.visit_index == 0
                or self.visit_index == len(self.schedule) - 1
            ):
                destination = home_addresses[self.home]
            else:
                location_list = self.schedule[self.visit_index][0]
                current_location = location_list[self.current_shopping_index]
                destination = building_addresses[current_location]

        self.path = self.simulation.path_finder.find_path(
            (int(self.pos.x), int(self.pos.y)), destination
        )
        if not self.path:
            self.path = [(int(self.pos.x), int(self.pos.y), "Goal")]

        self.current_step = 0
        self.distance_traveled_along_path = 0
        self.time_on_path = 0

    def update(self):
        if not self.schedule:
            return
        self.rect.center = self.pos * TILESIZE
        if (
            self.simulation.day_duration >= DAY_LENGTH - self.schedule[0][1]
            and not self.is_going_home
        ):
            if self.active_building != None:
                self.active_building.remove_agent(self)
            self.visit_index = len(self.schedule) - 1
            self.time_on_current_visit = 0
            self.current_shopping_index = 0
            self.is_going_home = True
            self.setup_path()

        current_visit = self.update_schedule()
        # If the agent has completed the current visit, start the next one
        if (
            current_visit
            and self.time_on_current_visit >= current_visit[1]
            and not self.is_going_home
        ):
            current_visit = self.get_next_visit(current_visit)

        if self.schedule:
            self.update_position(current_visit)

    def update_schedule(self):
        """
        Manage the current behavior of the agent.

        1. Agent is home -> Wait for small duration until starting their day
        2. Agent is working / socializing -> Set up path to building, stay for a period of time, wait until time is up
        3. Agent is shopping -> Get path to shop building, travel to shop location, repeat until alotted shopping time is up
        5. Agent is going home -> Night time starts, agent changes path to go home, waits until morning.
        """
        # If the agent has a schedule and hasn't finished it yet
        if self.schedule and self.visit_index < len(self.schedule):
            current_visit = self.schedule[self.visit_index]

            # Only increase the time at the visit if they arrived (work, social) at home (-1) or shopping (len(current_visit) > 1)
            # if (
            # self.arrived
            # or len(current_visit[0]) > 1
            # or current_visit[0][0] == -1
            # ):
            self.time_on_current_visit += self.simulation.dt
            self.time_on_path += self.simulation.dt

            return current_visit
        else:
            return

    def get_next_visit(self, current_visit):
        self.current_shopping_index = 0
        self.arrived = False

        visit_list = current_visit[0]
        current_visit_location = visit_list[self.current_shopping_index]
        # Starting from home or on the last vist ( not sure why this is removing an agent from home on the last visit )
        if self.visit_index == 0:
            self.simulation.homes[self.home].remove_agent(self)
        else:
            self.simulation.buildings[current_visit_location].remove_agent(self)
        # if were not on the last visit, go to the next one.
        if self.visit_index < len(self.schedule) - 1:
            self.visit_index += 1
            self.time_on_current_visit = 0
            self.setup_path()
        return current_visit

    def update_position(self, current_visit):
        """
        1. Get current distance traveled on path
        2. Get the current tile the agent should be on given the distance traveled
        3. For example, if the path is 64 pixels (4 steps, 4 * 16 = 64), and you've traveled 16 pixels (1 step) the current tile index should be (16 / 64) * len of path - 1 = 1/4 * 4 = 1
           a. could also be, current distance traveled / 16 = 16 / 16 = 1
        """

        distance_traveled = (
            self.time_on_path * PLAYER_SPEED
        )  # pixels = seconds * (pixels / second)
        current_tile_index = math.floor(
            distance_traveled / TILESIZE
        )  # constant = pixels / pixels

        # If the agent has reached the end of the path, go to the next one
        if current_tile_index > len(self.path) - 1:  # reached end of path
            if self.is_going_home and not self.is_home:
                self.simulation.homes[self.home].add_agent(self)
                self.is_home = True
            visit_list = self.schedule[self.visit_index][0]
            if len(visit_list) > 1:
                self.simulation.buildings[
                    current_visit[0][self.current_shopping_index]
                ].add_agent(self)
                self.simulation.buildings[
                    current_visit[0][self.current_shopping_index]
                ].remove_agent(self)

                if self.current_shopping_index == len(visit_list) - 1:
                    self.current_shopping_index = 0
                else:
                    self.current_shopping_index += 1
                self.setup_path()
            if not self.arrived and len(visit_list) == 1:
                self.arrived = True
                try:
                    if (
                        self.visit_index == 0
                        or self.visit_index == len(self.schedule) - 1
                    ):
                        self.simulation.homes[self.home].add_agent(self)
                    else:
                        self.simulation.buildings[
                            current_visit[0][0]
                        ].add_agent(self)
                except Exception as e:
                    print(e)
            return

            # current tile based on distance traveled
        current_tile = self.path[current_tile_index]

        # reset position, could be improved since this causes slight glitches when the agent was almost at the end of
        # the tile
        self.pos.x = current_tile[0]
        self.pos.y = current_tile[1]

        # Since we're at the start of the tile, I need to figure out how far along the tile the agent has moved.
        # I take the distance traveld UP TO the current tile and then find the difference from the total distance
        floored_distance_traveled = (
            current_tile_index * TILESIZE
        )  # pixels = n*pixels
        remaining_distance_traveled = (
            distance_traveled - floored_distance_traveled
        )  # pixels = pixels - pixels

        # Then I need to check which direction to move the agent along the tile to make sure he continues moving along the path.
        if current_tile[2] == "North":
            self.pos.y -= remaining_distance_traveled / TILESIZE
        elif current_tile[2] == "South":
            self.pos.y += remaining_distance_traveled / TILESIZE
        elif current_tile[2] == "East":
            self.pos.x += remaining_distance_traveled / TILESIZE
        elif current_tile[2] == "West":
            self.pos.x -= remaining_distance_traveled / TILESIZE


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
        self.reproduction_days = simulation.simulation_settings.reproduction_cooldown  # days since last reproduction (can reproduce first night)
        Family.count += 1

    def add_agent(self, agent: Agent):
        """Add agent to a family's agents list"""
        self.agents.append(agent)


def generate_schedules(agents):
    """New scheduling algorithm"""
    rng = np.random.default_rng()
    wb = rng.choice(range(len(building_addresses)), 2000)
    sb = rng.choice(social_building_ids, 2000)
    fb = rng.choice(food_building_ids, 5000)
    fv = rng.integers(5, 10, 2000)
    wakeup = rng.random(2000) * 4
    index = 0
    work_threshold = 6
    social_threshold = 4
    for agent in agents:
        # generate work_buildings
        w, f, s = agent.preferences
        social_visits = 0
        if (
            s >= social_threshold
            and (social_visits := int(s / (social_threshold))) > 1
        ):
            social_visits = rng.integers(
                1, int(agent.preferences[2] / (social_threshold))
            )
            social_duration = agent.preferences[2] / social_visits
            social_ids = sb[index : index + social_visits]
            social_ids = [[social_id] for social_id in social_ids]
        else:
            social_duration = 0
            social_ids = []
            w += s / 2
            f += s / 2
        work_visits = 0
        if (
            w >= work_threshold
            and (work_visits := int(w / (work_threshold))) > 1
        ):
            work_visits = rng.integers(1, int(w / (work_threshold)))
            work_duration = w / work_visits
            work_ids = wb[index : index + work_visits]
        else:
            f = f + w
            work_duration = 0
            work_ids = []
        food_ids = fb[index : index + fv[index]]
        work_ids = [[work_id] for work_id in work_ids]
        sched = (
            [(work_id, work_duration) for work_id in work_ids]
            + [(food_ids, f)]
            + [(social_id, social_duration) for social_id in social_ids]
        )
        np.random.shuffle(sched)
        agent.schedule = sched
        agent.schedule.insert(0, ([-1], wakeup[index]))
        agent.schedule.append(([-1], NIGHT_LENGTH))
        index += max(work_visits, social_visits)
