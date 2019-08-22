# Weather Forecaster
Weather Modeler.py was developed by me with the objective of creating personalized dashboards for meteorological forecasters. This program downloads GFS model data from a Unidata UCAR TDS Server, stores the data in local variables, processes and visualizes it in the form of a graph. The graph displays temperature, dew point, precip totals, and cloud cover forecasts for whatever the designated duration of the forecast is.

When this program is initially run, it will as for a geographic point location, and you may enter geographic coordinates or a city/town followed by the state. Since this is a global model, it accounts for the entire Northern Hemisphere. Once the location is succesfully entered, it will prompt you to enter the length of the forecast in hours. The GFS forecasts out to a maximum of 16 days, which means if you enter any numbers higher than 384 hours it will default to 384. 


