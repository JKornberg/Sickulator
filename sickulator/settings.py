# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0,0,255)
# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

TILESIZE = 8
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
UISCALE = .15


class SimulationSettings:
    def __init__(self,infection_rate=10, lifespan=10, illness_period=3, reproduction_rate=4, family_size=4, simulation_duration=50):
        self.infection_rate = infection_rate
        self.lifespan = lifespan
        self.illness_period = illness_period
        self.reproduction_rate = reproduction_rate
        self.family_size = family_size
        self.simulation_duration = simulation_duration
    