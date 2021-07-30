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
CAMERA_SPEED = 300
PLAYER_SPEED = 300  # pixels per second
DAILY_MORTALITY_CHANCE = 0.2


DAY_LENGTH = 20  # Day duration in seconds
NIGHT_LENGTH = 10


class SimulationSettings:
    def __init__(
            self,
            infection_rate=30,
            mortality_rate=10,
            lifespan=10,
            illness_period=3,
            reproduction_rate=4,
            reproduction_cooldown=2,
            agent_count=20,
            family_size=4,
            simulation_duration=50,
    ):
        self.infection_rate = infection_rate
        self.mortality = mortality_rate
        self.lifespan = lifespan
        self.illness_period = illness_period
        self.reproduction_rate = reproduction_rate
        self.reproduction_cooldown = reproduction_cooldown
        self.agent_count = agent_count
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

# Work buildings = building_addresses[0-6]
# Food Buildings = building_addresses[7-8]
# Social Buildings = building_addresses[9-11]
# Outside Areas = building_addresses[12-16]
building_addresses = [
    (36, 23),
    (44, 19),
    (54, 23),
    (49, 6),
    (54, 30),
    (70, 24),
    (66, 42),
    (38, 35),
    (34, 43),
    (84, 38),
    (88, 24),
    (85, 6),
    (35, 3),
    (61, 6),
    (51, 42),
    (70, 3),
    (86, 14),
]

building_rectangles = [
    pg.Rect((528, 272), (112, 128)),
    pg.Rect((672, 208), (112, 128)),
    pg.Rect((816, 272), (112, 128)),
    pg.Rect((752, 0), (112, 128)),
    pg.Rect((816, 464), (112, 128)),
    pg.Rect((1056, 272), (144, 144)),
    pg.Rect((1024, 576), (192, 128)),
    pg.Rect((560, 480), (112, 112)),
    pg.Rect((512, 608), (192, 96)),
    pg.Rect((1296, 512), (112, 128)),
    pg.Rect((1328, 288), (128, 128)),
    pg.Rect((1328, 0), (128, 128)),
    pg.Rect((496, 0), (208, 144)),
    pg.Rect((944, 32), (64, 96)),
    pg.Rect((768, 624), (192, 144)),
    pg.Rect((1024, 0), (208, 96)),
    pg.Rect((1296, 160), (208, 96)),    
]

# Rect((left, top), (w, h))
home_rectangles = [
    pg.Rect((32, 16), (80, 96)),
    pg.Rect((144, 16), (80, 96)),
    pg.Rect((256, 16), (80, 96)),
    pg.Rect((368, 16), (80, 96)),
    pg.Rect((32, 160), (80, 96)),
    pg.Rect((144, 160), (80, 96)),
    pg.Rect((256, 160), (80, 96)),
    pg.Rect((368, 160), (80, 96)),
    pg.Rect((32, 304), (80, 96)),
    pg.Rect((144, 304), (80, 96)),
    pg.Rect((256, 304), (80, 96)),
    pg.Rect((368, 304), (80, 96)),
    pg.Rect((32, 448), (80, 96)),
    pg.Rect((144, 448), (80, 96)),
    pg.Rect((256, 448), (80, 96)),
    pg.Rect((368, 448), (80, 96)),
    pg.Rect((32, 592), (80, 96)),
    pg.Rect((144, 592), (80, 96)),
    pg.Rect((256, 592), (80, 96)),
    pg.Rect((368, 592), (80, 96)),
]



work_building_ids = [5, 2, 1, 0, 4, 12]
food_building_ids = [7, 8, 14, 6, 9, 16, 10, 3]
social_building_ids = [11, 13, 15]

MAX_OCCUPANCY_RATIOS = {
    "Work": 0.2,
    "Shop": 0.2,
    "Social": 0.4,
    "Home": float("inf"),
}
