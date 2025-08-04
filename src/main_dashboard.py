import streamlit as st
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

from src.satellite_tracking import (
    get_available_satellites,
    get_satellite_position,
    get_satellite_metadata
)
from src.satellite_pass_ui import predict_passes
from src.orbit_visualization import generate_orbit_plot

# --------- Page Config ---------
st.set_page_config(
    page_title="Satellite Tracker",
    page_icon="🛰️",
    layout="wide"
)

# --------- Sidebar Logo & Navigation ---------
with st.sidebar:
    # Logo and App Name
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:5px;">
          <h2 style="margin:0;">🛰️ Satellite Tracker</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Navigation
    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["🚀 Real-Time Tracker", "📡 Pass Predictor", "🌍 Orbit Visualizer"],
        index=0,
    )
    auto_refresh = st.checkbox("🔄 Auto-refresh every 15 s", value=False)

    # Satellite type filter
    all_meta = get_available_satellites()
    all_types = sorted({m["type"] for m in all_meta})
    selected_types = st.multiselect(
        "Filter by Type",
        options=all_types,
        default=all_types
    )
    if not selected_types:
        selected_types = all_types

    st.markdown("---")
    st.write("### Satellite Selection")

    # Persisted selection state
    if "sat_choices" not in st.session_state:
        st.session_state.sat_choices = ["ISS (ZARYA)"]

    filtered = [
        m["name"] for m in all_meta
        if m["type"] in selected_types
    ]

    multi = st.checkbox("🔣 Multi-satellite mode", value=True)
    if multi:
        defaults = [
            s for s in st.session_state.sat_choices
            if s in filtered
        ]
        st.session_state.sat_choices = st.multiselect(
            "Choose satellites",
            options=filtered,
            default=defaults
        )
    else:
        if filtered:
            sel = st.selectbox("Choose one", options=filtered, index=0)
            st.session_state.sat_choices = [sel]
        else:
            st.session_state.sat_choices = []

    # Auto-refresh only on Real-Time page
    if auto_refresh and page == "🚀 Real-Time Tracker":
        st_autorefresh(interval=15_000, key="refresh")


# --------- Timestamp Footer Helper ---------
def footer_timestamp():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    st.markdown(
        f"<p style='color:gray;font-size:0.9em;'>🕒 Last updated: {now}</p>",
        unsafe_allow_html=True
    )


# --------- Real-Time Tracker ---------
if page == "🚀 Real-Time Tracker":
    st.subheader("Live Satellite Positions")
    rows = []
    for name in st.session_state.sat_choices:
        try:
            lat, lon, alt = get_satellite_position(name)
            meta = get_satellite_metadata(name)
            rows.append({
                "name":  name,
                "lat":   lat,
                "lon":   lon,
                "alt":   alt,
                "type":  meta["type"],
                "image": meta.get("image_url")
            })
        except Exception as e:
            st.warning(f"{name}: {e}")

    if rows:
        df = pd.DataFrame(rows)
        df["LatR"] = df.lat.round(1)
        df["LonR"] = df.lon.round(1)

        grouped = (
            df.groupby(["LatR", "LonR", "type"])
              .agg({
                  "name":  lambda x: ", ".join(sorted(x)),
                  "lat":   "mean",
                  "lon":   "mean",
                  "image": lambda imgs: next((u for u in imgs if u), None)
              })
              .reset_index()
        )

        # Bigger map + tighter footer margin
        fig = px.scatter_map(
            grouped,
            lat="lat",
            lon="lon",
            color="type",
            hover_name="name",
            zoom=1,
            height=600
        )
        fig.update_layout(margin={"r":0, "t":0, "l":0, "b":60})
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div style='margin-top:5px'></div>", unsafe_allow_html=True)

        for sat in rows:
            cols = st.columns([3,1])
            with cols[0]:
                st.write(f"**{sat['name']}**  ·  *{sat['type']}*")
                st.write(f"{sat['lat']:.3f}°, {sat['lon']:.3f}°  |  {sat['alt']:.1f} km")
            with cols[1]:
                if sat["image"]:
                    st.image(sat["image"], width=300)
                    st.caption(sat["name"])
                else:
                    st.write("_No image available_")
    else:
        st.warning("No satellites selected or data unavailable.")

    footer_timestamp()


# --------- Pass Predictor ---------
elif page == "📡 Pass Predictor":
    st.subheader("Predict Satellite Passes")
    lat = st.number_input("Your Latitude", value=51.05)
    lon = st.number_input("Your Longitude", value=-114.07)
    hours = st.slider("Look Ahead (hours)", 1, 72, 24)

    if st.button("Predict Passes"):
        for name in st.session_state.sat_choices:
            with st.spinner(f"Calculating passes for {name}…"):
                try:
                    table = predict_passes(name, lat, lon, hours)
                    st.markdown(f"#### 📡 {name}")
                    if table:
                        st.table(table)
                    else:
                        st.warning("No visible passes.")
                except Exception as e:
                    st.error(str(e))

    footer_timestamp()


# --------- Orbit Visualizer ---------
elif page == "🌍 Orbit Visualizer":
    st.subheader("3D Orbit Visualizer")
    duration = st.slider("Duration (minutes)", 10, 120, 90)
    view = st.radio("View Mode", ["🌀 Plotly 3D", "🌐 CesiumJS (Coming Soon)"])

    if st.button("Generate Orbit"):
        for name in st.session_state.sat_choices:
            st.markdown(f"#### 🚐 {name}")
            if view.startswith("🌀"):
                try:
                    fig = generate_orbit_plot(name, duration)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(str(e))
            else:
                st.info("🌐 CesiumJS globe is coming soon. Stay tuned!")

    footer_timestamp()
