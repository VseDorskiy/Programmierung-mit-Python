CO₂ Emissions Visualization Tool

Interactive Python Application for Data Exploration & Visualization

Overview

This project provides an interactive tool to explore CO₂ emissions from fossil fuels and industry using historical data from "Our World in Data" (~26,000 records from the 18th century to today).

The application features a Tkinter-based GUI and visualizes emissions using Matplotlib. It supports multiple plot types, country selection, color customization, and file format conversion.

Key Features

- Load and visualize CO₂ dataset (CSV or JSON)

- Interactive GUI built with Tkinter

- Select countries (China, Germany, India, UK, USA)

- Custom plot styles: Line, Scatter, Stack plot

- Color customization per selected country

- Dynamic plot title editor

- CSV <--> JSON file converter

- Input validation & error messages for smooth user experience


Demonstrated Skills

- Python (Tkinter, Matplotlib, JSON, CSV handling)

- GUI development

- Data transformation & visualization

- File format conversion

- Modular programming & clean project structure


Project Structure

/Projekt_python.py              # Main GUI class (MainGUI)

/projekt_add_functions.py       # Additional classes & helper functions

/co2.csv                        # Dataset from Our World in Data

/python_icon.png                # Icon used in "About" window


How It Works

1. Load the dataset (CSV or JSON).

2. Unlock GUI options to configure your plot:

- Plot title

- Country selection

- Plot type (Line / Scatter / Stack)

- Curve color selection

3. Preview settings in the main window.

4. Generate the plot with Matplotlib.

5. Optionally convert files between CSV and JSON.


Data Source

Original dataset:
Our World in Data – CO₂ Emissions
https://ourworldindata.org/explorers/co2
