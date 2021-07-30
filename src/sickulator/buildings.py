import pygame as pg

import numpy as np
from sickulator.agent import HealthState

from sickulator.settings import (
    SimulationSettings,
    building_addresses,
    home_addresses,
    work_building_ids,
    social_building_ids,
    food_building_ids,
    MAX_OCCUPANCY_RATIOS,
)

vec2 = pg.Vector2


class Building:
    """
    type - 'outside', or 'inside'
    building_class - "Home", "Shop", "Work", "Social"
    """

    def __init__(
        self,
        x,
        y,
        rect,
        type,
        id,
        simulation,
        building_class=None,
    ):
        self.pos = vec2(x, y)
        self.rect = rect
        self.type = type
        self.building_class = building_class
        self.id = id
        self.agents = []
        self.simulation = simulation
        self.simulation_settings = simulation.simulation_settings
        self.infected_count = 0
        if building_class == None:
            if id in work_building_ids:
                self.building_class = "Work"
            elif id in social_building_ids:
                self.building_class = "Social"
            elif id in food_building_ids:
                self.building_class = "Shop"
            else:
                raise Exception("Building not identified: " + str(id))
        else:
            self.building_class = building_class
        self.max_occupancy = np.ceil(
            MAX_OCCUPANCY_RATIOS[self.building_class]
            * self.simulation_settings.agent_count
        )

    def add_agent(self, agent):
        for a in self.agents:
            if agent.id == a.id:
                return
        self.agents.append(agent)
        agent.active_building = self
        if self.type != "outside":
            agent.inside = True  # Makes agent invisible
        if agent.health_state == HealthState.INFECTED:
            self.infect_building()
        elif (
            agent.health_state == HealthState.HEALTHY
            and self.infected_count > 0
        ):
            rng = np.random.default_rng()
            randoms = rng.random(self.infected_count)
            if np.any(
                randoms[
                    randoms < self.simulation_settings.infection_rate * 0.01
                ]
            ):
                agent.health_state = HealthState.INFECTED
        self.check_health_states()

    def remove_agent(self, agent):
        agent.active_building = None
        for i, a in enumerate(self.agents):
            if a.id == agent.id:
                self.agents[i].inside = False
                self.agents.pop(i)
                if a.health_state == HealthState.INFECTED:
                    self.infected_count -= 1
                return
        self.check_health_states()
        return

    def infect_building(self):
        rng = np.random.default_rng()
        randoms = rng.random(len(self.agents))
        for i, agent in enumerate(self.agents):
            if (
                agent.health_state == HealthState.HEALTHY
                and randoms[i] <= self.simulation_settings.infection_rate * 0.01
            ):
                agent.health_state = HealthState.INFECTED

    def check_health_states(self):
        infected = 0
        for agent in self.agents:
            if agent.health_state == HealthState.INFECTED:
                infected += 1
        self.infected_count = infected

    def reset_building(self):
        self.infected_count = 0
        self.agents = []

# home x-coord < 30
# building x-coord > 30


# (37, 8) = north park
# (61, 6) = baseball field
# (48,43) = southern park
