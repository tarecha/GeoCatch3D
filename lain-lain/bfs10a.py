import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')


# Data: ID, latitude, longitude, distance_to_river
data = [
    (1, -7.670556, 113.025, 66.37),
    (2, -7.673056, 113.028056, 69.38),
    (3, -7.696389, 113.030556, 73.11),
    (3, -7.696389, 113.030556, 74.11),
    (3, -7.696389, 113.030556, 75.11),
    (3, -7.696389, 113.030556, 76.11),
    (4, -7.695833, 113.038889, 228.63),
    (4, -7.695833, 113.038889, 229.63),
    (4, -7.695833, 113.038889, 230.63),
    (4, -7.695833, 113.038889, 231.63),
    (4, -7.695833, 113.038889, 232.63),
    (5, -7.701944, 113.041944, None),
    (5, -7.702778, 113.043056, None),
    (6, -7.754167, 112.990833, 7.11),
    (7, -7.753889, 113.031667, 167.41),
    (8, -7.748611, 113.040833, 477.74),
    (9, -7.754167, 113.053056, 200),
    (10, -7.750278, 113.061944, 58.16),
    (11, -7.761389, 112.9975, 417.92),
    (12, -7.760556, 113.026944, 103.45),
    (13, -7.765, 113.081667, 105.69),
    (14, -7.762222, 112.946389, 0),
    (15, -7.76, 112.962222, 0),
    (16, -7.758889, 112.969722, 105.5),
    (17, -7.764167, 113.0125, 134.4),
    (18, -7.766389, 113.086667, 68.27),
    (19, -7.776111, 113.105278, 0),
]
# Buat DataFrame
df = pd.DataFrame(data, columns=['ID', 'Latitude', 'Longitude', 'Distance'])

# Plot histogram distribusi jarak ke sungai
plt.figure(figsize=(8,5))
plt.hist(df['Distance'], bins=20, edgecolor='black')
plt.xlabel('Jarak (m)', fontsize=14)
plt.ylabel('Jumlah titik lokasi', fontsize=14)
plt.title('Offset jarak outlet minimal ke digitasi sungai Google Maps dan BIG', fontsize=18)
plt.grid(axis='y', alpha=0.75)
#plt.tight_layout()
plt.show()
