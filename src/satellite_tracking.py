import streamlit as st
from skyfield.api import load, wgs84
import pandas as pd

st.title("Real-Time ISS Tracker")

# Load ISS data
stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
iss = {sat.name: sat for sat in satellites}['ISS (ZARYA)']

# Current position
ts = load.timescale()
t = ts.now()
geocentric = iss.at(t)
subpoint = geocentric.subpoint()

# Display current ISS position
st.write('### Current ISS Position:')
st.write(f"Latitude: {subpoint.latitude.degrees:.2f}°")
st.write(f"Longitude: {subpoint.longitude.degrees:.2f}°")
st.write(f"Altitude: {subpoint.elevation.km:.2f} km")

# Add a map visualization
df = pd.DataFrame({
    'lat': [subpoint.latitude.degrees],
    'lon': [subpoint.longitude.degrees]
})

st.map(df, zoom=1)
