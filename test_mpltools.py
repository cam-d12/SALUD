import mpl_toolkits.basemap as Basemap
import matplotlib.pyplot as plt

# Create a new figure
fig = plt.figure(figsize=(8, 8))

# Create a new basemap instance
m = Basemap.Basemap(projection='ortho', lat_0=0, lon_0=0)

# Draw the coastlines, countries and boundaries
m.drawcoastlines(linewidth=0.5)
m.drawcountries(linewidth=0.5)
m.drawmapboundary(fill_color='lightblue')

# Show the plot
plt.show()




p