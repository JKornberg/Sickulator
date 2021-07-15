from simulation import Simulation
from settings import HEIGHT, WIDTH, UISCALE, SimulationSettings
import sys
import pygame as pg
from menus import *
import pygame_menu
import pickle
import os
from os import path
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt


class Game:
    def __init__(self):
        self.simulation_settings: SimulationSettings = SimulationSettings()
        _stdout = sys.stdout
        _stderr = sys.stderr
        sys.stdout = sys.stderr = None
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # Creates physical game window
        sys.stdout = _stdout
        sys.stderr = _stderr
        pg.display.set_caption("The Sickulator")
        pg.key.set_repeat(500, 100)  # Held key handler
        self.current = 0  # Current page index
        self.home = homeMenu(lambda: self._update_from_selection(2), lambda: self._update_from_selection(4))
        self.options = optionsMenu(self, lambda: self._update_from_selection(1))
        self.data_menu = dataMenu(lambda: self._update_from_selection(1))

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
        if index == 1:
            self.options.disable()
            self.data_menu.disable()
            self.home.enable()
            self.home.mainloop(self.screen)
        if index == 2:
            self.options.enable()
            self.options.mainloop(self.screen)
            self.home.disable()
        elif index == 3:
            self.home.disable()
            self.options.disable()
            self.run()
        elif index == 4:
            self.home.disable()
            self.options.disable()
            data_menu = dataMenu(lambda: self._update_from_selection(1))
            data_menu.mainloop(self.screen)

    def set_settings(self, simulation_settings: SimulationSettings):
        self.simulation_settings = simulation_settings

    def play_simulation(self, simulation_settings):
        self.set_settings(simulation_settings)
        self._update_from_selection(3)

    def end_simulation(self, daily_stats, cumulative_stats):
        self.save_to_results(daily_stats, cumulative_stats)

        x = range(len(daily_stats))
        # y = list(zip(*daily_stats))
        y = [[daily_stats[j][i] for j in range(len(daily_stats))] for i in range(len(daily_stats[0]))]
        location = path.dirname(os.path.realpath(__file__))
        file = path.join(location, 'data', 'temp_results.png')
        if not os.path.isdir(path.join(location, 'data')):
            os.mkdir(path.join(location, 'data'))
        # self.simulation_settings.infection_rate

        plt.clf()
        # Green, Red, Blue, Black #
        pal = ["#00ff40", "#f7020f", "#0a53f2", "#0a140c"]
        plt.stackplot(x, y, labels=['Healthy', 'Infected', 'Immune', 'Deceased'], colors=pal)
        plt.title('Change in agent population over time at infection rate: ' + str(
            self.simulation_settings.infection_rate) + '%', fontproperties='Times New Roman', size='16')
        plt.legend(loc='upper left')
        plt.xlabel('Time (days of simulation passed)', fontproperties='Times New Roman', size='16')
        plt.ylabel('Number of agents', fontproperties='Times New Roman',
                   size='16')
        plt.savefig(file, dpi=100)
        results = resultsMenu(daily_stats, cumulative_stats, lambda: self._update_from_selection(1))
        results.mainloop(self.screen)

    def save_to_results(self, daily_stats, cumulative_stats):
        obj = []
        location = path.dirname(os.path.realpath(__file__))
        file = path.join(location, 'data', 'data.txt')
        try:
            with open(file, "rb") as f:
                obj = pickle.load(f)
        except:
            print("No data.txt file found. Creating new file")
            if not os.path.isdir(path.join(location, 'data')):
                os.mkdir(path.join(location, 'data'))
        max_infection = 0

        for h, s, i, d in daily_stats:
            if (h + s == 0):
                continue
            max_infection = y if (y := s / (h + s)) > max_infection else max_infection
        result = {'date': datetime.now(), 'daily_stats': daily_stats, 'cumulative_stats': cumulative_stats}
        obj.append(result)
        with open(file, "wb") as f:
            pickle.dump(obj, f)
