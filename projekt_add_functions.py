import matplotlib.pyplot as plt
from matplotlib import dates as m_dates
from matplotlib import widgets
from matplotlib import artist


from matplotlib.backend_bases import MouseButton
import numpy as np
import pandas as pd


import os
import csv
import json
from datetime import datetime
from matplotlib.widgets import Cursor


class ReadData:

    """Reads data from file in csv or json format (encoding 'utf-8') originally received from website
      https://ourworldindata.org in csv format. Fills the dataset with data to create a plot"""

    def __init__(self, pfad="C:\\pythonProject\\", filename=''):
        self.pfad = pfad                                    # set standard working directory
        self.filename = filename

    def get_filename(self):                                 # get filename
        return self.filename

    def set_filename(self, filename):                       # set filename
        self.filename = filename

    def data_from_file(self):                               # read data from file
        try:
            _, fext = os.path.splitext(self.filename)

            if fext == ".json":                                    # read file in json format
                with open(self.filename, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                data_keys = list((list(data.values())[0]).keys())  # create a list of keys

                x_title = data_keys[2]
                y_title = data_keys[3]

                x, y, entity = [], [], []

                for row in data.values():
                    mydate = datetime.strptime(row[data_keys[2]], "%Y")
                    x.append(mydate)
                    y.append(float(row[data_keys[3]]))
                    entity.append(row[data_keys[0]])
                return x, y, entity, x_title, y_title
            elif fext == ".csv":                            # read data in csv format
                with open(self.filename, newline="", encoding='utf8') as csv_file:
                    reader = csv.reader(csv_file, delimiter=",")
                    title_string = next(reader)             # read header

                    _, _, x_title, y_title = list(title_string)

                    x, y, entity = [], [], []
                    for row in reader:                      # read other data
                        mydate = datetime.strptime(row[2], "%Y")
                        x.append(mydate)
                        y.append(float(row[3]))
                        entity.append(row[0])
                return x, y, entity, x_title, y_title
        except Exception:
            pass
            # msg = f'Error: {e}'
            # messagebox.showwarning('Warning', msg)
        finally:
            pass


class PlotWindow:

    """Creates a plot window and output plots in this window
        Optimizes the output data (sort the data before output to make the plots readable)
    """

    def __init__(self, size=(10, 6), *args, **kwargs):

        self.figure, self.axes = plt.subplots(figsize=size, dpi=100)
        self.x, self.y, self.entity_name, self.entities = [], [], [], []
        self.x_entity, self.y_entity = [], []
        self.x_title, self.y_title = None, None
        self.chosen_entities_dict = {}
        self.reordered_entities = []
        self.reordered_colors = []
        self.binding_id = None
        self.coord = []
        self.punkt = []
        self.xc, self.yc = [], []

    def plot_data_by_entities(self, x, y, entity_name, x_title, y_title, entities):     # choose the data for plots
        self.x, self.y, self.entity_name, self.x_title, self.y_title, self.entities = \
            x, y, entity_name, x_title, y_title, entities

        zip_data = tuple(zip(self.x, self.y, self.entity_name))                  # create a dictionary with chosen data
        self.chosen_entities_dict = {}

        for i, entity in enumerate(self.entities):
            self.x_entity = []
            self.y_entity = []

            for x1, y1, z1 in zip_data:
                if z1 == entity:
                    self.x_entity.append(x1)
                    self.y_entity.append(y1)

            self.chosen_entities_dict[entity] = self.x_entity, self.y_entity

    def plot_output(self, plot_title, colors, plottype, boxstyle=None):                         # build plots
        styles = plt.style.available  # List all available matplotlib styles
        plt.style.use(styles[9])

        type_p, _ = plottype.split()                                             # create simple names to choose plot
        type_p = type_p.lower()

        # resorting a list of entities in reversed max_y order to output skats correctly
        max_y = []
        for i, entity in enumerate(self.entities):                            # sorting the data for output optimization
            max_y.append(max(self.chosen_entities_dict[entity][1]))

        _, self.reordered_entities, self.reordered_colors = zip(*sorted(zip(max_y, self.entities, colors), reverse=True))

        for i, entity in enumerate(self.reordered_entities):                     # choose the plot type and build plots
            x_out, y_out = [], []
            x_out = self.chosen_entities_dict[entity][0]
            y_out = self.chosen_entities_dict[entity][1]

            if type_p == 'line':
                plt.plot(x_out, y_out, color=self.reordered_colors[i], linestyle='solid', label=entity)
            elif type_p == 'scatter':
                plt.scatter(x_out, y_out, color=self.reordered_colors[i], linestyle='solid', label=entity)
            elif type_p == 'stack':
                plt.stackplot(x_out, y_out, color=self.reordered_colors[i], labels=[entity])

        self.cursor = Cursor(self.axes, horizOn=False, vertOn=True, useblit=False, color='gray')

        self.annot = self.axes.annotate("", xy=(0, 0), xytext=(5, 5), xycoords='data', textcoords="offset points",
                                        bbox=dict(boxstyle='square', fc='lightgray', alpha=0.4))

        
        # self.annot.set_visible(False)

        # self.figure.canvas.mpl_connect('button_press_event', self.onclick) # button_press_event
        self.binding_id = plt.connect('motion_notify_event', self.on_move)
        # plt.connect('button_press_event', self.on_click)
        plt.connect('close_event', self.on_click)

        plt.xlabel(self.x_title)
        plt.ylabel(self.y_title)
        plt.title(plot_title)

        ax = plt.gca()

        locator = m_dates.AutoDateLocator(minticks=3, maxticks=7)           # create correct dates' zooming
        formatter = m_dates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        plt.gcf().autofmt_xdate()

        plt.legend(loc='upper left')
        plt.grid(visible=True)
        plt.show()

    def on_click(self, event):
        if event == 'close_event':
        # if event.button is MouseButton.LEFT:
            self.clean_annotations()
            self.clean_cursor_points()
            self.cursor.clear(event)

            plt.disconnect(self.binding_id)
            # self.figure.canvas.delete('all')
            # self.figure.canvas.close()
            # self.canvas.delete('all')

    # def onclick(self, event):
    def on_move(self, event):
        if event.inaxes:
            self.coord.append((event.xdata, event.ydata))
            x = event.xdata
            y = event.ydata

            self.clean_cursor_points()

            self.annot.xy = (x, y)

            df = pd.DataFrame({'Date': [x]})
            df['Date'] = pd.to_datetime(df['Date'], unit='d', origin='1970-01-01')
            xd = f"{df['Date'][0]: %Y}"

            yy = [0]*len(self.reordered_entities)
            txt = ['']*len(self.reordered_entities)

            max_len = max(len(a) for a in self.reordered_entities)

            for i, entity in enumerate(self.reordered_entities):
                for j in range(len(self.chosen_entities_dict[entity][0])):

                    if xd == f"{self.chosen_entities_dict[entity][0][j]: %Y}":
                        yy[i] = self.chosen_entities_dict[entity][1][j]

                # a_entity = self.set_length_entity(entity, max_len)
                # txt[i] = f" {a_entity} Value:{yy[i]:.2f}"
                txt[i] = f" {entity:{max_len+3}} Value:{yy[i]:.2f}"

            self.annot.set_text(f"{xd}\n" + '\n'.join(txt))
            self.create_cursor_points(x, yy)
            self.annot.set_visible(True)

            self.figure.canvas.draw_idle()
        else:
            self.clean_annotations()
            self.clean_cursor_points()
            self.figure.canvas.draw_idle()

    def set_length_entity(self, entity, maxlen):
        n = maxlen-len(entity)
        return entity+' '*int(n*1.9)

    def clean_annotations(self):
        self.annot.set_text("")

        if self.annot.get_visible():
            self.annot.set_visible(False)

    def create_cursor_points(self, x, y):
        self.xc = [x] * len(self.reordered_entities)
        self.punkt = [None] * len(self.reordered_entities)
        self.yc = [i for i in y]

        for j in range(len(self.reordered_entities)):
            if self.yc[j] > 0:
                self.punkt[j] = plt.plot(self.xc[j], self.yc[j], 'o', color=self.reordered_colors[j])

    def clean_cursor_points(self):
        for p in self.punkt:
            if p is not None:
                for pp in p:
                    pp.remove()

            self.xc, self.yc = [], []
            self.punkt = []


