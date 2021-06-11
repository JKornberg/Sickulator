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
    options.add.range_slider("Infection Rate", default=.05, increment=.01, range_values=(0,1))
    options.add.button('Play', onPlay)  # Add buttons to menu
    return options

