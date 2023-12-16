# Imports
import pandas as pd
import matplotlib.pyplot as plt
import re

import gpxpy

import folium
from IPython.display import display
import base64

import streamlit as st
from streamlit_folium import folium_static

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# load data file of activities
file_path = "./data_files/df_rockies.csv"
df = pd.read_csv(file_path)

base_path = "./Aida Strava download/"

# Function to extract coordinates
def extract_coords(gpx_path):
  fullpath = base_path + gpx_path
  try:
    with open(fullpath, 'r') as gpx_file:
      gpx = gpxpy.parse(gpx_file)
      point = gpx.tracks[0].segments[0].points[0]
      return point.latitude, point.longitude
  except Exception as e:
    print(f"Error processing file {filepath}: {e}")
    return None, None

# Apply the function and create new columns
df_rockies[['latitude', 'longitude']] = df_rockies['filename'].apply(lambda x: pd.Series(extract_coords(x)))

# Create a map instance
map = folium.Map(location=[df_rockies['latitude'].mean(), df_rockies['longitude'].mean()],
                 zoom_start=7,
                 tiles='OpenStreetMap',
                 width=1024,
                 height=600)

# Define marker colors for each activity type
colors = {
    'Ride': 'blue',
    'Hike': 'green',
    'Walk': 'red'
}


for item in gpx_list:
  gpx_index = re.search('activities/(.*).gpx', item).group(1)
  csv_filename = './data_files/data/route'+str(gpx_index)+'_df.csv'

# Add markers
for _, row in df_rockies.iterrows():
    resolution, width, height = 100, 3, 4

    img_string = row['media']
    if not pd.isna(img_string) and img_string[-4:] != ".mp4":

        # Get the activity description
        description = row['name']

        # Build the html iframe content
        html_stuff = f'''<p>{description}</p>'''

        img_locations = img_string.split('|')
        for loc in img_locations:
            input_path = f'./Aida Strava download/{loc}'
            Filename=f'./media/compressed/{loc[6:]}'
            encoded = base64.b64encode(open(Filename, 'rb').read())

            html_stuff +='<img src="data:image/jpeg;base64,{}">'.format(encoded.decode('UTF-8'))
            html_stuff += '<p></p>'

        # Create the HTML content for the iframe
        iframe = folium.IFrame(html_stuff, width=(width*resolution)+10, height=(height*resolution)+10)
        popup = folium.Popup(iframe, max_width=(width*resolution))
    else:
        popup = f"{row['type'].title()}"

    # add marker to map
    folium.Marker(
        location=[row['latitude'], row['longitude']],
#         popup=f"{row['type'].title()}",
        popup=popup,
        icon=folium.Icon(color=colors.get(row['type'], 'gray'))
    ).add_to(map)

    # read in csv file with coordinates of entire route
    gpx_file = row['filename']
    gpx_index = re.search('activities/(.*).gpx', gpx_file).group(1)
    csv_filename = './data_files/data/route'+str(gpx_index)+'_df.csv'
    route_df = pd.read_csv(csv_filename)
    coordinates = [tuple(x) for x in route_df[['latitude', 'longitude']].to_numpy()]

    # add routes to map
    folium.PolyLine(
        locations=coordinates,
        color=colors.get(row['type'], 'gray'),
        weight=2.5,
        opacity=1
    ).add_to(map)

# display(map)
# call to render Folium map in Streamlit
folium_static(map)
