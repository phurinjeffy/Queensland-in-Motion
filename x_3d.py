import numpy as np
import pandas as pd

# Define column names based on .dfn structure
cols = [
    'line', 'dateCode', 'flight', 'survey', 'FID',
    'altitude', 'bearing', 'gpshgt', 'ground', 'lasalt',
    'latitude', 'longitude', 'radalt'
]

# Load data
df = pd.read_csv('data/P1152-line-elevation.dat', delim_whitespace=True, header=None, names=cols)

# Drop nulls / replace large null values with np.nan
df.replace([-9999999, -99999999, -999999, -9.999999e+32, -9.9999999999e+32], np.nan, inplace=True)
df.dropna(subset=['latitude', 'longitude', 'ground'], inplace=True)

from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Prepare arrays
points = df[['longitude', 'latitude']].values
values = df['ground'].values

# Create a grid
lon_lin = np.linspace(df['longitude'].min(), df['longitude'].max(), 300)
lat_lin = np.linspace(df['latitude'].min(), df['latitude'].max(), 300)
lon_grid, lat_grid = np.meshgrid(lon_lin, lat_lin)

# Interpolate the ground height values
elevation_grid = griddata(points, values, (lon_grid, lat_grid), method='linear')

# Plot the terrain
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(lon_grid, lat_grid, elevation_grid, cmap='terrain')
ax.set_title("Queensland Terrain Elevation")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_zlabel("Elevation (m)")
plt.show()
