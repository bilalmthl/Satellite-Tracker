import streamlit as st
from skyfield.api import load, wgs84
from skyfield import almanac
import datetime

# Function to predict passes
def predict_passes(satellite_name='ISS (ZARYA)', lat=51.05, lon=-114.07, hours_ahead=24):
    ts = load.timescale()
    t0 = ts.now()
    t1 = ts.utc(t0.utc_datetime() + datetime.timedelta(hours=hours_ahead))

    stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
    satellites = load.tle_file(stations_url)
    satellite = {sat.name: sat for sat in satellites}.get(satellite_name)

    if not satellite:
        return []

    observer = wgs84.latlon(lat, lon)
    times, events = satellite.find_events(observer, t0, t1, altitude_degrees=10.0)
    event_names = ['rise', 'culminate', 'set']

    return [
        {
            'Event': event_names[e],
            'UTC Time': t.utc_strftime('%Y-%m-%d %H:%M:%S')
        }
        for t, e in zip(times, events)
    ]

# Streamlit UI
st.title("🛰️ Satellite Pass Predictor")

st.write("Predict when a satellite (e.g. ISS) will pass over your location in the next 24 hours.")

satellite_name = st.text_input("Satellite Name", value="ISS (ZARYA)")
lat = st.number_input("Latitude", value=51.05)
lon = st.number_input("Longitude", value=-114.07)
hours = st.slider("Hours ahead to search", min_value=1, max_value=72, value=24)

if st.button("Predict Passes"):
    with st.spinner("Calculating..."):
        passes = predict_passes(satellite_name, lat, lon, hours)
        if passes:
            st.success(f"Upcoming passes for {satellite_name}:")
            st.table(passes)
        else:
            st.warning("No passes found or invalid satellite name.")
