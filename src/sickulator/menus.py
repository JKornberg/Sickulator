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

    options.add.range_slider("Infection Rate (%)", default=33, increment=1, range_text_value_tick_number=2, range_values=(1,100), value_format=(lambda x : str(int(x)))) #  ideally range 1 to 100
    options.add.range_slider("Lifespan (in weeks)", default=5, increment=1, range_text_value_tick_number=2, range_values=(1,10), value_format=(lambda x : str(int(x)))) #  ideally range 8 to 156
    options.add.range_slider("Illness Period (in days)", default=4, increment=1, range_text_value_tick_number=2, range_values=(1,20), value_format=(lambda x : str(int(x)))) # ideally range 0 to 60
    options.add.range_slider("Reproduction Rate", default=4, increment=1, range_text_value_tick_number=2, range_values=(1,20), value_format=(lambda x : str(int(x)))) # default ??, increment ??, range ?? to ?? (intentions unclear here)
    options.add.range_slider("Family Size", default=4, increment=1, range_text_value_tick_number=2, range_values=(2,10), value_format=(lambda x : str(int(x)))) # ideally range 2 to 10
    options.add.button('Play', onPlay)  # Add buttons to menu
    return options

