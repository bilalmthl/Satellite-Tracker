from skyfield.api import load, wgs84
import plotly.graph_objects as go
import datetime

def generate_orbit_plot(satellite_name, minutes=90):
    # Load TLE data
    tle_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle'
    sats = load.tle_file(tle_url)
    sat_dict = {sat.name: sat for sat in sats}

    if satellite_name not in sat_dict:
        raise ValueError(f"{satellite_name} not found in TLE file.")

    sat = sat_dict[satellite_name]
    ts = load.timescale()
    t0 = ts.now()
    t1 = ts.utc(t0.utc_datetime() + datetime.timedelta(minutes=minutes))
    t_array = ts.linspace(t0, t1, minutes)

    positions = sat.at(t_array)
    subpoints = positions.subpoint()

    lats = subpoints.latitude.degrees
    lons = subpoints.longitude.degrees
    alts = subpoints.elevation.km

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=lons,
        y=lats,
        z=alts,
        mode='lines+markers',
        marker=dict(
            size=4,
            color=alts,
            colorscale='Viridis',
            colorbar=dict(title='Altitude (km)'),
        ),
        line=dict(width=2, color='blue'),
        name=satellite_name,
        hoverinfo='text',
        text=[
            f"{satellite_name}<br>Lat: {lat:.2f}°<br>Lon: {lon:.2f}°<br>Alt: {alt:.2f} km"
            for lat, lon, alt in zip(lats, lons, alts)
        ]
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude (km)',
            aspectmode='data'
        ),
        title=f"{satellite_name} Orbit (Color by Altitude)",
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig
