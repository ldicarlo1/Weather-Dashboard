"""This program is designed to download global weather model data, process it, and return Temprature, Cloud, and Precip Data.
""" 
import numpy as np 
import math 
from netCDF4 import num2date
from datetime import datetime
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS
import pandas as pd 
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib import style


class Weather_Model():
    def __init__(self, model_name, start, end, lat, lon):
        
        self.base_url = 'http://thredds.ucar.edu/thredds/catalog.xml'
        self.model_name = model_name

        self.start = start
        self.end = end
        self.lat = lat
        self.lon = lon
  
        self.connect()
        self.query_point()
        self.processing()
        self.plot()

    #Connects to the UCAR UNIDATA Server
    def connect(self):
        print('Connecting to Server...')

        top_cat = TDSCatalog(self.base_url)
        ref = top_cat.catalog_refs['Forecast Model Data']
        new_cat = ref.follow()
        cat = new_cat.catalog_refs[self.model_name].follow()
        self.ds = cat.latest

    #If geographical point data is requested this function is used
    def query_point(self):
        print('Retrieving selected variables...')

        ds = self.ds
        
        ncss = NCSS(ds.access_urls['NetcdfSubset'])
        query = ncss.query()
        now = datetime.utcnow()
        timestamp = self.end

        #converts time from datetime to standard time
        self.init_time = now.strftime('%Hz-%d-%Y')
        self.end_time = (now + pd.Timedelta(hours=timestamp)).strftime('%Hz-%d-%Y')

        query.time_range(now + pd.Timedelta(hours=self.start), now + pd.Timedelta(hours=timestamp))
        query.accept('netcdf4')
        query.lonlat_point(self.lon,self.lat)

        #pull temperature, cloud cover, and precip data
        query.variables('Temperature_surface','Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average',
        'Total_precipitation_surface_Mixed_intervals_Accumulation','Dewpoint_temperature_height_above_ground','Convective_available_potential_energy_surface'
        ,'Storm_relative_helicity_height_above_ground_layer')
        self.data = ncss.get_data(query)

        return self.data

    def processing(self):
        data= self.data
        temp = data.variables['Temperature_surface']
        temp = np.round(temp[:].squeeze() - 273.15)     #round all temperature data to avoid decimals
        temp = (temp*(9/5) + 32)

        dewpt = data.variables['Dewpoint_temperature_height_above_ground']
        dewpt = np.round(dewpt[:].squeeze() - 273.15)     
        dewpt = (dewpt*(9/5) + 32)

        cloud_cover = data.variables['Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average'] #percent
        cloud_cover = cloud_cover[:].squeeze()

        precip = data.variables['Total_precipitation_surface_Mixed_intervals_Accumulation']   #mm/s
        precip = precip[:].squeeze()
        precip = precip/25.40   #converts to inches of H20 p

        CAPE = data.variables['Convective_available_potential_energy_surface'][:].squeeze()
        hel = data.variables['Storm_relative_helicity_height_above_ground_layer'][:].squeeze()


        time_var = data.variables['time']
        time = num2date(time_var[:].squeeze(),time_var.units)

        self.df = pd.DataFrame({
            'Temperature': temp,'Dew Point': dewpt, 'Cloud Cover': cloud_cover, 'Precipitation': precip, 'time':time, 'CAPE':CAPE,
            'Helicity':hel
        }, index = time)
        
        return self.df

    def plot(self):
        df = self.df
        temp = df['Temperature']
        clouds = df['Cloud Cover']
        precip = df['Precipitation']
        dewpt = df['Dew Point']
        time = df['time']

        name = Nominatim().reverse("{},{}".format(self.lat,self.lon))     #generate a location
        name= (str(name)).split(',')        #split the name of the location in order to avoid an unecessarily long address
        name = name[-5:]                     #return the city, county, zip, and country
        name=','.join(name)
        duration = self.end - self.start

        plt.style.use('seaborn')


        ax2 = plt.subplot2grid((6,1),(0,0), rowspan=1)
        plt.ylabel('Precip Amount (inch/3hr)')
        plt.title('{} hour Temperature, Cloud, and Precip Forecast for {}'.format(duration,name))    #describe the location, start and end time

        ax2.axes.get_xaxis().set_visible(False)

        ax1 = plt.subplot2grid((6,1),(1,0), rowspan=4,sharex=ax2)
        plt.ylabel('Temperature (F)')
        ax1.axes.get_xaxis().set_visible(False)


        ax3 = plt.subplot2grid((6,1),(5,0), rowspan=1 ,sharex=ax2)
        ax3.fill_between(time,0,clouds,color='lightgrey')
        plt.xlabel('Date')
        plt.ylabel('Cloud Cover %')

        ax1.plot(time,temp, color='red', label='Temperature')
        ax1.plot(time,dewpt,'--', color = 'blue', label='Dew Point')
        ax1.legend(loc='upper left')

        ax2.bar(time,precip,width=0.1,color='blue', label='Precipitation')  
        ax2.legend(loc='upper left')

        ax3.plot(time,clouds, color='grey',label='Cloud Cover')
        plt.xlabel('Date')
        ax3.legend(loc='upper left')

        plt.show()
        



def main():

        location = input('Enter City/Town followed by the State: ') or ('Washington DC')
        x = Nominatim()
        name = x.geocode(location)
        lat = name.latitude
        lon = name.longitude
        model_name = 'GFS Quarter Degree Forecast'
        try:
            start = 0

            end = int(input('How many hours out:  ') or 72)
            
        except ValueError:
            print('Please enter a number')

        Weather_Model(model_name, start, end, lat,lon)






if __name__ == "__main__":
    main()


    

