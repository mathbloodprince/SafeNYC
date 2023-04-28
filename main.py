#!/opt/homebrew/bin/python3
import argparse
import numpy as np
from visualizers import plot_crime_density
from gmaps import compute_directions
from data import load_gdf
from crime import compute_kde, compute_safety
import geopandas as gpd
from scipy.stats import gaussian_kde

if __name__ == '__main__':
    # parse the start and end addresses
    parser = argparse.ArgumentParser(description="A simple script to concatenate two strings.")
    parser.add_argument("start", type=str, help="Starting Location Address")
    parser.add_argument("end", type=str, help="Ending Location Address")
    parser.add_argument("mode", type=str, help="Mode of Transportation")
    args = parser.parse_args()
    start, end, mode = args.start, args.end, args.mode
    
    # compute all the directions and convert to geopandas dataframe
    routes = compute_directions(start, end, mode=mode)
    routes = [gpd.GeoDataFrame(geometry=gpd.points_from_xy([coord[1] for coord in route], [coord[0] for coord in route]), crs="EPSG:4326") for route in routes]
    routes = [route.to_crs(epsg=3857) for route in routes]
    routes = {f'Route_{idx + 1}': route for idx, route in enumerate(routes)}

    # load dataframe of crime data as geopandas dataframe
    crime_gdf = load_gdf()
    crime_gdf = crime_gdf.to_crs(epsg=3857)

    # fit a KDE to the crime_df -> normalize by population density and rescale
    coords = crime_gdf[['latitude', 'longitude']].values
    kde = gaussian_kde(coords.T)
    crime_gdf['kde_values'] = kde(coords.T)
    crime_gdf['kde_norm'] = crime_gdf['kde_values'] / crime_gdf['population_per_sq_mile']
    crime_gdf['kde_norm'] = (crime_gdf['kde_norm'] - crime_gdf['kde_norm'].min()) / (crime_gdf['kde_norm'].max() - crime_gdf['kde_norm'].min())

    safety_ranking = compute_safety(routes, crime_gdf) 

    # plot the crime density
    plot_crime_density(safety_ranking, routes, crime_gdf)

    




