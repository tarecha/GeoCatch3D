import numpy as np
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
from modul import config as cfg
import rasterio

from scipy.ndimage import label, generate_binary_structure, binary_dilation

wbt = WhiteboxTools()


with rasterio.open(cfg.fileFlowAccumulationBreachThresholdKetinggian) as src:
    matrikFA = src.read(1)
    transform = src.transform

matrikFA[np.isnan(matrikFA)] = 0
matrikFA[np.isinf(matrikFA)] = 0
nilaiFAunik = np.unique(matrikFA.astype(int))
nilaiFAunik = nilaiFAunik[nilaiFAunik > 0][::-1]
print(nilaiFAunik.dtype)
# for row in nilaiFAunik:
#     print(f"nilaiFAunik {row}")

dynamicthreshold = np.percentile(nilaiFAunik, 80)
print(f"dynamicthreshold {dynamicthreshold}")
matrikFA[matrikFA < dynamicthreshold] = 0
matrikFAasli = matrikFA.copy()
matrikFA[matrikFA >= dynamicthreshold] = 1
mask = matrikFA.copy()
struktur8 = generate_binary_structure(2, 2)  # 2D, 8-neighbors
struktur_perluas = binary_dilation(struktur8, iterations=4)
labeled_array, num_features = label(mask, structure=struktur8)
hasil = []
for i in range(1, num_features + 1):
    cluster_mask = (labeled_array == i)
    max_val = matrikFAasli[cluster_mask].max()
    # Cari posisi titik dengan FA maksimum di cluster ini
    posisi = np.argwhere((matrikFAasli == max_val) & cluster_mask)[0]
    hasil.append([int(posisi[0]), int(posisi[1]), matrikFAasli[int(posisi[0]),int(posisi[1])]])

hasil = np.array(hasil)
hasil = hasil[np.argsort(-hasil[:, 2])]
# ----- 4. Tampilkan hasil -----
i=0
for r, c, v in hasil:
    print(f"no urut {i} ==> baris = {r}, kolom = {c}, nilai FA = {v:.2f}")
    i+=1


#matrikFA[matrikFA >= dynamicthreshold] = 1
# koordinat = np.column_stack(( *np.where(matrikFA > 0), matrikFA[np.where(matrikFA > 0)] ))
# koordinat=koordinat[np.argsort(-koordinat[:, 2])]
# for baris,kolom,fa in koordinat:
#     print(f"baris {baris:>3.0f}, kolom {kolom:>3.0f}, fa {fa:>7.2f}")


# coords = np.column_stack(np.where(mask))

# points_xy = [rasterio.transform.xy(transform, r, c) for r, c in coords]
# X = np.array(points_xy)
#
# # DBSCAN clustering
# clustering = DBSCAN(eps=100, min_samples=1).fit(X)
# print(f"clustering {clustering}")
# # Ambil 1 titik representatif per cluster (nilai acc terbesar)
# labels = clustering.labels_
# print(f"clustering {clustering}")
# unique_labels = np.unique(labels)
#
# final_points = []
# for label in unique_labels:
#     indices = np.where(labels == label)[0]
#     best_idx = max(indices, key=lambda i: matrikFA[coords[i][0], coords[i][1]])
#     final_points.append(Point(X[best_idx]))
#     print(final_points)
#
# # Simpan sebagai SHP
# gdf = gpd.GeoDataFrame(geometry=final_points, crs="EPSG:32749")  # sesuaikan CRS
# gdf.to_file("outlet_dbscan.shp")

# Fungsi bantu untuk menampilkan raster
def show_raster(ax, path, title):
    with rasterio.open(path) as src:
        data = src.read(1)
        data[data == src.nodata] = np.nan
        img = ax.imshow(data, cmap="coolwarm")
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(img, ax=ax, shrink=0.6)
       # print("+++++++++++++++++++++++++++++++++++")
        #print(src.crs)
       # print(src.res)  # resolusi (X, Y)

# Fungsi bantu untuk menampilkan histogram
def show_histogram(ax, path, title):
    with rasterio.open(path) as src:
        data = src.read(1)
        data[data == src.nodata] = np.nan
        data = data[data > 0]  # filter nilai 0 dan nodata

    ax.hist(data.ravel(), bins=100, color='green', log=True)
    ax.set_title(title)
    ax.set_xlabel('Nilai')
    ax.set_ylabel('Frekuensi (log)')

# Tampilkan subplot 2x2
fig, axs = plt.subplots(1, 2, figsize=(8, 8))

# Raster tampilan
show_raster(axs[0, 0], cfg.fileFlowAccumulationBreachThresholdKetinggian, "a")

#show_raster(axs[2, 0], mask, "c")
img=axs[1,0].imshow(matrikFAasli, cmap="coolwarm")
axs[1,0].set_title("Hasil Dynamic Threshold")
axs[1,0].axis("off")
plt.colorbar(img, ax=axs[1,0], shrink=0.6)

# Histogram tampilan (dari MDInfFA)
show_histogram(axs[0, 1], cfg.fileFlowAccumulationBreachThresholdKetinggian, "a")

axs[1,1].hist(matrikFAasli.ravel(), bins=100, color='green', log=True)
axs[1,1].set_title("hasil dynamic threshold")
axs[1,1].set_xlabel('Nilai')
axs[1,1].set_ylabel('Frekuensi (log)')



plt.tight_layout()
plt.show()
