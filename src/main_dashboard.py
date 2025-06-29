import streamlit as st
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import streamlit.components.v1 as components

from src.satellite_tracking import (
    get_available_satellites,
    get_satellite_position
)
from src.satellite_pass_ui import predict_passes
from src.orbit_visualization import generate_orbit_plot

# --------- Satellite Type Grouping ---------
def get_satellite_type(name):
    name = name.upper()
    if "STARLINK" in name:
        return "Starlink"
    elif "NAVSTAR" in name or "GPS" in name:
        return "GPS/NAVSTAR"
    elif "ISS" in name:
        return "ISS"
    elif "TIANHE" in name or "CSS" in name or "SHENZHOU" in name:
        return "Chinese Station"
    elif "FREGAT" in name or "DEB" in name:
        return "Debris"
    else:
        return "Other"

# --------- Page Config ---------
st.set_page_config(page_title="Satellite Tracker", layout="wide")
st.title("🚀 Satellite Tracker Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🚀 Real-Time Tracker", "📡 Pass Predictor", "🌍 Orbit Visualizer"])

auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 15s", value=False)
if auto_refresh and page == "🚀 Real-Time Tracker":
    st_autorefresh(interval=15000, key="refresh")

# --------- Satellite Selection ---------
try:
    all_sats = get_available_satellites()
    multi_select = st.sidebar.checkbox("🔣 Multi-satellite mode", value=False)

    if multi_select:
        sat_choices = st.sidebar.multiselect("Select Satellites", options=all_sats, default=["ISS (ZARYA)"])
    else:
        sat_choices = [st.sidebar.selectbox("🔍 Search & Select Satellite", options=all_sats, index=0)]
except Exception as e:
    st.sidebar.error("Could not load satellites.")
    sat_choices = ["ISS (ZARYA)"]

# --------- Real-Time Tracker ---------
if page == "🚀 Real-Time Tracker":
    st.subheader("Live Satellite Positions")
    raw_positions = []
    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    for name in sat_choices:
        try:
            lat, lon, alt = get_satellite_position(name)
            raw_positions.append({
                'Satellite': name,
                'Latitude': lat,
                'Longitude': lon,
                'Altitude': alt,
                'Type': get_satellite_type(name)
            })
        except Exception as e:
            st.warning(f"{name}: {e}")

    df = pd.DataFrame(raw_positions)
    df['LatRound'] = df['Latitude'].round(1)
    df['LonRound'] = df['Longitude'].round(1)

    grouped = (
        df.groupby(['LatRound', 'LonRound', 'Type'])
        .agg({
            'Satellite': lambda x: ', '.join(sorted(set(x))),
            'Latitude': 'mean',
            'Longitude': 'mean'
        })
        .reset_index()
    )

    if not grouped.empty:
        fig = px.scatter_map(
            grouped,
            lat="Latitude",
            lon="Longitude",
            color="Type",
            hover_name="Satellite",
            zoom=1,
            height=500
        )
        fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No valid satellite positions found.")

    st.markdown(f"<p style='color:gray;font-size:0.9em;'>🕒 Last updated: {now} UTC</p>", unsafe_allow_html=True)

# --------- Pass Predictor ---------
elif page == "📡 Pass Predictor":
    st.subheader("Predict Satellite Passes")

    lat = st.number_input("Your Latitude", value=51.05)
    lon = st.number_input("Your Longitude", value=-114.07)
    hours = st.slider("Look Ahead (Hours)", 1, 72, 24)

    if st.button("Predict Passes", key="predict_btn"):
        for sat_name in sat_choices:
            with st.spinner(f"Calculating passes for {sat_name}..."):
                try:
                    passes = predict_passes(sat_name, lat, lon, hours)
                    st.markdown(f"### 📡 Passes for `{sat_name}`")
                    if passes:
                        st.table(passes)
                    else:
                        st.warning("No visible passes.")
                except Exception as e:
                    st.error(f"Error for {sat_name}: {e}")

# --------- Orbit Visualizer ---------
elif page == "🌍 Orbit Visualizer":
    st.subheader("3D Orbit Visualizer")
    minutes = st.slider("Orbit Duration (minutes)", 10, 120, 90)
    view_mode = st.radio("Select View", ["🌀 3D Orbit Plot (Plotly)", "🌐 CesiumJS Globe"])

    if st.button("Generate Orbit", key="orbit_btn"):
        for sat_name in sat_choices:
            st.markdown(f"### 🚐 Orbit: `{sat_name}`")
            if view_mode == "🌀 3D Orbit Plot (Plotly)":
                try:
                    fig = generate_orbit_plot(sat_name, minutes)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(str(e))
            else:
                st.info("🌐 CesiumJS Globe is coming soon. Stay tuned!")
