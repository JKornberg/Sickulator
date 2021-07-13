import pygame as pg

import numpy as np
from sickulator.agent import HealthState

from sickulator.settings import SimulationSettings, building_addresses, home_addresses
vec2 = pg.Vector2


class Building:
    """
    type - 'outside', or 'inside'
    """

    def __init__(self, x, y, rect, type, id, simulation):
        self.pos = vec2(x, y)
        self.rect = rect
        self.type = type
        self.id = id
        self.agents = []
        self.simulation = simulation
        self.simulation_settings = simulation.simulation_settings
        self.infected_count = 0
    
    def add_agent(self, agent):
        self.agents.append(agent)
        if (self.type != 'outside'):
            agent.inside = True  # Makes agent invisible
        if (agent.health_state == HealthState.INFECTED):
            self.infected_count += 1
            self.infect_building()
        elif (agent.health_state == HealthState.HEALTHY and self.infected_count > 0):
            rng = np.random.default_rng()
            randoms = rng.random(self.infected_count)
            if np.any(randoms[randoms < self.simulation_settings.infection_rate * .01]):
                agent.health_state = HealthState.INFECTED
                self.infected_count += 1


    def remove_agent(self, agent):
        for i, a in enumerate(self.agents):
            if a.id == agent.id:
                self.agents[i].inside = False
                self.agents.pop(i)
                self.infected_count -= 1
                return
        #print("Agent not found in building")
        return

    def infect_building(self):
        rng = np.random.default_rng()
        randoms = rng.random(len(self.agents))
        for i, agent in enumerate(self.agents):
            if agent.health_state == HealthState.HEALTHY and randoms[i] <= self.simulation_settings.infection_rate * .01:
                agent.health_state = HealthState.INFECTED
                self.infected_count += 1

    """
    def create_homes(self):
        self.homes = []
        for x in range(0, len(home_addresses) - 1):
            self.homes.append(Building(home_addresses[x][0], home_addresses[x][1], "home"))
    
    def create_buildings(self):
        self.buildings = []
        for x in range(0, len(building_addresses)):
            if x < 6: # index of park addresses start on 6
                self.buildings.append(Building(building_addresses[x][0], building_addresses[x][1], "inside"))
            else:
                self.buildings.append(Building(building_addresses[x][0], building_addresses[x][1], "outside"))
    """


# home x-coord < 30
# building x-coord > 30



# (37, 8) = north park
# (61, 6) = baseball field
# (48,43) = southern park
