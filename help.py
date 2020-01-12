from netCDF4 import Dataset
import numpy as np 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pygrib
from datetime import datetime, timedelta

x = []
bias = []
num = 95               # June 13 is the first day that includes the GFS 0.5 degree update; specifies which index is the start of the 13th of June
month = 6                 # the starting month of the loop being June
for i in range(0,110):    # 110 days is the total length of days that we have reanalysis data for since June 13th   
    date = (datetime(2019,6,13) + timedelta(days=i)).strftime('%Y%m%d')
    month = date[4:6]
    timestep = np.array(['00','03','06','09','12','15','18','21'])
    bias.append(x)
    for j in range(0, len(timestep)):      #loops through for 8 time steps within each day
        file = '/mnt/naslsc2nwp/GFS/data/'+date+'/gfs.t00z.pgrb2.0p50.f0'+timestep[j]+''
        grb = pygrib.open(file)
        t2m = grb.select(name='Temperature')[0].values - 273.15
        t2m = np.array(t2m)
        t2m_west_of_meridian = np.array(t2m[30:121,660:720]) 
        t2m_east_of_meridian = np.array(t2m[30:121,0:91])
        t2m_oper = np.concatenate((t2m_west_of_meridian,t2m_east_of_meridian),axis=1) #adjusts longitude to be from -30 to 45
        
        file2 = '/home/luca/Desktop/Bias Project/all_vars_2019_'+month+'.nc'
        nc = Dataset(file2)
        t2m_era5 = nc.variables['t2m'][:]
        t2m_era5 = np.array(t2m_era5)
        t2m_era5 = np.where(t2m_era5==-32767,np.nan,t2m_era5)
        diff = t2m_oper - t2m_era5[num]    #sets ocean data to NaN
        num+=1
        if num == len(t2m_era5):
            num = 0 
        x.append(diff)
bias = np.array(bias)
#bias_average = np.nanmean()











    
