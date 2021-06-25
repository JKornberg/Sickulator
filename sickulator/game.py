from simulation import Simulation
from settings import HEIGHT, WIDTH, UISCALE, SimulationSettings
import sys
import pygame as pg
from menus import *
import pygame_menu
import pickle
import os

class Game:
    def __init__(self):
        self.simulation_settings : SimulationSettings = SimulationSettings()
        _stdout = sys.stdout
        _stderr = sys.stderr
        sys.stdout = sys.stderr = None
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # Creates physical game window
        sys.stdout = _stdout
        sys.stderr = _stderr
        pg.display.set_caption("The Sickulator")
        pg.key.set_repeat(500, 100)  # Determines how held keys are handled (delay, interval) in ms
        self.home = homeMenu(lambda : self._update_from_selection(2))
        self.current = 0
        self.options = optionsMenu(self)


    def run(self):
        self.simulation = Simulation(self)
        self.simulation.run()


    def quit(self):
        pg.quit()
        sys.exit()

    def show_start_screen(self):
        self.home.mainloop(self.screen)


    def show_go_screen(self):
        pass

    def _update_from_selection(self, index: int) -> None:
        """
        Change widgets depending on index.
        :param index: Index
        :return: None
        """
        self.current = index
        # Swap buttons using hide/show
        if index == 2:
            self.options.enable()
            self.options.mainloop(self.screen)
            self.home.disable()

        elif index == 3:
            self.home.disable()
            self.options.disable()
            self.run()
            
    def set_settings(self, simulation_settings: SimulationSettings):
        self.simulation_settings = simulation_settings

    def play_simulation(self, simulation_settings):
        self.set_settings(simulation_settings)
        self._update_from_selection(3)

    def end_simulation(self, result_data):
        self.save_to_results(result_data)
        results = resultsMenu(result_data)
        results.mainloop(self.screen)

    def save_to_results(self, result_data):
        obj = []
        try:
            with open("data/data.txt","rb") as f:
                obj = pickle.load(f)
        except:
            print("No data.txt file found. Creating new file")
            os.mkdir('data')
        max_infection = 0
        for h, s, i, d in result_data:
            if (h + s == 0):
                continue
            max_infection = y if (y:=s/(h+s)) > max_infection else max_infection
        result = {'duration': len(result_data), 'max_infection' : max_infection,}
        obj.append(result)
        with open("data/data.txt","wb") as f:
            pickle.dump(obj, f)
