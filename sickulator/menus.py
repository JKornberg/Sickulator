
from settings import SimulationSettings
import pygame_menu
import pygame as pg
from settings import HEIGHT, WIDTH, UISCALE

menuTheme = pygame_menu.themes.THEME_GREEN.copy()
menuTheme.font = pygame_menu.font.FONT_NEVIS
menuTheme.background_color=(51,87,57)
menuTheme.selection_color=(250, 190, 112)

uiTheme = menuTheme.copy()
uiTheme.title = False
uiTheme.background_color = (55,96,113)



def homeMenu(onPlay):
    home= pygame_menu.Menu(  # Instantiate Menu
        height=HEIGHT,
        width=WIDTH,
        onclose=pygame_menu.events.CLOSE,
        title='The Sickulator',
        theme=menuTheme,
        enabled=True
    )
    home.add.button('Play', onPlay)  # Add buttons to menu
    home.add.button('Quit', pygame_menu.events.EXIT)
    return home


def optionsMenu(game):
    options = pygame_menu.Menu(  # Instantiate Menu
            height=HEIGHT,
            width=WIDTH,
            onclose=pygame_menu.events.CLOSE,
            title='Options',
            theme=menuTheme,
            enabled=False
        )

    infection_rate = game.simulation_settings.infection_rate
    lifespan =  game.simulation_settings.lifespan
    illness_period =  game.simulation_settings.illness_period
    reproduction_rate =  game.simulation_settings.reproduction_rate
    family_size =  game.simulation_settings.family_size
    simulation_duration =  game.simulation_settings.simulation_duration
    ir_slider = options.add.range_slider("Infection Rate (%)", default=infection_rate, \
                increment=1, range_text_value_tick_number=2, range_values=(1,100), \
                value_format=(lambda x : str(int(x))))
    l_slider = options.add.range_slider("Lifespan (in weeks)", default=lifespan, \
                increment=1, range_text_value_tick_number=2, range_values=(1,10), \
                value_format=(lambda x : str(int(x))))
    ip_slider = options.add.range_slider("Illness Period (in days)", default=illness_period, \
                increment=1, range_text_value_tick_number=2, range_values=(1,20), \
                value_format=(lambda x : str(int(x)))) 
    rr_slider = options.add.range_slider("Reproduction Rate", default=reproduction_rate,\
                increment=1, range_text_value_tick_number=2, range_values=(1,20),\
                value_format=(lambda x : str(int(x))))
    fs_slider = options.add.range_slider("Family Size", default=family_size, increment=1,\
                range_text_value_tick_number=2, range_values=(2,10), value_format=(lambda x : str(int(x))))
    sd_slider = options.add.range_slider("Simulation Duration (virtual days)",\
                default=simulation_duration, increment=1, range_text_value_tick_number=2,\
                range_values=(1,100), value_format=(lambda x : str(int(x))))
    options.add.button('Play', lambda : game.play_simulation(SimulationSettings(\
        int(ir_slider.get_value()),int(l_slider.get_value()),int(ip_slider.get_value()),\
        int(rr_slider.get_value()),int(fs_slider.get_value()),int(sd_slider.get_value()))))  # Add buttons to menu
    return options


def popup():
    surf = pg.Surface((100,100))
    surf.fill((255,255,255))
    return surf

def resultsMenu():
    results = pygame_menu.Menu(title="Results", height=HEIGHT,
            width=WIDTH,
            onclose=pygame_menu.events.CLOSE,
            theme=menuTheme,
            )
    results.add.label("Peak Infected Percentage: ")
    results.add.label("Total Healthy: ")
    results.add.label("Total Infected: ")
    results.add.label("Total Immune: ")
    results.add.label("Total Deceased: ")

    return results