
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


def connect_00z():
    now = datetime.today().strftime('%Y%m%d')
    file = Dataset('https://nomads.ncep.noaa.gov:9090/dods/gfs_0p50/gfs'+now+'/gfs_0p50_00z')

    return file 
    
def connect_06z():
    now = datetime.today().strftime('%Y%m%d')
    file = Dataset('https://nomads.ncep.noaa.gov:9090/dods/gfs_0p50/gfs'+now+'/gfs_0p50_06z')

    return file 

def query_server(model_run):
    if model_run == '06z':
        ds = connect_06z()
        print('GFS 06z Half Degree Model Chosen')
    elif model_run == '00z':
        ds = connect_00z()
        print('GFS 00z Half Degree Model Chosen')
    else:
        print('Enter either 0z or 6z')

    lat = ds.variables['lat'][:]
    lon  = ds.variables['lon'][:]

    T2m = ds.variables['tmp2m'][:]
    #converts to Kelvin
    T2m = T2m - 273.15

    z500 = ds.variables['hgtprs'][:,20]
    #convert to dm
    z500 = z500/10

    mslp = ds.variables['prmslmsl'][:]
    #convert to mb
    mslp = mslp/100

    SSRD = ds.variables['dswrfsfc'][:]
    #replaces initial time step with 0's instead of NaNs
    SSRD[0] = np.zeros((361,720))

    TP = ds.variables['apcpsfc'][:]
    #replaces initial time step with 0's instead of NaNs
    TP[0] = np.zeros((361,720))

    u_wind = ds.variables['ugrd100m'][:]
    v_wind = ds.variables['vgrd100m'][:]
    #calculate the wind direction by U and V components
    w100 = np.sqrt((u_wind*u_wind) + (v_wind*v_wind))

    
    return T2m,mslp,z500,w100,SSRD,TP,lat,lon 


T2m,mslp,z500,w100,SSRD,TP,lat,lon = query_server('06z')










    
