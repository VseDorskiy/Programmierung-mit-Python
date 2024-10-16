import csv
import json
import tkinter
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import font

from PIL import Image
import os
import sys
import pandas as pd

from projekt_add_functions import ReadData
from projekt_add_functions import PlotWindow

class MainGUI:

    """Creates main user interface to build plots using data from open webpage:
    https://ourworldindata.org/explorers/co2?facet=none&country=CHN~USA~IND~GBR~OWID_WRL~DEU&Gas+or+
    Warming=CO%E2%82%82&Accounting=Production-based&Fuel+or+Land+Use+Change=All+fossil+emissions&Count=Per+capita

    Options:
        - open and save file in json and csv formats. in save if the open and saved files have different formats,
          converts the file: json --> csv or csv --> json, otherwise make a copy
        - assign parameters to plot (title, type plot, entities, colors for entities from palette or standard colors)
        - output the chosen parameters in the main window to check all the parameters together
    """

    def __init__(self):
        self.pfad = "C:\\pythonProject\\"                   # main directory where should be data and files

        self.root = tk.Tk()

        self.standard_font = 'Arial'                        # define standard font
        self.standard_font_size = 'Arial 12'
        self.menu_font_size = '12'                          # define standard fontsize for menu
        self.fontsize = '12'                                # define standard fontsize for dialogs
        self.st_button_color = '#f0f0f0'                    # standard color for disabled button

        # -------------------------------- Configure root Window --------------------------------------------
        self.root.title("Plot Construction")
        self.root.geometry("500x500")
        self.root.resizable(width=False, height=False)

        self.root.option_add("*font", self.standard_font_size)
        self.root.option_add("*Dialog.msg.font", self.standard_font_size)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)
        self.root.columnconfigure(4, weight=1)
        self.root.columnconfigure(5, weight=1)

        # -------------------------------- Creating child windows --------------------------------------------
        self.rddata = ReadData()                                  # instantiation the class
        self.plot_w = PlotWindow()                                # instantiation the class

        # configure the Toplevel window "Choose Entities"
        self.w_choose_ent = SecondWindow('Choose Entities', size="450x430", function=self.choose_entities_w_construct,
                                         button_name1='Save', bt1_command=self.save_entities, btns=2, shortcut_bt1=1,
                                         shortcut_function=self.save_entities)

        # configure the Toplevel window "Choose Plot Type"
        self.w_choose_plot = SecondWindow('Choose PLot Type', size="400x250", function=self.choose_plot_w_construct,
                                         button_name1='Save', bt1_command=self.choose_plottype, btns=2, shortcut_bt1=1,
                                         shortcut_function=self.choose_plottype)

        # configure the Toplevel window "About"
        self.w_about = SecondWindow('About', button_name1='Close', size="450x250", btns=1, function=self.project_about)

        # configure the Toplevel window "Create new Plot Title"
        self.input_pl_title_w = SecondWindow('Create new Plot Title', button_name1='Save', btns=2, size="600x200",
                                             function=self.input_window_construct, bt1_command=self.read_title,
                                             shortcut_bt1=1, shortcut_function=self.read_title, focus_state=1)

        # ------------------------------------- Define self.variables --------------------------------------------
        self.plot_title = ''                                        # chosen plot title
        self.input_title = ''                                       # plot title in input field
        self.entity_names = ['China', 'Germany', 'India', 'United Kingdom', 'United States']
        self.standard_colors = ['blue', 'green', 'red', 'cyan', 'magenta']
        self.installed_colors = []                                  # installed_colors
        self.installed_colors_to_output = []                        # installed_colors for chosen entities

        self.set_colors_default()                                # installed_colors = standard_colors (install or reset)

        self.chosen_entities = []
        self.entities_to_output = []                                # entities choosed to build aa plot
        self.choose_names_bool = [False] * len(self.entity_names)   # chosen indexes of entities after save
        self.color_button_status = [False] * len(self.entity_names) # chosen indexes of entities before save

        self.plot_b = None
        self.plots = ['Line Plot', 'Scatter Plot', 'Stack Plot']    # types of plots
        self.plottype = self.plots[0]                               # chosen plottype (by default - Line)
        self.indent_main = 10                                       # indent for plot_output_summary

        self.fr = None
        self.frc = None

        self.x, self.y, self.entity = [], [], []                    # received coordinates from data file
        self.x_title, self.y_title = None, None                     # received axis-titles from data file

        self.global_status = None                                   # status: do we have loaded data for plot

        self.filename = ''                                          # filename with data to read
        self.savefilename = ''                                      # filename with data to write

        # ----------------------------------- Creating menu --------------------------------------------
        self.create_menu('disabled')

        # ----------------------------- Creating frames in root window ----------------------------------
        i = 10

        self.title_frame = tk.Frame(self.root, padx=0, pady=0, borderwidth=2, relief='ridge',
                                  width=500, height=100)                            # frame for title output
        self.title_frame.grid(row=0, column=0, columnspan=6, sticky='new')
        self.title_frame.grid_propagate(False)                                      # make the frame static

        self.par_frame = tk.Frame(self.root, padx=0, pady=0, borderwidth=2, relief='ridge',
                                  width=250, height=334)
        self.par_frame.grid(row=1, column=0, columnspan=3, sticky='nw')             # frame for entities output
        self.par_frame.grid_propagate(False)                                        # make the frame static

        self.tools_frame = tk.Frame(self.root, padx=0, pady=0,borderwidth=2, relief='ridge',
                                    width=250, height=334)                           # frame for plot type output
        self.tools_frame.grid(row=1, column=3, columnspan=3, sticky='ne')
        self.tools_frame.grid_propagate(False)                                       # make the frame static

        # --------------------------------Output Plot' parameters in root window--------------------------------
        self.plot_summary_output()                                                   # output headers for plot summary

        # -------------------------------- Create buttons in main window-----------------------------------------
        self.button_frame = tk.Frame(self.root, padx=0, pady=0,                       # frame for buttons
                                    borderwidth=3, width=500, height=64)
        self.button_frame.grid(row=2, column=0, columnspan=6, sticky='sew')
        self.button_frame.grid_propagate(False)

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)
        self.button_frame.columnconfigure(3, weight=1)
        self.button_frame.columnconfigure(4, weight=1)
        self.button_frame.columnconfigure(5, weight=1)

        self.bt_length = 60
        self.bt_txt1, self.bt_txt2 = "Build Plot", "Exit"

        self.y_i_ind = self.x_i_ind1 = self.x_i_ind2 = 5
        self.ext_ind = 10

        self.change_global_status('disabled')                       # set global_status to False

        self.b_plot = tk.Button(self.button_frame, text=self.bt_txt1, command=self.build_plot, state='disabled')
        self.b_plot.grid(row=0, column=4, padx=self.ext_ind, pady=self.ext_ind,
                         ipadx=self.x_i_ind1, ipady=self.y_i_ind, sticky='ew')

        self.b_quit = tk.Button(self.button_frame, text=self.bt_txt2, command=self.on_closing)
        self.b_quit.grid(row=0, column=5, padx=self.ext_ind, pady=self.ext_ind,
                         ipadx=self.x_i_ind2, ipady=self.y_i_ind, sticky='ew')

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)     # exit through Window Close Command

        self.root.bind("<KeyPress>", self.shortcut)                 # install shortcut handler

        self.root.mainloop()

    def clean_color_button_status(self):                            # clean chosen entities (status before save)
        self.color_button_status = [False] * len(self.entity_names)

    def clean_summary_output(self):                                 # clean plot data in main window
        self.title_p1 = tk.Label(self.title_frame, text=' ' * 60, font=('', self.fontsize))
        self.title_p1.grid(row=0, column=1, columnspan=4, padx=0, pady=self.indent_main, ipadx=0, ipady=self.indent_main,
                           sticky='ew')

        self.ent_pl = [''] * len(self.entity_names)

        for i in range(len(self.entity_names)):
            self.ent_pl[i] = tk.Label(self.par_frame, font=('', self.fontsize), text=' ' * 40)
            self.ent_pl[i].grid(row=i + 1, column=0, padx=self.indent_main + 10, pady=5, ipadx=0, ipady=0, sticky='nw')

        self.ent_pt1 = tk.Label(self.tools_frame, text=' ' * 20, font=('', self.fontsize))
        self.ent_pt1.grid(row=1, column=0, padx=self.indent_main, pady=5, ipadx=self.indent_main, ipady=0, sticky='nw')

    def plot_summary_output(self):                                   # output chosen plot data in main window

        self.clean_summary_output()                                  # Clean the output area

        txt = self.plot_title
        self.title_p = tk.Label(self.title_frame, text="Plot Title: ", font=('', self.fontsize,'italic'))
        self.title_p.grid(row=0, column=0, padx=self.indent_main, pady=self.indent_main, ipadx=0,
                          ipady=self.indent_main, sticky='w')

        self.title_p1 = tk.Label(self.title_frame, text=txt, font=('', self.fontsize))
        self.title_p1.grid(row=0, column=1, columnspan=4, padx=0, pady=self.indent_main, ipadx=0,
                           ipady=self.indent_main, sticky='w')

        self.ent_p = tk.Label(self.par_frame, font=('', self.fontsize,"italic"), text="Chosen Entities:")
        self.ent_p.grid(row=0, column=0, padx=self.indent_main, pady=10, ipadx=0, ipady=0, sticky='nw')

        for i, txt1 in enumerate(self.entities_to_output):
            self.ent_pl[i] = tk.Label(self.par_frame, font=('', self.fontsize),
                                      fg=self.installed_colors_to_output[i], text=txt1)
            self.ent_pl[i].grid(row=i+1, column=0, padx=self.indent_main, pady=5, ipadx=self.indent_main, ipady=0,
                                sticky='nw')

        self.ent_pt = tk.Label(self.tools_frame, text="Plot Type:", font=('', self.fontsize,"italic"))
        self.ent_pt.grid(row=0, column=0, padx=self.indent_main, pady=self.indent_main, ipadx=0, ipady=0, sticky='nw')

        txt = self.plottype
        self.ent_pt1 = tk.Label(self.tools_frame, text=txt, font=('', self.fontsize))
        self.ent_pt1.grid(row=1, column=0, padx=self.indent_main, pady=5, ipadx=self.indent_main, ipady=0, sticky='nw')

    def create_menu(self, status):                                      # create menu in main window

        self.menubar = tk.Menu(self.root,font=self.standard_font)
        self.filemenu = tk.Menu(self.menubar, font=(self.standard_font,self.menu_font_size), tearoff=0)

        self.filemenu.add_command(label="Open File", accelerator='Alt+O', underline=0, command=self.fileopen)
        self.filemenu.add_command(label="Save As", accelerator='Ctrl+S', underline=0,
                                  command=self.filesave_as, state=status)
        self.filemenu.add_command(label="Close File", accelerator='Alt+C', underline=0,
                                  command=self.fileclose, state=status)

        self.filemenu.add_separator()

        self.filemenu.add_command(label="Exit", accelerator='Alt+X', underline=1, command=self.on_closing)
        self.menubar.add_cascade(menu=self.filemenu, label='File', underline=0)

        self.actionmenu = tk.Menu(self.menubar, font=(self.standard_font,self.menu_font_size), tearoff=0)
        self.actionmenu.add_command(label="Change Title", accelerator='Ctrl+T', underline=7,
                                    command=self.input_plot_title, state=status)
        self.actionmenu.add_command(label="Choose Entities", accelerator='Alt+E',
                                    command=self.choose_entities, underline=7, state=status)
        self.actionmenu.add_command(label="Choose Plot Type", accelerator='Alt+P',
                                    command=self.plot_type_choose, underline=7, state=status)
        self.actionmenu.add_separator()
        self.actionmenu.add_command(label="Build Plot", accelerator='Alt+B', command=self.build_plot,
                                    underline=0, state=status)

        self.menubar.add_cascade(menu=self.actionmenu, label='Tools',underline=0)

        self.aboutmenu = tk.Menu(self.menubar, font=(self.standard_font,self.menu_font_size), tearoff=0)
        self.aboutmenu.add_command(label="About", accelerator='Alt+A', underline=0, command=self.about)
        self.menubar.add_cascade(menu=self.aboutmenu, label='Help', underline=0)

        self.root.config(menu=self.menubar)

    def change_global_status(self, status):                             # set/change global status
        self.global_status = True if status == 'normal' else False

    def change_buttons_status(self, status):                            # change buttons status in main window

        st = True if status == 'normal' else False

        if st != self.global_status:
            self.b_plot.config(state=status)
            # self.b_plot = tk.Button(self.button_frame, text=self.bt_txt1, command=self.build_plot, state=status)
            self.b_plot.grid(row=0, column=4, padx=self.ext_ind, pady=self.ext_ind,
                             ipadx=self.x_i_ind1, ipady=self.y_i_ind, sticky='ew')

            self.change_global_status(status)

    def on_closing(self):                                               # ask user before exit
        if messagebox.askyesno(title='Exit', message='Do you really want to quit?'):
            self.root.destroy()

    def choose_plottype(self):                                          # get chosen plottype and output in main window
        self.plottype = self.plot_b.get()
        self.plot_summary_output()

    def clean_plottitle(self):                                          # clean plot title
        self.plot_title = ''

    def clean_plottype(self):                                           # set plot type to default
        self.plottype = self.plots[0]

    def fileclose(self):                                                # close file and clean chosen parameters
        self.change_buttons_status("disabled")
        self.create_menu("disabled")
        self.filename = ''
        self.clean_chosen_data()
        self.clean_summary_output()

    def fileopen(self):                                             # open file (csv or json), read data, fill variables
        try:
            self.filename = tk.filedialog.askopenfilename(filetypes=[("csv files", "*.csv"),
                                                                     ("json files", "*.json"),
                                                                     ("All files", "*.*")],
                                                          initialdir=self.pfad, title="Select File:")
            if self.filename == '':
                raise FileNotFoundError('File to open is not chosen!')

            self.rddata.set_filename(self.filename)
            self.x, self.y, self.entity, self.x_title, self.y_title = self.rddata.data_from_file()

        except FileNotFoundError as f:                               #if error - warningwindow open
            messagebox.showwarning('File Open', f)
        except Exception:
            msg = "File has incorrect format or corrupted!"
            messagebox.showerror('File Open', msg)
        else:                                                        #if file and data is Ok, set output data to default
            messagebox.showinfo('Data Load', 'Data loaded successfully!')
            self.change_buttons_status('normal')
            self.create_menu('normal')
            self.clean_chosen_data()
            self.plot_summary_output()

    def filesave_as(self):                                              # save data in file with csv or json format
        self.write_file()

    def write_file(self):                                               # write data to file in csv or json format
        try:
            save_objekt = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv",
                                                      filetypes=[("csv files", "*.csv"),
                                                                 ("json files", "*.json"),
                                                                 ("All files", "*.*")],
                                                      initialdir=self.pfad, title="Save File:")

            if save_objekt is None:                                     # key cancel chosen, no objekt from dialog
                raise FileNotFoundError('Filename to save is not specified!')

            if save_objekt.name != '':                                  # filename to save chosen
                self.savefilename = save_objekt.name

                _, fext_open = os.path.splitext(self.filename)
                _, fext_save = os.path.splitext(self.savefilename)

                if fext_save == ".json" and fext_open == ".csv":        # convert csv --> json (encoding utf-8)

                    data_dict = {}
                    with open(self.filename, 'r', encoding='utf-8') as csv_file:
                        csv_reader = csv.DictReader(csv_file)            # open csv file and maps it to dictionary

                        for i, rows in enumerate(csv_reader):            # create keys for each line and fill dictionary
                            data_dict[f'Key{i}'] = rows

                    with open(self.savefilename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json.dumps(data_dict, indent=4))      # write created dictionary to json file

                elif fext_save == ".csv" and fext_open == ".json":            # json --> csv converter

                    data_dict = {}
                    with open(self.filename, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)                           # load data from json file

                    with open(self.savefilename, 'w', encoding='utf-8', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)

                        data_keys = list((list(data.values())[0]).keys())      # write header
                        csv_writer.writerow(data_keys)

                        for key, value in data.items():                        # write data in file string by string
                            csv_writer.writerow(value.values())

                else:
                    with open(self.filename, 'r', encoding='utf-8') as rf:     # formats of files match - copy file
                        with open(self.savefilename, 'w', encoding='utf-8') as wf:
                            for line in rf:
                                wf.write(line)

        except FileNotFoundError as f:                                          # error handler: if something goes wrong
            messagebox.showwarning('File Save', f)
        except Exception:
            messagebox.showerror('Save File', 'Something went wrong:(')
        else:
            messagebox.showinfo('Save File', 'File saved successfully!')

    def shortcut(self, event):                                                  # set shortcuts to main menu

        if event.state == 131072 and event.keysym == 'o':   # Open filemenu
            self.fileopen()
        if event.state == 131072 and event.keysym == 'x':   # Exit
            self.on_closing()
        if event.state == 131072 and event.keysym == 'a':   # About
            self.about()
        if event.state == 0 and event.keysym == 'Escape':   # Close window
            self.on_closing()

        if self.global_status:                                              # works when the file with data downloaded

            if event.state == 4 and event.keysym == 's':                    # Save file in json or csv format
                self.filesave_as()
            if event.state == 131072 and event.keysym == 'c':               # Close File
                self.fileclose()
            if event.state == 4 and event.keysym == 't':                    # Change Title
                self.input_plot_title()
            if event.state == 131072 and event.keysym == 'e':               # Choose Entities
                self.choose_entities()
            if event.state == 131072 and event.keysym == 'p':               # Choose Plot Type
                self.plot_type_choose()
            if event.state == 131072 and event.keysym == 'b':               # Build_Plot
                self.build_plot()
            if event.state == 0 and event.keysym == 'Return':               # Build_Plot
                self.build_plot()

    def about(self):                                                        # open window "About"
        self.w_about.open()

    def project_about(self, window):                                        # create filling of about' window

        self.canvas = tk.Canvas(window, width=400, height=160)              # create animated text
        self.canvas.pack(fill='both', expand=True)
        self.canvas.delete('all')                           #clean old canvas if it was opened and loop is not finished

        self.canvas_t = self.canvas.create_text(120, 60, font=('Arial', 12), text='', anchor="nw")
        txt_input = ["Project 'Build a Plot on Python'",
                     "version 1.0",
                     "Projekt developed by Vsevolod Dorskiy"]

        txt_label = '\n'.join(txt_input)

        delta = 50
        delay = 0

        for x in range(len(txt_label) + 1):
            s = txt_label[:x]
            txt_output = lambda s=s: self.canvas.itemconfigure(self.canvas_t, text=s)
            self.canvas.after(delay, txt_output)
            delay += delta

        python_image = self.pfad + "python_icon.png"                        # place an image in about' window

        img=tkinter.PhotoImage(file=python_image)
        img_label = tk.Label(window, image=img, bd=5)
        img_label.place(x=20, y=60)
        img_label.image = img

    def input_plot_title(self):                                             # open window Choose Plot Title
        self.input_pl_title_w.open()

    def input_window_construct(self, window):                               # create filling for Choose Plot Title
        self.fr = tk.Frame(window, width=500, height=50)
        self.fr.grid(row=0, column=0, sticky='nsw')
        self.fr.columnconfigure(0, weight=1)
        self.fr.columnconfigure(1, weight=3)
        self.fr.rowconfigure(0, weight=1)
        self.fr.rowconfigure(1, weight=1)

        i = 5
        self.lbl = tk.Label(self.fr, text="Enter new Plot Title:", font=('',self.fontsize,'italic'))
        self.lbl.grid(row=0, column=0, padx=i, pady=i, ipadx=i, ipady=i, sticky='w')

        new_title = tk.StringVar()
        self.input_title = tk.Entry(self.fr, textvariable=new_title, font=('',self.fontsize),width=45)

        self.input_title.insert(tk.END, self.plot_title)                       # insert saved plot title in input field

        self.input_title.grid(row=0, column=1, padx=i, pady=i, ipadx=i, ipady=i, sticky='w')

        self.input_title.bind('<FocusIn>', lambda x: self.input_title.selection_range(0, tk.END))  # set focus on input
        self.input_title.focus()

    def read_title(self, *args):                                                # read and save plot title
        self.plot_title = self.input_title.get().title()                        # read and change format of string
        self.plot_summary_output()                                              # change plot data in main window

    def set_installed_colors_to_output(self):                               # set colors to chosen entities for plot
        self.installed_colors_to_output = []

        for i, value in enumerate(self.installed_colors):
            if self.choose_names_bool[i]:
                self.installed_colors_to_output.append(value)

    def build_plot(self):                                                       # build a plot with chosen parameters

        if self.check_plot_parameters():
        # choose needed data from read one in accordance with the chosen parameters
            self.plot_w.plot_data_by_entities(self.x, self.y, self.entity, self.x_title, self.y_title,
                                              self.entities_to_output)
        # create a plot
            self.plot_w.plot_output(self.plot_title, self.installed_colors_to_output, self.plottype)

    def check_plot_parameters(self):                        # check that all the needed parameters for plot are set
        status = True
        if len(self.plot_title) == 0:
            messagebox.showwarning('Plot Data', 'Please enter Plot\' Title!')
            status = False
        elif len(self.entities_to_output) == 0:
            messagebox.showwarning('Plot Data', 'Please enter Entities\' Names!')
            status = False
        return status

    def choose_entities(self):                              # open window to choose entities and colors
        self.w_choose_ent.open()

    def clean_chosen_data(self):                            # clean chosen by user parameters for plot
        self.clean_plottitle()
        self.clean_plottype()

        self.clean_chosen_entities()
        self.clean_color_button_status()
        self.set_colors_default()

        self.chosen_entities = []
        self.entities_to_output =[]
        self.installed_colors_to_output = []

    def clean_chosen_entities(self):                            # clean chosen indexes of entities
        self.choose_names_bool = [False] * len(self.entity_names)

    def save_entities(self, *args):                             # save chosen entities in the window Choose Entities
        self.entities_to_output = []

        self.clean_chosen_entities()

        for i in range(len(self.entity_names)):                 # create a list of chosen entities
            if self.chosen_entities[i].get():
                self.choose_names_bool[i] = True
                self.entities_to_output.append(self.entity_names[i])

        self.set_installed_colors_to_output()                   # create a list of chosen colors to chosen entities

        self.chosen_entities = []

        if len(self.entities_to_output) == 0:                   # if no entities chosen
            messagebox.showwarning('Choose Entities:','PLease choose minimum one Entity!')

        self.plot_summary_output()

    def plot_type_choose(self):                                 # open the window Choose Plot Type
        self.w_choose_plot.open()

    def choose_plot_w_construct(self, window):                  # create filling for window Choose Plot Type
        self.frp = tk.Frame(window, width=300, height=200)
        self.frp.grid(row=0, column=0, sticky='nsw')

        i = 10
        lbc = tk.Label(self.frp, text="Choose Plot Type:", font=('',self.fontsize,'italic'))
        lbc.grid(row=0, column=0, padx=i, pady=i, ipadx=i, ipady=i, sticky='nw')

        self.plot_b = tk.StringVar()

        self.plot_b.set(self.plottype)                          # initializing the choice

        for pl in self.plots:
            self.rad_b = tk.Radiobutton(self.frp, text=pl, variable=self.plot_b, indicatoron=True,
                                        font=('',self.fontsize), value=pl)
            self.rad_b.grid(padx=i, pady=2, ipadx=i+10, ipady=2, sticky="nw")

    def choose_entities_w_construct(self, window):                  # construct window to choose entities and colors
        self.frc = tk.Frame(window, width=440, height=350)
        self.frc.grid(row=0, column=0, sticky='new')
        self.frc.columnconfigure(0, weight=1)
        self.frc.columnconfigure(1, weight=4)
        self.frc.columnconfigure(2, weight=3)

        self.frc.rowconfigure(0, weight=1)
        self.frc.rowconfigure(1, weight=1)
        self.frc.rowconfigure(2, weight=1)
        self.frc.rowconfigure(3, weight=1)
        self.frc.rowconfigure(4, weight=1)
        self.frc.rowconfigure(5, weight=1)

        i = 10
        j= 50
        lbc = tk.Label(self.frc, text="Choose Entities:",font=('',self.fontsize,'italic'))
        lbc.grid(row=0, column=0, padx=i, pady=5, ipadx=i, ipady=5, sticky='nw')

        self.color_button_status = [status for status in self.choose_names_bool]   # fill the indexes of chosen entities

        var1 = tk.BooleanVar()                                                     # create a list of checkbuttons
        var1.set(self.choose_names_bool[0])
        txt1=self.entity_names[0]
        cb1 = tk.Checkbutton(self.frc, text=txt1, variable=var1,font=('',self.fontsize),
                             onvalue=True, offvalue=False,
                             command= lambda k=txt1:self.color_buttons_access(k))
        cb1.grid(row=1, column=0, columnspan=2, padx=j, pady=5, ipadx=2, ipady=2, sticky="w")
        self.chosen_entities.append(var1)

        var2 = tk.BooleanVar()
        var2.set(self.choose_names_bool[1])
        txt2 = self.entity_names[1]
        cb2 = tk.Checkbutton(self.frc, text=txt2, variable=var2,font=('',self.fontsize),
                             onvalue=True, offvalue=False,
                             command=lambda k=txt2: self.color_buttons_access(k))
        cb2.grid(row=2, column=0, columnspan=2, padx=j, pady=2, ipadx=2, ipady=2, sticky="w")
        self.chosen_entities.append(var2)

        var3 = tk.BooleanVar()
        var3.set(self.choose_names_bool[2])
        txt3 = self.entity_names[2]
        cb3 = tk.Checkbutton(self.frc, text=txt3, variable=var3,font=('',self.fontsize),
                             onvalue=True, offvalue=False,
                             command=lambda k=txt3: self.color_buttons_access(k))
        cb3.grid(row=3, column=0, columnspan=2, padx=j, pady=2, ipadx=2, ipady=2, sticky="w")
        self.chosen_entities.append(var3)

        var4 = tk.BooleanVar()
        var4.set(self.choose_names_bool[3])
        txt4 = self.entity_names[3]
        cb4 = tk.Checkbutton(self.frc, text=txt4, variable=var4,font=('',self.fontsize),
                             onvalue=True, offvalue=False,
                             command=lambda k=txt4: self.color_buttons_access(k))
        cb4.grid(row=4, column=0, columnspan=2, padx=j, pady=2, ipadx=2, ipady=2, sticky="ew")
        self.chosen_entities.append(var4)

        var5 = tk.BooleanVar()
        var5.set(self.choose_names_bool[4])
        txt5 = self.entity_names[4]
        cb5 = tk.Checkbutton(self.frc, text=self.entity_names[4], variable=var5,font=('',self.fontsize),
                             onvalue=True, offvalue=False,
                             command=lambda k=txt5: self.color_buttons_access(k))
        cb5.grid(row=5, column=0, columnspan=2,padx=j, pady=2, ipadx=2, ipady=2, sticky="w")
        self.chosen_entities.append(var5)

        # create buutons to choose the colors for entities

        self.buttons_color_choose_add()                 # add buttons and set the color buttons to chosen entities

        bt_state = 'disabled'                           # create Reset Colors button
        for i in self.color_button_status:
            if i:
                bt_state='normal'

        self.bt_color_reset = tk.Button(self.frc, bg=self.st_button_color, state=bt_state, text='Reset Colors',
                                     command=self.installed_colors_reset)
        self.bt_color_reset.grid(row=len(self.entity_names) + 1, column=2, padx=self.bt_padx, pady=self.bt_pady,
                                 ipadx=2, ipady=2, sticky="ew")

    def buttons_color_choose_add(self):                     # create colored buttons in Choose Entties window
        self.bt_padx, self.bt_pady = 2, 10
        self.bt_text = " " * 10

        self.bt_color = [''] * len(self.entity_names)

        for i in range(len(self.entity_names)):

            if self.color_button_status[i]:
                bt_bg = self.installed_colors[i]
                bt_state = 'normal'
            else:
                bt_bg = self.st_button_color
                bt_state = 'disabled'

            self.bt_color[i] = tk.Button(self.frc, bg=bt_bg, state=bt_state, text=self.bt_text,
                                      command=lambda k=i: self.choose_color(k))
            self.bt_color[i].grid(row=i + 1, column=2, padx=self.bt_padx, pady=self.bt_pady, ipadx=2, ipady=2,
                               sticky="ew")

    def set_colors_default(self):                               # set all the colors standard
        self.installed_colors = []
        self.installed_colors = [x for x in self.standard_colors]

    def installed_colors_reset(self):                           # set the chosen entities standard color
        self.set_colors_default()
        self.buttons_color_choose_add()
        # print('reset', self.installed_colors)

    def choose_color(self, i):                                  # choose color from color dialog to entity
        _, color_code = tk.colorchooser.askcolor(title="Choose Color:")
        if color_code:
            self.bt_color[i].config(bg=color_code)
            self.bt_color[i].grid(row=i+1, column=2, padx=self.bt_padx, pady=self.bt_pady,
                                   ipadx=2, ipady=2, sticky="ew")

            self.installed_colors[i] = color_code
        self.set_active_window(self.frc)

    def color_buttons_access(self,choosed_entity):        # change an access to buttons in Choose Entities window

        for i, entity in enumerate(self.entity_names):
            if entity == choosed_entity:
                if not self.color_button_status[i]:
                    self.bt_color[i].config(state='normal', bg=self.installed_colors[i])
                    self.color_button_status[i] = True
                else:
                    self.bt_color[i].config(state='disabled', bg=self.st_button_color)
                    self.color_button_status[i] = False
                self.bt_color[i].grid(row=i + 1, column=2, padx=self.bt_padx, pady=self.bt_pady, ipadx=2, ipady=2,
                           sticky="ew")

            for i in self.color_button_status:
                if i:
                    self.bt_color_reset.config(state='normal')
                    break
                else:
                    self.bt_color_reset.config(state='disabled')

            self.bt_color_reset.grid(row=len(self.entity_names) + 1, column=2, padx=self.bt_padx,
                                     pady=self.bt_pady, ipadx=2, ipady=2, sticky="ew")

    def set_active_window(self, window):                                    # set focus on choosed window
        window.focus_set()


class SecondWindow:

    """Creates a standard Toplevel window with one or two buttons, filling with other external objects possibility,
       assignment commands to buttons and key_press event handler"""

    def __init__(self, title=None, button_name1='Ok', button_name2='Cancel', btns=1, size="400x400", function=None,
                 bt1_command=None, bt2_command=None, shortcut_bt1=0, shortcut_function=None, focus_state=None,
                 *args, **kwargs):

        self.bt_name1 = button_name1                        # name of button #1
        self.bt_name2 = button_name2                        # name of button #2
        self.number_of_buttons = btns                       # number of standard buttons in window
        self.title = title                                  # window title
        self.size = size                                    # window size
        self.function = function                            # filling the window with new objects
        self.bt1_command = bt1_command                      # command for button #1
        self.bt2_command = bt2_command                      # command for button #2
        self.shortcut_bt1 = shortcut_bt1                    # command for key <return>
        self.shortcut_function = shortcut_function          # additional command, can be fullfiled before window closing
        self.focus_state = focus_state                      # set focus on chosen field / button
        self.window = None                                  # name of Toplevel window

        #--------------- Calculting the parameters of standard buttons in the window----------------------------------

        self.l_sym = 5
        self.bt_length = max(len(self.bt_name1) * self.l_sym, len(self.bt_name2) * self.l_sym, 60)
        self.x_window_size, self.y_window_size = map(int, size.split('x'))
        self.y_i_ind = 5
        self.ext_ind = 10

        self.x_i_ind1 = (self.bt_length - len(self.bt_name1) * self.l_sym) / 2
        self.x_i_ind2 = (self.bt_length - len(self.bt_name2) * self.l_sym) / 2

        self.x1 = self.x_window_size - self.number_of_buttons * (self.bt_length + 2 * self.ext_ind) - 3 * self.ext_ind
        self.x2 = self.x_window_size - self.bt_length - 4 * self.ext_ind

        self.y1 = self.y2 = self.y_window_size - self.ext_ind - 40

    def open(self):                                             # open the Toplevel window
        self.window = tk.Toplevel()
        self.window.grab_set()                                  # keep window allways on top
        # self.window.focus_set()

        self.window.title(self.title)
        self.window.geometry(self.size)
        self.window.wm_resizable(width=False, height=False)

        if self.function is not None:                           # use function if it's set
            self.function(self.window)

        if self.number_of_buttons == 1:                         # create one button in window
            self.btn1 = tk.Button(self.window, text=self.bt_name1, command=self.window.destroy)
            self.btn1.pack(anchor='center', side='bottom', padx=self.ext_ind, pady=self.ext_ind,
                           ipadx=self.x_i_ind1+10, ipady=self.y_i_ind)

        elif self.number_of_buttons == 2:                       # create two buttons in window
            if self.bt1_command is not None:                    # assign command to button #1
                self.btn1 = tk.Button(self.window, text=self.bt_name1, padx=self.x_i_ind1, pady=self.y_i_ind,
                                      command=self.bt1_function)
            else:
                self.btn1 = tk.Button(self.window, text=self.bt_name1, padx=self.x_i_ind1, pady=self.y_i_ind,
                                      command=self.window.destroy)
            self.btn1.place(x=self.x1, y=self.y1)

            if self.bt2_command is not None:                                    # assign command to button #2
                self.btn2 = tk.Button(self.window, text=self.bt_name2, padx=self.x_i_ind2, pady=self.y_i_ind,
                                      command=self.bt2_function)
            else:
                self.btn2 = tk.Button(self.window, text=self.bt_name2, padx=self.x_i_ind2, pady=self.y_i_ind,
                                      command=self.window.destroy)
            self.btn2.place(x=self.x2, y=self.y2)

        if self.focus_state is None:                                            # set focus in the window
            self.btn1.focus_set()

        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)           # window close command
        self.window.bind("<KeyPress>", self.shortcut)                           # activate key press handler

    def shortcut(self, event):                                                # commands for key press handler on event
        if event.state == 0 and event.keysym == 'Return':  # Close window
            if self.shortcut_bt1 == 0:
                self.window.destroy()
            else:
                self.shortcut_function_close()
        if event.state == 0 and event.keysym == 'Escape':  # Close window
            self.window.destroy()

    def bt1_function(self):                                                 # function to be fullfilled by button #1
        self.bt1_command()
        self.window.destroy()

    def bt2_function(self):                                                 # function to be fullfilled by button #2
        self.bt2_command()
        self.window.destroy()

    def shortcut_function_close(self):                                      # function to be fullfiled on window closing
        self.shortcut_function()
        self.window.destroy()


if __name__ == "__main__":
    MainGUI()
