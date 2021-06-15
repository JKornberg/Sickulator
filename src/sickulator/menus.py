import pygame_menu
from settings import HEIGHT, WIDTH

theme = pygame_menu.themes.THEME_ORANGE.copy()


def homeMenu(onPlay):
    home= pygame_menu.Menu(  # Instantiate Menu
        height=HEIGHT,
        width=WIDTH,
        onclose=pygame_menu.events.CLOSE,
        title='The Sickulator',
        theme=theme,
        enabled=True
    )
    home.add.button('Play', onPlay)  # Add buttons to menu
    home.add.button('Quit', pygame_menu.events.EXIT)
    return home

def optionsMenu(onPlay):
    options = pygame_menu.Menu(  # Instantiate Menu
            height=HEIGHT,
            width=WIDTH,
            onclose=pygame_menu.events.CLOSE,
            title='Options',
            theme=theme,
            enabled=False
        )

    # all sliders stuck with range starting at 0 right now; crashes otherwise. Problem with our code or problem with library?

    options.add.range_slider("Infection Rate (%)", default=33, increment=1, range_values=(0,100)) #  ideally range 1 to 100
    options.add.range_slider("Lifespan (in weeks)", default=26, increment=1, range_values=(0,156)) #  ideally range 8 to 156
    options.add.range_slider("Illness Period (in days)", default=14, increment=1, range_values=list(range(0, 61, 7)), range_text_value_enabled=False, range_text_value_tick_number=2) # ideally range 0 to 60
    options.add.range_slider("Reproduction Rate", default=.05, increment=.01, range_values=(0,1)) # default ??, increment ??, range ?? to ?? (intentions unclear here)
    options.add.range_slider("Family Size", default=2, increment=1, range_values=list(range(2,11))) # ideally range 2 to 10
    options.add.button('Play', onPlay)  # Add buttons to menu
    return options

