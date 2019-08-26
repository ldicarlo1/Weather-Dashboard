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
    def __init__(self,model_name,start,end,lat,lon,variables):
        
        self.base_url = 'http://thredds.ucar.edu/thredds/catalog.xml'
        self.model_name = model_name
        self.start = start
        self.end = end
        self.lat = lat
        self.lon = lon
        self.variables = variables


    #Connects to the UCAR UNIDATA Server
    def connect(self):
        print('Connecting to Server...')

        top_cat = TDSCatalog(self.base_url)
        ref = top_cat.catalog_refs['Forecast Model Data']
        new_cat = ref.follow()
        cat = new_cat.catalog_refs[self.model_name].follow()
        ds = cat.latest
        return ds

    #If geographical point data is requested this function is used
    def query_point(self):
        print('Retrieving selected variables...')

        ds = self.connect()
        
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
        query.variables(self.variables)
        data = ncss.get_data(query)

        return data

    def processing(self):
        
        data= self.query_point()
        #define changes in variables between HRRR and GFS models

        try:
            temp = data.variables['Temperature_surface']
            cloud_cover = data.variables['Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average'] #percent
            precip = data.variables['Total_precipitation_surface_Mixed_intervals_Accumulation']   #mm/s
            self.label_precip = '3 hrs'
        except Exception:
            temp = data.variables['Temperature_height_above_ground']
            cloud_cover = data.variables['Total_cloud_cover_entire_atmosphere'] #percent
            precip = data.variables['Total_precipitation_surface_1_Hour_Accumulation']   #mm/s
            self.label_precip = 'Hour'

        temp = np.round(temp[:].squeeze() - 273.15)     #round all temperature data to avoid decimals
        temp = (temp*(9/5) + 32)
        cloud_cover = cloud_cover[:].squeeze()
        dewpt = data.variables['Dewpoint_temperature_height_above_ground']
        dewpt = np.round(dewpt[:].squeeze() - 273.15)     
        dewpt = (dewpt*(9/5) + 32)
        precip = precip[:].squeeze()
        precip = precip/25.40   #converts to inches of H20 p

        CAPE = data.variables['Convective_available_potential_energy_surface'][:].squeeze()

        CIN = data.variables['Convective_inhibition_surface'][:].squeeze()
        u_wind = data.variables['u-component_of_wind_isobaric'][:].squeeze()
        v_wind = data.variables['v-component_of_wind_isobaric'][:].squeeze()
        try:
            u_500 = u_wind[:,18]
            v_500 = v_wind[:,18]
            u_sfc = u_wind[:,30]
            v_sfc = v_wind[:,30] 
        except Exception:
            u_500 = u_wind[:,0]
            v_500 = v_wind[:,0]
            u_sfc = u_wind[:,4]
            v_sfc = v_wind[:,4]   
            
        wind_500 = np.sqrt((u_500 * u_500) + (v_500 * v_500)) 
        wind_sfc = np.sqrt(((u_sfc * u_sfc) + (v_sfc * v_sfc)))
        shear = (wind_500 - wind_sfc) * 1.94384     #convert from m/s to knots
       

        time_var = data.variables['time']
        time = num2date(time_var[:].squeeze(),time_var.units)

        df = pd.DataFrame({
            'Temperature': temp,'Dew Point': dewpt, 'Cloud Cover': cloud_cover, 'Precipitation': precip, 'time':time, 'CAPE':CAPE,
            'Shear':shear, 'CIN':CIN
        }, index = time)
        return df
        

    def location_name(self):
        name = Nominatim().reverse("{},{}".format(self.lat,self.lon))     #generate a location
        name= (str(name)).split(',')        #split the name of the location in order to avoid an unecessarily long address
        name = name[-5:]                     #return the city, county, zip, and country
        name=','.join(name)
        duration = self.end - self.start
        return duration,name


    def plot(self):
        print('Generating Map')
        duration,name = self.location_name()
        df = self.processing()
        temp = df['Temperature']
        clouds = df['Cloud Cover']
        precip = df['Precipitation']
        dewpt = df['Dew Point']
        time = df['time']

        plt.style.use('seaborn')


        ax2 = plt.subplot2grid((6,1),(0,0), rowspan=1)
        plt.ylabel('Precip Amount (inch/{})'.format(self.label_precip))
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

        ax2.bar(time,precip,width=0.05,color='blue', label='Precipitation')  
        ax2.legend(loc='upper left')

        ax3.plot(time,clouds, color='grey',label='Cloud Cover')
        ax3.vmin=0
        ax3.vmax=100
        plt.xlabel('Date')
        ax3.legend(loc='upper left')

        plt.show()
        
    def plot_convection(self):
        print('Generating Map')
        duration,name = self.location_name()
        df = self.processing()
        temp = df['Temperature']
        CAPE = df['CAPE']
        precip = df['Precipitation']
        dewpt = df['Dew Point']
        time = df['time']
        CIN = df['CIN']
        shear = df['Shear']

        plt.style.use('seaborn')
        ax2 = plt.subplot2grid((6,1),(0,0), rowspan=2)
        plt.ylabel('J/Kg')
        plt.title('{} hour Convective Forecast for {}'.format(duration,name))    #describe the location, start and end time

        ax2.axes.get_xaxis().set_visible(False)

        ax1 = plt.subplot2grid((6,1),(2,0), rowspan=2,sharex=ax2)
        plt.ylabel('Temperature (F)')
        ax1.axes.get_xaxis().set_visible(False)


        ax3 = plt.subplot2grid((6,1),(4,0), rowspan=2 ,sharex=ax2)
        plt.xlabel('Date')
        plt.ylabel('Speed Shear 0-6km (knots)')

        ax1.plot(time,temp, color='red', label='Temperature')
        ax1.plot(time,dewpt,'--', color = 'blue', label='Dew Point')
        ax1.legend(loc='upper left')

        ax2.plot(time,CAPE,color='green', label='CAPE')
        ax2.plot(time,CIN,color='red',label='CIN')  
        ax2.legend(loc='upper left')

        ax3.plot(time,shear, color='grey',label='Speed Shear 0-6km')
        ax3.fill_between(time,0,shear,color='lightgrey')
        plt.xlabel('Date')
        ax3.legend(loc='upper left')

        plt.show()

class GFS(Weather_Model):
    def __init__(self):

        location = input('Enter City/Town followed by the State: ') or ('Washington DC')
        x = Nominatim()
        name = x.geocode(location)
        try:
            start = 0

            end = int(input('How many hours out:  ') or 72)
            
        except ValueError:
            print('Please enter a number')
        lat = name.latitude
        lon = name.longitude
        model_name = 'GFS Quarter Degree Forecast'
        variables = ('Temperature_surface','Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average',
        'Total_precipitation_surface_Mixed_intervals_Accumulation','Dewpoint_temperature_height_above_ground','Convective_available_potential_energy_surface'
        ,'Storm_relative_helicity_height_above_ground_layer','Convective_inhibition_surface','u-component_of_wind_isobaric','v-component_of_wind_isobaric')
        super().__init__(model_name,start,end,lat,lon,variables)
        self.plot()

class HRRR(Weather_Model):
    def __init__(self):

        location = input('Enter City/Town followed by the State: ') or ('Washington DC')
        x = Nominatim()
        name = x.geocode(location)
        try:
            start = 0

            end = int(input('How many hours out:  ') or 72)
            
        except ValueError:
            print('Please enter a number')
        lat = name.latitude
        lon = name.longitude
        model_name = 'NCEP HRRR CONUS 2.5km'
        variables= ('Total_precipitation_surface_1_Hour_Accumulation','Total_cloud_cover_entire_atmosphere','Temperature_height_above_ground',
        'Dewpoint_temperature_height_above_ground','Convective_available_potential_energy_surface','Storm_relative_helicity_height_above_ground_layer',
        'Convective_inhibition_surface','u-component_of_wind_isobaric','v-component_of_wind_isobaric')
        super().__init__(model_name,start,end,lat,lon,variables)
        self.plot()
        
if __name__ == "__main__":
    GFS()


    
