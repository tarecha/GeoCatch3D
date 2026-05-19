import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
import rasterio
import queue


# Load the TIFF file
def load_tiff(file_path):
    with rasterio.open(file_path) as dataset:
        return dataset.read(1)  # Read the first band


# BFS function to find connected components of a given pixel value
def bfs_find_connected(matrix, start_x, start_y, target_value):
    rows, cols = matrix.shape
    visited = np.zeros_like(matrix, dtype=bool)
    result = np.zeros_like(matrix)  # Store the connected component

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4-connectivity
    q = queue.Queue()
    q.put((start_x, start_y))
    visited[start_x, start_y] = True

    while not q.empty():
        x, y = q.get()
        result[x, y] = target_value

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and not visited[nx, ny] and matrix[nx, ny] == target_value:
                visited[nx, ny] = True
                q.put((nx, ny))

    return result


# Identify the largest connected region for a specific pixel value
def find_connected_region(matrix, target_value):
    largest_component = np.zeros_like(matrix)
    visited_global = np.zeros_like(matrix, dtype=bool)
    rows, cols = matrix.shape

    for i in range(rows):
        for j in range(cols):
            if matrix[i, j] == target_value and not visited_global[i, j]:
                component = bfs_find_connected(matrix, i, j, target_value)
                if np.sum(component == target_value) > np.sum(largest_component == target_value):
                    largest_component = component
                visited_global |= (component == target_value)

    return largest_component


# Load the GDEM TIFF file
file_path = "D:\\maps\\ASTGTMV003_S09E116_dem.tif" # Pastikan ini sesuai dengan lokasi file Anda
dem_data = load_tiff(file_path)

# Define the target pixel value
target_pixel_value = 2020

# Find the connected region for the specific value
connected_region = find_connected_region(dem_data, target_pixel_value)

# Plot the original DEM and the BFS result
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

ax[0].imshow(dem_data, cmap="gray", interpolation="nearest")
ax[0].set_title("Original DEM")
ax[0].set_xticks([])
ax[0].set_yticks([])

ax[1].imshow(connected_region, cmap="coolwarm", interpolation="nearest")
ax[1].set_title(f"Connected Region for Elevation {target_pixel_value}")
ax[1].set_xticks([])
ax[1].set_yticks([])

plt.show()
