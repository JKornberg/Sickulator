from settings import SimulationSettings
import pygame_menu
import pygame as pg
from settings import HEIGHT, WIDTH, UISCALE
import pickle
from os import path

menuTheme = pygame_menu.themes.THEME_GREEN.copy()
menuTheme.font = pygame_menu.font.FONT_NEVIS
menuTheme.background_color = (51, 87, 57)
menuTheme.selection_color = (250, 190, 112)

uiTheme = menuTheme.copy()
uiTheme.title = False
uiTheme.background_color = (55, 96, 113)


def homeMenu(onPlay, onResult):
    home = pygame_menu.Menu(  # Instantiate Menu
        height=HEIGHT,
        width=WIDTH,
        onclose=pygame_menu.events.CLOSE,
        title='The Sickulator',
        theme=menuTheme,
        enabled=True
    )
    home.add.button('Configure Simulation', onPlay)  # Add buttons to menu
    home.add.button('Previous Trials', onResult)  # Add buttons to menu
    home.add.button('Quit', pygame_menu.events.EXIT)
    return home


def optionsMenu(game, onBack):
    options = pygame_menu.Menu(  # Instantiate Menu
        height=HEIGHT,
        width=WIDTH,
        onclose=pygame_menu.events.CLOSE,
        title='Options',
        theme=menuTheme,
        enabled=False
    )

    infection_rate = game.simulation_settings.infection_rate
    lifespan = game.simulation_settings.lifespan
    illness_period = game.simulation_settings.illness_period
    reproduction_rate = game.simulation_settings.reproduction_rate
    family_size = game.simulation_settings.family_size
    simulation_duration = game.simulation_settings.simulation_duration
    ir_slider = options.add.range_slider("Infection Rate (%)", default=infection_rate,
                                         increment=1, range_text_value_tick_number=2, range_values=(1, 100),
                                         value_format=(lambda x: str(int(x))))
    mr_slider = options.add.range_slider("Mortality Rate (%)", default=family_size, increment=1,
                                         range_text_value_tick_number=2, range_values=(1, 100),
                                         value_format=(lambda x: str(int(x))))
    l_slider = options.add.range_slider("Lifespan (in days)", default=lifespan,
                                        increment=1, range_text_value_tick_number=2, range_values=(1, 10),
                                        value_format=(lambda x: str(int(x))))
    ip_slider = options.add.range_slider("Illness Duration (in days)", default=illness_period,
                                         increment=1, range_text_value_tick_number=2, range_values=(1, 20),
                                         value_format=(lambda x: str(int(x))))
    rr_slider = options.add.range_slider("Reproduction Rate", default=reproduction_rate,
                                         increment=1, range_text_value_tick_number=2, range_values=(1, 20),
                                         value_format=(lambda x: str(int(x))))
    ag_slider = options.add.range_slider("Starting Agent Count", default=simulation_duration, increment=1,
                                         range_text_value_tick_number=2,
                                         range_values=(1, 100), value_format=(lambda x: str(int(x))))
    fs_slider = options.add.range_slider("Family Size", default=family_size, increment=1,
                                         range_text_value_tick_number=2, range_values=(2, 10),
                                         value_format=(lambda x: str(int(x))))
    sd_slider = options.add.range_slider("Simulation Duration (in days)", default=simulation_duration, increment=1,
                                         range_text_value_tick_number=2, range_values=(1, 100),
                                         value_format=(lambda x: str(int(x))))
    options.add.button('Run Simulation', lambda: game.play_simulation(SimulationSettings(
        int(ir_slider.get_value()), int(mr_slider.get_value()), int(l_slider.get_value()), int(ip_slider.get_value()),
        int(rr_slider.get_value()), int(ag_slider.get_value()), int(fs_slider.get_value()), int(sd_slider.get_value()),
    )))  # Add buttons to menu

    options.add.button("Back", onBack)

    return options


def popup():
    surf = pg.Surface((100, 100))
    surf.fill((255, 255, 255))
    return surf


def resultsMenu(daily_stats, cumulative_stats, onBack):
    results = pygame_menu.Menu(title="Results", height=HEIGHT,
                               width=WIDTH,
                               onclose=pygame_menu.events.CLOSE,
                               theme=menuTheme,
                               )
    max_infection = 0
    for h, s, i, d in daily_stats:
        if (h + s == 0):
            continue
        max_infection = y if (y := s / (h + s)) > max_infection else max_infection
    location = path.dirname(path.realpath(__file__))
    image_file = path.join(location, 'data', 'temp_results.png')
    results.add.image(image_file)
    results.add.label("Peak Infected Percentage: " + str(round(max_infection, 2)))
    results.add.label("Percentage Killed: " + str(100 * (cumulative_stats[0] / cumulative_stats[3])) + "%")
    results.add.label("Percentage Immunized: " + str(100 * (cumulative_stats[1] / cumulative_stats[3])) + "%")
    results.add.label("Percentage Infected: " + str(100 * (cumulative_stats[2] / cumulative_stats[3])) + "%")
    results.add.button("Back", onBack)
    return results


def dataMenu(onBack):
    dataMenu = pygame_menu.Menu(title="Previous Simulations", width=WIDTH, height=HEIGHT, theme=menuTheme)
    obj = []
    location = path.dirname(path.realpath(__file__))
    file = path.join(location, 'data', 'data.txt')
    try:
        with open(file, "rb") as f:
            obj = pickle.load(f)
            if len(obj) == 0:
                dataMenu.add.label(title="No historical simulations, run the sickulator!")
            else:
                for result in obj:
                    f = dataMenu.add.frame_h(width=500, height=100)
                    f._relax = True
                    f.pack(dataMenu.add.label("Date: " + result['date'].strftime("%B %d %Y, %H:%M")))
                    f.pack(dataMenu.add.label("Percentage Infected: " + str(round(result['cumulative_stats'][0], 2))))
    except FileNotFoundError as e:
        print("No data.txt file found.")
        dataMenu.add.label(title="No historical simulations, run the sickulator!")

    dataMenu.add.button("Back", onBack)
    return dataMenu
