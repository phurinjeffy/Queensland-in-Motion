import xarray as xr
import pandas as pd
import numpy as np
import plotly.graph_objects as go

CITY_COORDS = {
    "Brisbane":   {"lat": -27.4550, "lon": 153.0351},
    "Gold Coast": {"lat": -28.0815, "lon": 153.4482},
    "Townsville": {"lat": -19.2499, "lon": 146.7700},
    "Cairns":     {"lat": -16.8878, "lon": 145.7633}
}

MAX_TEMP_FILE = "data/2025.max_temp.nc"
MIN_TEMP_FILE = "data/2025.min_temp.nc"

def find_nearest_grid_point(ds: xr.DataArray, target_lat: float, target_lon: float):
    lat_diff = np.abs(ds["lat"].values - target_lat)
    lon_diff = np.abs(ds["lon"].values - target_lon)
    i_lat = lat_diff.argmin()
    i_lon = lon_diff.argmin()
    return float(ds["lat"].values[i_lat]), float(ds["lon"].values[i_lon])

def extract_time_series(
    max_ds: xr.Dataset,
    min_ds: xr.Dataset,
    city_name: str,
    city_coords: dict
):
    max_var = list(max_ds.data_vars)[0]
    min_var = list(min_ds.data_vars)[0]

    max_temp = max_ds[max_var]
    min_temp = min_ds[min_var]

    time_index = pd.to_datetime(max_temp["time"].values)

    tgt_lat, tgt_lon = city_coords["lat"], city_coords["lon"]
    nearest_lat, nearest_lon = find_nearest_grid_point(max_temp, tgt_lat, tgt_lon)

    max_ts = max_temp.sel(lat=nearest_lat, lon=nearest_lon, method="nearest").values
    min_ts = min_temp.sel(lat=nearest_lat, lon=nearest_lon, method="nearest").values

    return {
        "time": time_index,
        "max": max_ts,
        "min": min_ts,
        "grid_lat": nearest_lat,
        "grid_lon": nearest_lon,
    }


def generate_temp_figure(
    city_name: str,
    max_temp_file: str = MAX_TEMP_FILE,
    min_temp_file: str = MIN_TEMP_FILE
) -> None:
    if city_name not in CITY_COORDS:
        raise ValueError(f"City '{city_name}' not found. Options: {list(CITY_COORDS)}")

    # Load data
    max_ds = xr.open_dataset(max_temp_file)
    min_ds = xr.open_dataset(min_temp_file)

    series = extract_time_series(max_ds, min_ds, city_name, CITY_COORDS[city_name])
    times = series["time"]
    max_vals = series["max"]
    min_vals = series["min"]

    fig = go.Figure()

    # Max Temp (solid red)
    fig.add_trace(
        go.Scatter(
            x=times,
            y=max_vals,
            mode="lines",
            name="Max",
            line=dict(color="firebrick", width=2),
            hoverinfo="x+y"
        )
    )
    # Min Temp (dashed blue)
    fig.add_trace(
        go.Scatter(
            x=times,
            y=min_vals,
            mode="lines",
            name="Min",
            line=dict(color="royalblue", width=2, dash="dash"),
            hoverinfo="x+y"
        )
    )

    # Unified hover: single box, date appears once
    fig.update_layout(hovermode="x unified")

    # X-axis formatting: show day‐precision labels
    fig.update_layout(
        title=f"Daily Max & Min Temperatures in {city_name} (2025)",
        xaxis=dict(
            title="Date",
            tickformat="%d %b",
            dtick="M1",        # one tick every 1 calendar month (automatically on the 1st)
            tickangle=-45,
            showticklabels=True
        ),
        yaxis=dict(title="Temperature (°C)"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bordercolor="LightGray",
            borderwidth=1
        ),
        margin=dict(l=60, r=40, t=100, b=80),
        height=500,
        width=900
    )

    output_filename = f"{city_name.lower().replace(' ', '_')}_temps.html"
    fig.write_html(output_filename)
    print(f"Saved figure for {city_name} to '{output_filename}'.")


if __name__ == "__main__":
    generate_temp_figure("Brisbane")
    # generate_temp_figure("Gold Coast")
    # generate_temp_figure("Cairns")
    # generate_temp_figure("Townsville")
