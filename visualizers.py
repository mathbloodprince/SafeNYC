import matplotlib.pyplot as plt
import contextily as ctx

def plot_crime_density(safety_ranking, routes, crime_gdf):
    """Plot the population scaled crime density of NYC, and the routes ranked by safety"""
    fig, ax = plt.subplots(figsize=(10, 10))
    sc = ax.scatter(crime_gdf.geometry.x, crime_gdf.geometry.y, c=crime_gdf['kde_norm'], cmap='viridis', marker='o', s=5, edgecolor='none')
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    cbar = fig.colorbar(sc, ax=ax, label='KDE values')
    ax.set_title('Kernel Density Estimate of Crime in New York City')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    for idx, (route_name, route_kde) in enumerate(safety_ranking):
        route_gdf = routes[route_name]
        route_gdf.plot(ax=ax, linewidth=0.01, label=f'{route_name} (Safety Rank {idx + 1})')

    ax.legend()
    plt.show()


