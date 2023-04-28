import googlemaps
import polyline
from moviepy.editor import ImageSequenceClip
import os
import requests
import math

######## 1. Enter your API key here to use googlemaps with the crime density map ########
# KEY = 'YOUR_API_KEY'
gmaps = googlemaps.Client(key=KEY)

def compute_directions(start_address, end_address, mode="driving"):
    """Compute the polyline trajectory between a start and end address, recording the steps on the way."""
    directions_result = gmaps.directions(start_address, end_address, mode=mode, alternatives=True)
    
    overview_polylines = []
    for route in directions_result:
        encoded_polyline = route['overview_polyline']['points']
        decoded_polyline = polyline.decode(encoded_polyline)
        overview_polylines.append(decoded_polyline)
    return overview_polylines 
    
def calculate_heading(coord1, coord2):
    """Computes the camera heading for smoother frames"""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    d_lon = lon2 - lon1
    y = math.sin(d_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)

    heading = math.degrees(math.atan2(y, x))
    return (heading + 360) % 360

def get_street_view(coordinates):
    """From a list of coordinates, download Street View images and stitch them together into a video."""
    sampled_coordinates = coordinates[::1]  # Adjust the step size for more or fewer samples

    # Download Street View images for the sampled coordinates
    image_filenames = []
    for i, coord in enumerate(sampled_coordinates[:-1]):
        next_coord = sampled_coordinates[i + 1]
        heading = calculate_heading(coord, next_coord)
        street_view_url = f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={coord[0]},{coord[1]}&fov=90&heading={heading}&pitch=10&key={Key}"

        response = requests.get(street_view_url)
        
        if response.status_code == 200:
            filename = f"frame_{i:03d}.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            image_filenames.append(filename)
        else:
            print(f"Failed to download image for coordinates {coord}")

    # Create a video from the images
    clip = ImageSequenceClip(image_filenames, fps=5)  # Adjust 'fps' for desired frame rate
    clip.write_videofile("driving_video.mp4")

    # Clean up downloaded images
    for filename in image_filenames:
        os.remove(filename)

