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
PLAYER_SPEED = 3
DAILY_MORTALITY_CHANCE = .2

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

home_addresses = [
    (4, 4),
    (11, 4),
    (18, 4),
    (25, 4),
    (4, 12),
    (11, 12),
    (18, 12),
    (25, 12),
    (4, 22),
    (11, 22),
    (18, 22),
    (25, 22),
    (4, 30),
    (11, 30),
    (18, 30),
    (25, 30),
    (4, 40),
    (11, 40),
    (18, 40),
    (25, 40),
]

building_addresses = [
    (49, 6),
    (44, 19),
    (36, 23),
    (54, 23),
    (54, 30),
    (38, 36),
    (37, 8),
    (61, 6),
    (48, 43),
]

# Rect((left, top), (w, h))
home_rectangles = [pg.Rect((32, 16), (80, 96)), pg.Rect((144, 16), (80, 96)), pg.Rect((256, 16), (80, 96)),
                   pg.Rect((368, 16), (80, 96)), pg.Rect((32, 160), (80, 96)), pg.Rect((144, 160), (80, 96)),
                   pg.Rect((256, 160), (80, 96)), pg.Rect((368, 160), (80, 96)), pg.Rect((32, 304), (80, 96)),
                   pg.Rect((144, 304), (80, 96)), pg.Rect((256, 304), (80, 96)), pg.Rect((368, 304), (80, 96)),
                   pg.Rect((32, 448), (80, 96)), pg.Rect((144, 448), (80, 96)), pg.Rect((256, 448), (80, 96)),
                   pg.Rect((368, 448), (80, 96)), pg.Rect((32, 592), (80, 96)), pg.Rect((144, 592), (80, 96)),
                   pg.Rect((256, 592), (80, 96)), pg.Rect((368, 592), (80, 96))]

building_rectangles = [pg.Rect((752, 0), (112, 128)), pg.Rect((672, 208), (112, 128)), pg.Rect((528, 272), (112, 128)),
                       pg.Rect((816, 272), (112, 128)), pg.Rect((816, 464), (112, 128)), pg.Rect((560, 480), (112, 112)),
                       pg.Rect((496, 0), (208, 144)), pg.Rect((944, 32), (64, 96)), pg.Rect((768, 624), (192, 144))
                       ]
