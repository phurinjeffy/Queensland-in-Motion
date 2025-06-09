import numpy as np
import pandas as pd
import xarray as xr
import plotly.graph_objects as go

# === Load and interpolate DEM ===
cols = [
    'line', 'dateCode', 'flight', 'survey', 'FID',
    'altitude', 'bearing', 'gpshgt', 'ground', 'lasalt',
    'latitude', 'longitude', 'radalt'
]
df = pd.read_csv("data/P1152-line-elevation.dat", sep=r'\s+', header=None, names=cols)
df.replace([-9999999, -99999999, -999999, -9.999999e+32, -9.9999999999e+32], np.nan, inplace=True)
df.dropna(subset=['latitude', 'longitude', 'ground'], inplace=True)

# Define interpolation grid (matching Queensland)
num_points = 200
lon_lin = np.linspace(df['longitude'].min(), df['longitude'].max(), num_points)
lat_lin = np.linspace(df['latitude'].min(), df['latitude'].max(), num_points)

# === Load and interpolate solar radiation for 2020–2024 ===
YEARS = [2020, 2021, 2022, 2023, 2024]
radiation_surfaces_by_month = [[] for _ in range(12)]  # Jan to Dec

for year in YEARS:
    ds = xr.open_dataset(f"data/solar/{year}.radiation.nc")
    var = list(ds.data_vars)[0]
    radiation = ds[var]
    times = pd.to_datetime(radiation['time'].values)

    # Interpolate to consistent grid
    radiation_interp = radiation.interp(
        lon=xr.DataArray(lon_lin, dims="lon"),
        lat=xr.DataArray(lat_lin, dims="lat"),
        method="linear"
    )

    # Collect monthly data
    for month in range(1, 13):
        month_idxs = np.where(times.month == month)[0]
        if len(month_idxs) == 0:
            continue
        month_data = radiation_interp.isel(time=month_idxs).mean(dim='time', skipna=True)
        radiation_surfaces_by_month[month - 1].append(month_data.values)

# Compute 5-year monthly averages
radiation_surfaces = []
month_labels = []
for month_idx in range(12):
    if len(radiation_surfaces_by_month[month_idx]) == 0:
        continue
    stacked = np.stack(radiation_surfaces_by_month[month_idx])
    monthly_avg = np.nanmean(stacked, axis=0)
    radiation_surfaces.append(monthly_avg)
    month_labels.append(pd.Timestamp(f"2020-{month_idx+1:02d}-01").strftime('%B'))

# Color scale configuration
fixed_zmin = np.min([np.nanmin(surface) for surface in radiation_surfaces])
fixed_zmax = np.max([np.nanmax(surface) for surface in radiation_surfaces])

custom_colorscale = [
    [0.0,  "rgb(70,130,180)"],    # steel blue (low radiation)
    [0.3,  "rgb(173,216,230)"],   # light blue
    [0.5,  "rgb(255,255,150)"],   # soft warm yellow
    [0.7,  "rgb(255,165,0)"],     # orange
    [1.0,  "rgb(255,69,0)"]       # red (high radiation)
]

# === City coordinates for annotations ===
city_locs = {
    "Brisbane":   {"lon": 153.0351, "lat": -27.4550},
    "Gold Coast": {"lon": 153.4482, "lat": -28.0815},
    "Townsville": {"lon": 146.7700, "lat": -19.2499},
    "Cairns":     {"lon": 145.7633, "lat": -16.8878}
}

# Prepare hover text from January
z_data = radiation_surfaces[0]
custom_text = np.empty(z_data.shape, dtype=object)
for i in range(z_data.shape[0]):
    for j in range(z_data.shape[1]):
        val = z_data[i, j]
        if np.isnan(val):
            custom_text[i, j] = (
                f"Longitude: {lon_lin[j]:.3f}°<br>" +
                f"Latitude: {lat_lin[i]:.3f}°<br>" +
                "Radiation: NaN MJ/m²"
            )
        else:
            custom_text[i, j] = (
                f"Longitude: {lon_lin[j]:.3f}°<br>" +
                f"Latitude: {lat_lin[i]:.3f}°<br>" +
                f"Radiation: {val:.2f} MJ/m²"
            )

# === Plotting ===
initial_heat = go.Heatmap(
    z=z_data,
    x=lon_lin,
    y=lat_lin,
    colorscale=custom_colorscale,
    zmin=fixed_zmin,
    zmax=fixed_zmax,
    colorbar=dict(title="Solar Radiation (MJ/m²)"),
    showscale=True,
    text=custom_text,
    hovertemplate="%{text}<extra></extra>"
)

fig = go.Figure(data=[initial_heat])

# Add city markers
for city, coords in city_locs.items():
    fig.add_trace(
        go.Scatter(
            x=[coords["lon"]],
            y=[coords["lat"]],
            mode="markers+text",
            marker=dict(color="black", size=6, symbol="circle"),
            text=[city],
            textposition="top center",
            textfont=dict(size=12, color="black"),
            showlegend=False,
            hoverinfo="skip"
        )
    )

# === Prepare frames for animation ===
frames = []
for i, (surface, label) in enumerate(zip(radiation_surfaces, month_labels)):
    # Create hover text for each frame
    frame_text = np.empty(surface.shape, dtype=object)
    for row in range(surface.shape[0]):
        for col in range(surface.shape[1]):
            val = surface[row, col]
            if np.isnan(val):
                frame_text[row, col] = (
                    f"Longitude: {lon_lin[col]:.3f}°<br>" +
                    f"Latitude: {lat_lin[row]:.3f}°<br>" +
                    "Radiation: NaN MJ/m²"
                )
            else:
                frame_text[row, col] = (
                    f"Longitude: {lon_lin[col]:.3f}°<br>" +
                    f"Latitude: {lat_lin[row]:.3f}°<br>" +
                    f"Radiation: {val:.2f} MJ/m²"
                )

    frames.append(go.Frame(
        data=[
            go.Heatmap(
                z=surface,
                x=lon_lin,
                y=lat_lin,
                colorscale=custom_colorscale,
                zmin=fixed_zmin,
                zmax=fixed_zmax,
                colorbar=dict(title="Solar Radiation (MJ/m²)"),
                text=frame_text,
                hovertemplate="%{text}<extra></extra>"
            )
        ],
        name=label
    ))
    
# Compass center point (adjust lon/lat as needed for top-right)
compass_center_lon = lon_lin[-5]
compass_center_lat = lat_lin[-5]
offset = 0.5  # degrees for spacing

# Define compass directions
compass_points = {
    "N": (compass_center_lon, compass_center_lat + offset + 0.1),
    "E": (compass_center_lon + offset + 0.1, compass_center_lat),
    "S": (compass_center_lon, compass_center_lat - offset - 0.2),
    "W": (compass_center_lon - offset - 0.1, compass_center_lat)
}

# Add NESW labels as separate scatter trace
for direction, (lon, lat) in compass_points.items():
    fig.add_trace(go.Scatter(
        x=[lon],
        y=[lat],
        mode="text",
        text=[direction],
        textfont=dict(size=14, color="black"),
        showlegend=False,
        hoverinfo="skip"
    ))

# Add cross lines for the compass
fig.add_trace(go.Scatter(
    x=[compass_center_lon, compass_center_lon],
    y=[compass_center_lat - offset * 0.75, compass_center_lat + offset * 0.75],
    mode="lines",
    line=dict(color="black", width=1),
    showlegend=False,
    hoverinfo="skip"
))
fig.add_trace(go.Scatter(
    x=[compass_center_lon - offset * 0.75, compass_center_lon + offset * 0.75],
    y=[compass_center_lat, compass_center_lat],
    mode="lines",
    line=dict(color="black", width=1),
    showlegend=False,
    hoverinfo="skip"
))

# Update layout with animation config
fig.update(frames=frames)

fig.update_layout(
    title="Average Monthly Solar Radiation in Queensland (2020-2024)",
    xaxis_title="Longitude",
    yaxis_title="Latitude",
    height=900,
    width=1000,
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "Play", "method": "animate", "args": [None, {
                "frame": {"duration": 1000, "redraw": True},
                "fromcurrent": True,
                "transition": {"duration": 300, "easing": "linear"}
            }]},
            {"label": "Pause", "method": "animate", "args": [[None], {
                "frame": {"duration": 0, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0}
            }]}
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 80},
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }],
    sliders=[{
        "active": 0,
        "pad": {"t": 60},
        "x": 0.1,
        "len": 0.9,
        "xanchor": "left",
        "y": 0,
        "yanchor": "top",
        "steps": [{
            "label": label,
            "method": "animate",
            "args": [[label], {
                "mode": "immediate",
                "frame": {"duration": 500, "redraw": True},
                "transition": {"duration": 300}
            }]
        } for label in month_labels]
    }]
)

fig.write_html("solar_radiation_animation.html")
