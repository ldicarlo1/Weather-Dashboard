
import numpy as np
import matplotlib.pyplot as plt
import netCDF4



# set up the URL to access the data server.
# See the NWW3 directory on NOMADS 
# for the list of available model run dates.

mydate='20191204'
url='https://nomads.ncep.noaa.gov:9090/dods/gfs_0p50/gfs20191204/gfs_0p50_06z'

# Extract the significant wave height of combined wind waves and swell

file = netCDF4.Dataset(url)
lat  = file.variables['lat'][:]
lon  = file.variables['lon'][:]
T2m = file.variables['tmp2m'][:].squeeze() - 273.15
z500 = file.variables['hgtprs'][:,20]

level = file.variables['lev']

print(T2m)



https://nomads.ncep.noaa.gov:9090/dods/gfs_0p50/gfs20191204/gfs_0p50_06z.info



def query_server(model_run):
    '''Queries the THREDDS server for variables of interest.
    Converts variables into correct units.
    Fills in 00z data..
    Returns all variables.
    '''
    #start a query
    if model_run == '06z':
        ncss = connect_06z()
        print('GFS 06z Half Degree Model Chosen')
    elif model_run == '00z':
        ncss = connect_00z()
        print('GFS 00z Half Degree Model Chosen')
    else:
        print('Enter either 0z or 6z')
   #start a query
    #all variables will be a length of 129, carrying timestamps from 00z init date to 00z end date
    query = ncss.query()
    query.accept('netcdf')
    query.variables('Pressure_reduced_to_MSL_msl').all_times()
    data = ncss.get_data(query)
    time_mslp = data.variables[(list(data.variables))[1]][:].squeeze()
    mslp = data.variables['Pressure_reduced_to_MSL_msl'][:].squeeze()
    mslp = mslp/100
    mslp = data_adjustment(mslp,time_mslp)

    query = ncss.query()
    query.accept('netcdf')
    query.variables('Downward_Short-Wave_Radiation_Flux_surface_Mixed_intervals_Average').all_times()
    data = ncss.get_data(query)
    SSRD = data.variables['Downward_Short-Wave_Radiation_Flux_surface_Mixed_intervals_Average'][:].squeeze()
    time_SSRD = data.variables[(list(data.variables))[1]][:].squeeze()
    SSRD = data_adjustment(SSRD,time_SSRD)
    
    
    query = ncss.query()
    query.accept('netcdf')
    query.variables('Total_precipitation_surface_Mixed_intervals_Accumulation').all_times()
    data = ncss.get_data(query)
    TP = data.variables['Total_precipitation_surface_Mixed_intervals_Accumulation'][:].squeeze()  
    #TP time steps go 3z,6z,9z,9z,12z,12z,15z,15z, etc
    #we want accumulated only, which is every first time step, problem is that 3z and 6z aren't repeated
    #we pull 6z out
    TP_6z = TP[1]
    #time steps now look like this 3z,9z,9z,12z,12z,15z,15z
    TP = TP[0::2]
    # time steps now look like this 3z,9z,12z,15z
    # add 6z back in 
    TP = np.insert(TP,1,TP_6z[0], axis=0)
    #insert 0z to first spot
    TP_0 = TP[0] - TP[0]
    TP = np.insert(TP,0,TP_0,axis=0) 
    # timesteps now are regular 0z,3z,6z,9z,12z,15z

    #latitude is constant but longitude must be combined for east/west of prime meridian correction  
    lat = data.variables['lat'][:].squeeze()
    lon = data.variables['lon'][:].squeeze()

    query = ncss.query()
    query.accept('netcdf')
    query.variables('Temperature_height_above_ground').all_times().vertical_level(2)
    data = ncss.get_data(query)
    time_T2m = data.variables[(list(data.variables))[1]][:].squeeze()
    T2m = data.variables['Temperature_height_above_ground'][:].squeeze() 
    T2m = T2m - 273.15  
    T2m = data_adjustment(T2m,time_T2m)

    
    #creates query
    query = ncss.query()
    query.accept('netcdf')
    #specifies that we would like to collect the whole time extent of the GFS model 
    query.variables('u-component_of_wind_height_above_ground','v-component_of_wind_height_above_ground').all_times().vertical_level(100)
    #specifies we want wind at 100 meters
    data = ncss.get_data(query)
    time_w100 = data.variables[(list(data.variables))[1]][:].squeeze()
    u_wind = data.variables['u-component_of_wind_height_above_ground'][:].squeeze()
    v_wind = data.variables['v-component_of_wind_height_above_ground'][:].squeeze()
    #calculate the wind direction by U and V components
    w100 = np.sqrt((u_wind*u_wind) + (v_wind*v_wind))
    w100 = np.array(w100)
    w100 = data_adjustment(w100,time_w100)
    
    query = ncss.query()
    query.accept('netcdf')
    query.variables('Geopotential_height_isobaric').all_times().vertical_level(50000) 
    data = ncss.get_data(query)
    time_z500 = data.variables[(list(data.variables))[1]][:].squeeze()
    z500 = data.variables['Geopotential_height_isobaric'][:].squeeze()
    z500 = z500/10
    z500 = data_adjustment(z500, time_z500)

    del(query,data,ncss,u_wind,v_wind)
    
    return T2m,mslp,z500,w100,SSRD,TP,lat,lon 
    
    
    #all must be in 129,361,720 format.
    
