import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

def filter_data(path, year='2019'):
    """Get the 2019 data from the csv file, and get the corresponding latitudes and longitudes"""
    # read the dataframe: 77825496 rows x 35 columns
    df = pd.read_csv(path, low_memory=False)
    
    # filter based on felonies
    filtered_df = df.loc[(df['LAW_CAT_CD'] == 'FELONY')
                         & (df['CMPLNT_FR_DT'].str.endswith(year))
                         & (df['CMPLNT_FR_DT'].str.contains('NaN')==False)
                         & (df['CMPLNT_TO_DT'].str.endswith(year))
                         & (df['CMPLNT_TO_DT'].str.contains('NaN')==False)
                         & (df['Latitude'].notnull())
                         & (df['Longitude'].notnull())
                         ] 
    # [124382 rows x 35 columns]
    
    # get the NYC region from each
    lats = filtered_df['Latitude'].tolist()
    longs = filtered_df['Longitude'].tolist()
    return lats, longs

def load_data():
    """Load the latitude and longitude coordinates from np arrays"""
    lats = np.load('DATA/lats.npy')
    longs = np.load('DATA/longs.npy')
    return lats, longs

def load_gdf():
    """Create a geodataframe"""
    # read the borough data
    borough_data = gpd.read_file('DATA/new-york-city-boroughs.geojson')

    # load the np arrays
    lats, longs = load_data()

    # Define a dictionary that maps each borough name to its population density (per square mile)
    population_density_map = {
        'Manhattan': 74781	,         
        'Brooklyn': 39438, 
        'Queens': 22125,         
        'Bronx': 34920,
        'Staten Island': 8618 
        }

    # Add a new column 'population_per_sq_mile' to the borough_data GeoDataFrame
    borough_data['population_per_sq_mile'] = borough_data['name'].map(population_density_map)

    # Create a pandas DataFrame from your numpy arrays
    crime_data = pd.DataFrame({'latitude': lats, 'longitude': longs})

    # Combine the latitudes and longitudes into a 'geometry' column with Shapely Point objects
    crime_data['geometry'] = crime_data.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

    # Convert the pandas DataFrame into a GeoPandas GeoDataFrame
    crime_gdf = gpd.GeoDataFrame(crime_data, crs='EPSG:4326')

    # Perform the spatial join
    crime_with_borough_gdf = gpd.sjoin(crime_gdf, borough_data[['geometry', 'name', 'population_per_sq_mile']], how='left', op='within')

    # Print the first few rows of the result
    return crime_with_borough_gdf
     
