import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')


# Data: ID, latitude, longitude, distance_to_river
data = [
    (1, -7.930556, 112.535000, 25.72),
    (2, -7.939167, 112.538056, 7.65),
    (3, -7.921667, 112.533056, 0.00),
    (4, -7.953611, 112.531111, 8.73),
    (5, -7.913889, 112.528611, 13.71),
    (6, -7.984167, 112.519444, 8.18),
    (6, -7.985278, 112.520833, 59.84),
    (7, -8.008889, 112.514444, 14.43),
    (8, -7.873056, 112.480000, 20.00),
    (8, -7.859167, 112.476667, 50.00),
    (8, -7.845278, 112.464722, 47.17),
    (8, -7.843333, 112.449444, 125.57),
    (9, -7.873056, 112.506667, 233.75),
    (9, -7.869444, 112.517500, 44.62),
    (10, -7.865556, 112.457222, 12.96),
    (10, -7.855278, 112.443333, 21.06),
    (10, -7.853333, 112.440556, 107.87),
    (11, -8.014167, 112.447222, 23.45),
    (12, -7.854167, 112.439167, 0.00),
    (13, -7.853056, 112.440556, 0.68),
    (14, -7.842778, 112.449167, 53.77),
    (15, -7.849444, 112.518611, 38.71),
    (16, -7.953056, 112.415556, 8.92),
    (17, -7.842778, 112.449167, 54.73),
    (18, -7.837778, 112.452222, 23.10)
]

# Buat DataFrame
df = pd.DataFrame(data, columns=['ID', 'Latitude', 'Longitude', 'Distance'])

# Plot histogram distribusi jarak ke sungai
plt.figure(figsize=(8,5))
plt.hist(df['Distance'], bins=20, edgecolor='black')
plt.xlabel('Distance to River (m)')
plt.ylabel('Number of Points')
plt.title('Histogram of outlet to river distances')
plt.grid(axis='y', alpha=0.75)
plt.tight_layout()
plt.show()
