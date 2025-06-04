import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import plotly.graph_objects as go

# === Load and interpolate DEM from .dat ===
cols = [
    'line', 'dateCode', 'flight', 'survey', 'FID',
    'altitude', 'bearing', 'gpshgt', 'ground', 'lasalt',
    'latitude', 'longitude', 'radalt'
]
df = pd.read_csv("data/P1152-line-elevation.dat", sep=r'\s+', header=None, names=cols)
df.replace([-9999999, -99999999, -999999, -9.999999e+32, -9.9999999999e+32], np.nan, inplace=True)
df.dropna(subset=['latitude', 'longitude', 'ground'], inplace=True)

# Grid terrain
num_points = 200
lon_lin = np.linspace(df['longitude'].min(), df['longitude'].max(), num_points)
lat_lin = np.linspace(df['latitude'].min(), df['latitude'].max(), num_points)
lon_grid, lat_grid = np.meshgrid(lon_lin, lat_lin)

points = df[['longitude', 'latitude']].values
values = df['ground'].values
terrain_data = griddata(points, values, (lon_grid, lat_grid), method='linear')

# === Define major cities ===
cities = {
    "Brisbane": {"lat": -27.4550, "lon": 153.0351},
    "Gold Coast": {"lat": -28.0815, "lon": 153.4482},
    "Townsville": {"lat": -19.2499, "lon": 146.7700},
    "Cairns": {"lat": -16.8878, "lon": 145.7633}
}

city_names = list(cities.keys())
label_offset = 0.25  # degrees longitude (adjust if needed)

city_label_lons = [cities[name]["lon"] + label_offset for name in city_names]
city_label_lats = [cities[name]["lat"] for name in city_names]
city_label_zs = [
    griddata(points, values, (cities[name]["lon"], cities[name]["lat"]), method='linear') + 20
    for name in city_names
]

# === Build plotly figure ===
fig = go.Figure()

# Terrain surface
fig.add_trace(go.Surface(
    z=terrain_data,
    x=lon_lin,
    y=lat_lin,
    colorscale='Spectral',
    reversescale=True,
    cmin=-60,
    cmax=np.nanmax(terrain_data),
    showscale=True,
    colorbar=dict(title='Elevation (m)'),
    opacity=1.0,
    name='Digital Elevation Model',
    hovertemplate=
        "Longitude: %{x:.4f}<br>" +
        "Latitude: %{y:.4f}<br>" +
        "Elevation: %{z:.2f} m<extra></extra>"
))

# City markers
fig.add_trace(go.Scatter3d(
    x=city_label_lons,
    y=city_label_lats,
    z=city_label_zs,
    mode='markers+text',
    marker=dict(size=2, color='black'),
    text=city_names,
    textposition='middle right',
    textfont=dict(color='black', size=10),
    showlegend=False,
    name='Cities',
    hovertemplate=
        "%{text}<br>" +
        "Longitude: %{x:.4f}<br>" +
        "Latitude: %{y:.4f}<br>" +
        "Elevation: %{z:.2f} m<extra></extra>"
))

# Layout
fig.update_layout(
    title="Queensland - Terrain Elevation",
    scene=dict(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Elevation (m)',
        aspectratio=dict(x=1, y=1, z=0.3)
    ),
    width=1000,
    height=800,
    margin=dict(l=20, r=20, t=50, b=20)
)

# Save figure
fig.write_html("queensland_terrain_elevation.html")
