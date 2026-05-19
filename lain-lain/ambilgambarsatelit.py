import ee
import geemap
import matplotlib.pyplot as plt
import numpy as np

plt.switch_backend('qt5agg')

# --- Inisialisasi ---
ee.Authenticate()
ee.Initialize(project='embung-477900')

roi = ee.Geometry.Point([112.7521, -7.2575]).buffer(2000)

# --- Koleksi citra utama dan awan ---
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')

# --- Gabungkan citra dan mask awan berdasarkan probabilitas ---
def mask_s2_clouds(img):
    cloud_prob = ee.Image(
        clouds.filter(ee.Filter.eq('system:index', img.get('system:index'))).first()
    )
    cloud_mask = cloud_prob.select('probability').lt(30)  # hanya <30% awan
    return img.updateMask(cloud_mask).divide(10000)

# --- Filter waktu & area, lalu gabungkan ---
collection = (
    s2.filterBounds(roi)
      .filterDate('2024-01-01', '2025-12-31')
      .map(mask_s2_clouds)
      .sort('system:time_start', False)
)

# --- Buat komposit bebas awan ---
composite = collection.mosaic()

# --- Ambil RGB ---
rgb = composite.select(['B4', 'B3', 'B2'])

# --- Konversi ke NumPy ---
rgb_data = geemap.ee_to_numpy(rgb, region=roi, scale=10)
rgb_data = np.nan_to_num(rgb_data, nan=0)

# --- Stretch kontras ---
valid = rgb_data[rgb_data > 0]
if valid.size > 0:
    p2, p98 = np.percentile(valid, (2, 98))
    rgb_stretch = np.clip((rgb_data - p2) / (p98 - p2), 0, 1)
else:
    rgb_stretch = rgb_data

plt.figure(figsize=(8, 8))
plt.imshow(rgb_stretch)
plt.title("Citra Komposit Sentinel-2 (mask awan probabilitas <30%)")
plt.axis("off")
plt.show()
