# Weather Forecaster
Weather Modeler was developed by me with the objective of creating personalized dashboards for meteorological forecasters. This program downloads GFS and HRRR model data from a Unidata UCAR TDS Server, stores the data in local variables, processes and visualizes it in the form of a graph. The program will display regular weather parameters or convective parameters depending on the graph of choice.

When this program is initially run, it will as for a geographic point location, and you may enter geographic coordinates or a city/town followed by the state. Since this is a global model, it accounts for the entire Northern Hemisphere. Once the location is succesfully entered, it will prompt you to enter the length of the forecast in hours. The GFS forecasts out to a maximum of 16 days, which means if you enter any numbers higher than 384 hours it will default to 384. The HRRR on the other hand only forecasts out to 18 hours, therefore it will default to this number automatically.  

# Required Python Packages
---------------------------
For this script to run, it requires NumPy, Pandas, Datetime, netCDF4, Siphon, GeoPy, and matplotlib. 

To install NumPy use this code:

    $ pip install numpy
    
To install Pandas:
    
    $ pip install pandas
    
To install Datetime:
  
    $ pip install datetime
    
To install netCDF4:

    $ pip install netCDF4
    
To install Siphon:

    $ pip install siphon 
    
To install GeoPy:

    $ pip install geopy
    
To install matplotlib:

    $ pip install matplotlib
    
    

# Examples
--------------


![](images/git.png)

Here is an example of the convective weather graph.

![](images/conv.png)

This program is intended to improve location forecasting and benefit meteorologists by providing them with quanitifiable data rather than interpolating large scale maps. If you have any questions regarding this program don't hesitate to reach out. 
