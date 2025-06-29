import streamlit as st
import pandas as pd
from src.satellite_tracking import get_satellite_position, get_available_satellites
from src.satellite_pass_ui import predict_passes
from src.orbit_visualization import generate_orbit_plot

# --- Streamlit config ---
st.set_page_config(page_title="Satellite Tracker", layout="wide")
st.title("🛰️ Satellite Tracker Dashboard")

# --- Sidebar ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🛰 Real-Time Tracker", "📡 Pass Predictor", "🌍 Orbit Visualizer"])

# Load satellite list dynamically
try:
    all_sats = get_available_satellites()
    sat_name = st.sidebar.selectbox("Select Satellite", options=all_sats, index=0)
except Exception as e:
    st.sidebar.error(f"Could not load satellites. Defaulting to ISS.")
    sat_name = "ISS (ZARYA)"

# Optional: Auto-refresh for Real-Time tab
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 15s", value=False)

# --- Real-Time Tracker ---
if page == "🛰 Real-Time Tracker":
    st.subheader("Live Satellite Position")

    try:
        lat, lon, alt = get_satellite_position(sat_name)
        st.write(f"**Latitude:** {lat:.2f}°")
        st.write(f"**Longitude:** {lon:.2f}°")
        st.write(f"**Altitude:** {alt:.2f} km")

        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=1)

        if auto_refresh:
            st.experimental_rerun()  # refresh the app loop

    except Exception as e:
        st.error(f"Error retrieving satellite position: {e}")

# --- Pass Predictor ---
elif page == "📡 Pass Predictor":
    st.subheader("Predict Satellite Passes")

    lat = st.number_input("Your Latitude", value=51.05, key="pass_lat")
    lon = st.number_input("Your Longitude", value=-114.07, key="pass_lon")
    hours = st.slider("Look Ahead (Hours)", 1, 72, 24, key="pass_hours")

    if st.button("Predict Passes", key="predict_btn"):
        with st.spinner("Calculating..."):
            passes = predict_passes(sat_name, lat, lon, hours)
            if passes:
                st.success(f"Upcoming passes for {sat_name}:")
                st.table(passes)
            else:
                st.warning("No visible passes found.")

# --- Orbit Visualizer ---
elif page == "🌍 Orbit Visualizer":
    st.subheader("Orbit Visualizer")

    minutes = st.slider("Orbit Duration (minutes)", 10, 120, 90, key="orbit_duration")
    view_mode = st.radio("Select View", ["🌀 3D Orbit Plot (Plotly)", "🌐 CesiumJS Globe"], key="orbit_view")

    if st.button("Generate Orbit", key="orbit_btn"):
        if view_mode == "🌀 3D Orbit Plot (Plotly)":
            try:
                fig = generate_orbit_plot(sat_name, minutes)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(str(e))
        else:
            st.info("🌐 CesiumJS integration is coming soon.")
