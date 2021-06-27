import pygame as pg

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

BLUE = (0, 0, 255)
# game settings
WIDTH = 1024  # originally 1024
HEIGHT = 768  # og 768
FPS = 60
TITLE = "Agent City"
BGCOLOR = DARKGREY

# size of agents/camera
TILESIZE = 16
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
UISCALE = 0.15

# Agent Settings
PLAYER_SPEED = 8
DAILY_MORTALITY_CHANCE = .1

DAY_LENGTH = 20  # Day duration in seconds
NIGHT_LENGTH = 5

class SimulationSettings:
    def __init__(
        self,
        infection_rate=10,
        lifespan=10,
        illness_period=3,
        reproduction_rate=4,
        family_size=4,
        simulation_duration=50,
    ):
        self.infection_rate = infection_rate
        self.lifespan = lifespan
        self.illness_period = illness_period
        self.reproduction_rate = reproduction_rate
        self.family_size = family_size
        self.simulation_duration = simulation_duration
