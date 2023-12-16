# Imports
import pandas as pd
import matplotlib.pyplot as plt
import re

import gpxpy

import folium
import base64

import streamlit as st
from streamlit_folium import folium_static

APP_TITLE = 'Adventures in the Canadian Rockies'
APP_SUB_TITLE = "Aug '23"

st.set_page_config(APP_TITLE)
st.title(APP_TITLE)
st.header(APP_SUB_TITLE)

# Add image at top
image_path = './media/jagged_peaks.jpg'
st.image(image_path, caption='Intrepid hikers')

# load data file of activities
file_path = "./data_files/df_rockies.csv"
df_rockies = pd.read_csv(file_path)

# Create a map instance
map = folium.Map(location=[46.538584, -86.430602],
                 zoom_start=4,
                 tiles='OpenStreetMap',
                 width=1024,
                 height=600)

# Define marker colors for each activity type
colors = {
    'Ride': 'blue',
    'Hike': 'green',
    'Walk': 'red'
}

gpx_list = df_rockies['filename'].tolist()
for item in gpx_list:
  gpx_index = re.search('activities/(.*).gpx', item).group(1)
  csv_filename = './data_files/data/route'+str(gpx_index)+'_df.csv'

# Add markers
for _, row in df_rockies.iterrows():
    resolution, width, height = 100, 3, 4

    img_string = row['media']
    if not pd.isna(img_string) and img_string[-4:] != ".mp4":

        # Get the activity description
        activity_description = row['description']
        # Get the distance and elevation gain
        distance = row['distance_km']
        elev_gain = round(row['elev_gain'])
        stats = f'Distance: {distance} km, Elevation gain: {elev_gain} m'

        # Build the html iframe content
        html_stuff = f'''<p>{activity_description}</p><p>{stats}</p>'''

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

    activity_type = row['type']
    activity_name = row['name']
    # add marker to map
    marker = folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup,
        icon=folium.Icon(color=colors.get(row['type'], 'gray')),
        tooltip = f'{activity_type}: {activity_name}'
    )
    marker.add_to(map)

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

# add marker for Oakville to map
marker_oakville = folium.Marker(
    location=[43.484830, -79.687418],
    icon=folium.Icon(color='gray'),
    tooltip='Toronto'
)
marker_oakville.add_to(map)

# display(map)
# call to render Folium map in Streamlit
folium_static(map)
