"""Performs computations over the latitude and longitude of crimes in NYC."""
from scipy.spatial import cKDTree
from sklearn.neighbors import KernelDensity
import numpy as np

def compute_kde(route_gdf, crime_gdf, bandwidth=0.001):
    """Compute the kernel density estimate of crimes along a route."""
    xy_route = np.vstack([route_gdf.geometry.x, route_gdf.geometry.y]).T
    xy_data = np.vstack([crime_gdf.geometry.x, crime_gdf.geometry.y]).T
    
    kde = KernelDensity(bandwidth=bandwidth, metric='haversine')
    kde.fit(np.radians(xy_data))
    
    log_density = kde.score_samples(np.radians(xy_route))
    density = np.exp(log_density)
   
    return density

def compute_safety(routes, crime_gdf):
    """Rank the routes by safety (average crime density of route).""" 
    route_kde_values = {}
    for idx, (route_name, route_gdf) in enumerate(routes.items()):
        route_kde = compute_kde(route_gdf, crime_gdf)
        route_kde_values[route_name] = np.mean(route_kde)

    safety_ranking = sorted(route_kde_values.items(), key=lambda x: x[1])
    # print(f"safety ranking: {safety_ranking}")
    return safety_ranking

