import numpy as np
import rasterio
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
from scipy.ndimage import label
from collections import Counter
from scipy.spatial import cKDTree


def detect_water_regions(dem_path):
    """
    Detects and visualizes water regions using nearest neighbor clustering and Connected Component Analysis (CCA).
    :param dem_path: Path to the DEM file
    """
    # Load DEM data
    with rasterio.open(dem_path) as src:
        dem_data = src.read(1)
        profile = src.profile

    # Handle no-data values
    dem_data = np.where(dem_data == src.nodata, np.nan, dem_data)

    # Exclude zero and NaN values
    valid_indices = np.argwhere(~np.isnan(dem_data) & (dem_data > 0))
    valid_values = dem_data[~np.isnan(dem_data) & (dem_data > 0)]

    # Build KDTree for nearest neighbor search
    tree = cKDTree(valid_indices)

    # Find the most common elevations among nearest neighbors
    elevation_counts = Counter(valid_values)
    most_common_elevations = [elev for elev, count in elevation_counts.most_common(20)]

    # Identify the best elevation that forms the largest connected region
    best_elevation = None
    max_region_count = 0
    best_labeled_regions = None

    for elevation in most_common_elevations:
        elevation_mask = (dem_data == elevation)
        labeled_regions, num_regions = label(elevation_mask)

        # Find largest connected region
        if num_regions > max_region_count:
            max_region_count = num_regions
            best_elevation = elevation
            best_labeled_regions = labeled_regions

    # Plot the detected water regions
    plt.figure(figsize=(10, 6))
    plt.imshow(best_labeled_regions, cmap='tab20', interpolation='nearest')
    plt.colorbar(label=f"Connected Water Bodies at {best_elevation}m")
    plt.title(f"Detected Water Regions at Elevation {best_elevation}m (Total: {max_region_count})")
    plt.show()

    print(f"Selected elevation: {best_elevation}m")
    print(f"Total detected water regions: {max_region_count}")


# Membaca file DEM
file_path = "D:\\maps\\ASTGTMV003_S09E116_dem.tif"
detect_water_regions(file_path)

