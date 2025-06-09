import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# 1) Load elevation points
col_names = [
    "line", "dateCode", "flight", "survey", "FID",
    "altitude", "bearing", "gpshgt", "ground", "lasalt",
    "latitude", "longitude", "radalt"
]
df = pd.read_csv("data/P1152-line-elevation.dat", sep=r"\s+", header=None, names=col_names)

# Replace null values
df.replace({
    -9.9999999999e+32: np.nan,
    -9.9999999: np.nan,
    -9999999: np.nan
}, inplace=True)
df.dropna(subset=["latitude", "longitude", "ground"], inplace=True)

# 2) Determine bounds
minx, maxx = df["longitude"].min(), df["longitude"].max()
miny, maxy = df["latitude"].min(), df["latitude"].max()

# 3) Build interpolation grid
nx, ny = 800, 800
grid_lon = np.linspace(minx, maxx, nx)
grid_lat = np.linspace(miny, maxy, ny)
XI, YI = np.meshgrid(grid_lon, grid_lat)

# 4) Interpolate elevation
pts_lon = df["longitude"].to_numpy()
pts_lat = df["latitude"].to_numpy()
pts_elev = df["ground"].to_numpy()

grid_elev_lin = griddata(
    (pts_lon, pts_lat), pts_elev, (XI, YI), method="linear", fill_value=np.nan
)
grid_elev_near = griddata(
    (pts_lon, pts_lat), pts_elev, (XI, YI), method="nearest"
)

# Fill missing values
grid_elev = np.where(np.isnan(grid_elev_lin), grid_elev_near, grid_elev_lin)

# 5) Plot rasterized elevation
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(grid_elev, extent=[minx, maxx, miny, maxy], origin='lower', cmap='terrain')
ax.set_title("Interpolated Elevation Raster")
plt.colorbar(im, ax=ax, label='Elevation (m)')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()
