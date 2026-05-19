import numpy as np
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import LinearSegmentedColormap

plt.switch_backend('qt5agg')
from modul import config as cfg
import rasterio
# Fungsi bantu untuk menampilkan raster
def show_raster(ax, path, title):
    with rasterio.open(path) as src:
        data = src.read(1)
        data[data == src.nodata] = 0
        ax.imshow(data, cmap=custom_cmapfa)
        ax.set_title(title)
        ax.axis("off")

def show_raster_array(ax, array, title):
    # data = src.read(1)
    # data[data == src.nodata] = np.nan
    ax.imshow(array, cmap=custom_cmapfa)
    ax.set_title(title,fontsize=10)
    ax.axis("off")

        #plt.colorbar(img, ax=ax, shrink=0.6)
       # print("+++++++++++++++++++++++++++++++++++")
        #print(src.crs)
       # print(src.res)  # resolusi (X, Y)

# Fungsi bantu untuk menampilkan histogram
def show_histogram(ax, path, title):
    with rasterio.open(path) as src:
        data = src.read(1)
        #data[data == src.nodata] = np.nan
        data = data[data > 0]  # filter nilai 0 dan nodata

    ax.hist(data.ravel(), bins=100, color='green', log=True)
    ax.set_title(title,fontsize=10)
    ax.set_xlabel('Nilai')
    ax.set_ylabel('Frekuensi (log)')

# Tampilkan subplot 2x2
fig, axs = plt.subplots(2, 3, figsize=(8, 8))
D8_to_vector = {

    1: (1, 0),    # East
    2: (1, -1),   # Southeast
    3: (0, -1),   # South
    4: (-1, -1),  # Southwest
    5: (-1, 0),   # West
    6: (-1, 1),   # Northwest
    7: (0, 1),    # North
    8: (1, 1),    # Northeast
}
terrain_colors = plt.get_cmap("seismic")(np.linspace(0, 1, 1024))
terrain_colors[0] = [1, 1, 1, 1]
custom_terrain = LinearSegmentedColormap.from_list("custom_terrain", terrain_colors)

cmapfa = plt.get_cmap("bwr")(np.linspace(0, 1, 256))
cmapfa[0] = [0, 0, 0, 1]
custom_cmapfa = LinearSegmentedColormap.from_list("custom_cmapfa", cmapfa)
from scipy.ndimage import label, generate_binary_structure, binary_dilation
titikTengah = 912
wbt = WhiteboxTools()
wbt.d8_pointer(dem=cfg.fileBreachDepression, output=cfg.filed8pointer)
#wbt.d8_flow_accumulation(i=cfg.filed8pointer2, output=cfg.fileFlowAccumulationBreachD82, out_type="cells", pntr=True)

with rasterio.open(cfg.fileFlowAccumulationBreachMDInf) as src:
    matrikFAMDINF = src.read(1)
with rasterio.open(cfg.fileFlowAccumulationBreachD8) as src:
    matrikFA = src.read(1)
    print(f"sum D8 {np.sum(matrikFA)}")


with rasterio.open(cfg.fileSeleksiDEM) as src:
    matrikKecil = src.read(1)
    transformasi = src.transform
    crs = src.crs

print(f"sum 1 {np.sum(matrikFA)}")
matrikFAMDINF[np.isnan(matrikFAMDINF)] = 0
matrikFAMDINF[np.isinf(matrikFAMDINF)] = 0
matrikFA[np.isnan(matrikFA)] = 0
matrikFA[np.isinf(matrikFA)] = 0
print(f"sum 2 {np.sum(matrikFA)}")
tinggi, lebar = matrikKecil.shape
for i in range(tinggi):
    for j in range(lebar):
        #print(f"i {i}, j {j}")
        if matrikKecil[i, j] <= titikTengah:
            matrikFA[i, j] = 0
            matrikFAMDINF[i, j] = 0

show_raster_array(axs[0, 0], matrikFA, "Altitude threshold D8 FA")
show_raster_array(axs[1, 0], matrikFAMDINF, "Altitude threshold MD∞ FA")

matrikFAthresholdketinggian = matrikFA.copy()
nilaiFAunik = np.unique(matrikFA.astype(int))
nilaiFAunik = nilaiFAunik[nilaiFAunik > 0][::-1]
print(nilaiFAunik.dtype)
for row in nilaiFAunik:
    print(f"nilaiFAunik {row}")
print(f"nilaiFAunik {nilaiFAunik}")
dynamicthreshold = np.percentile(nilaiFAunik, cfg.percentile)
dynamicthreshold = 50
print(f"dynamicthreshold {dynamicthreshold}")
matrikFA[matrikFA < dynamicthreshold] = 0
matrikFAMDINF[matrikFAMDINF < dynamicthreshold] = 0
matrikFAthresholdketinggiandynamic = matrikFA.copy()
show_raster_array(axs[0, 1], matrikFA, "Percentile 85th threshold D8 FA")
show_raster_array(axs[1, 1], matrikFAMDINF, "Percentile 85th threshold  MD∞ FA")
matrikFA[matrikFA >= dynamicthreshold] = 1
matrikFAMDINF[matrikFAMDINF >= dynamicthreshold] = 2




show_raster_array(axs[0, 2], matrikFA, "Stream extraction D8 FA")
show_raster_array(axs[1, 2], matrikFAMDINF, "Stream extraction MD∞ FA")
with rasterio.open(
        cfg.fileExtractstreams, 'w',
        driver='GTiff',
        height=matrikFA.shape[0],
        width=matrikFA.shape[1],
        count=1,
        dtype=matrikFA.dtype,
        crs=crs,
        transform=transformasi
) as dst:
    dst.write(matrikFA, 1)
    print(f"[SUKSES] GeoTIFF berhasil disimpan ke { cfg.fileExtractstreams}")

#wbt.extract_streams(flow_accum=cfg.fileFlowAccumulationBreachD8,output=cfg.fileExtractstreams, threshold=dynamicthreshold, zero_background=True)
wbt.stream_link_identifier(d8_pntr=cfg.filed8pointer, streams=cfg.fileExtractstreams,output=cfg.fileStreamslinkidentifier, zero_background=True)
with rasterio.open(cfg.fileStreamslinkidentifier) as src:
    matrikstreamkinkidentifier= src.read(1)

rows, cols = np.nonzero(matrikstreamkinkidentifier)
values = matrikstreamkinkidentifier[rows, cols]
print(f"identifier {values}")
# Gabungkan menjadi array N x 3 (baris, kolom, nilai)
stackstream = np.stack((rows, cols, values), axis=1)

print(f"stackstream {stackstream}, {stackstream.dtype}")
pourpoint = []
clusters = max(values) #jumlah cluster
clusters = np.unique(stackstream[:, 2])
print(clusters)
for cid in clusters:
    cluster_data = stackstream[stackstream[:, 2] == cid]
    #print(f"cluster_data {cluster_data}, {cluster_data.dtype}")
    max_val = -np.inf
    best_row, best_col = -1, -1

    for row, col, _ in cluster_data:
        nilai = matrikFAMDINF[int(row), int(col)]
        print(f"row {row}, col {col}, nilai {nilai}")
        if nilai > max_val:
            max_val = nilai
            best_row, best_col = row, col

    pourpoint.append([best_row, best_col, cid, max_val])


hasil_akhir = np.array(pourpoint)

#np.set_printoptions(suppress=True, formatter={'float_kind': '{:0.2f}'.format})

print(hasil_akhir)



# wbt.stream_link_class(d8_pntr=cfg.filed8pointer,streams=cfg.fileExtractstreams, output=cfg.fileStreamslinkclass,zero_background=True)



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



# Raster tampilan
# show_raster(axs[0, 0], cfg.fileFlowAccumulationBreachD8, "flow accumulation D8")
# show_raster_array(axs[0, 1], matrikFAthresholdketinggian, "Threshold ketinggian")
# show_raster_array(axs[0, 2], matrikFAthresholdketinggiandynamic, "Threshold ketinggian + dynamic")
# show_raster_array(axs[1, 0], matrikFA, "Threshold ketinggian + dynamic + ekstrak")
# show_raster(axs[1, 1], cfg.fileExtractstreams, "ekstrak stream")
# show_raster(axs[1, 2], cfg.fileExtractstreamsbawah, " ekstrak stream bawah")
# #show_raster(axs[2, 0], cfg.fileStreamslinkclass, " stream link class")
# show_raster(axs[2,1], cfg.filewatershed, "watershed")
#
# show_raster(axs[2,2], cfg.fileFlowAccumulationBreachD8, "flow accumulation mdinf")
# # img=axs[1,0].imshow(matrikFAasli, cmap="coolwarm")
# # axs[1,0].set_title("Hasil Dynamic Threshold")
# # axs[1,0].axis("off")
# # plt.colorbar(img, ax=axs[1,0], shrink=0.6)
# show_histogram(axs[2, 0], cfg.filewatershed, "a")
#
#

#
# #show_raster(axs[2, 0], mask, "c")
# img=axs[1,0].imshow(matrikFAasli, cmap="coolwarm")
# axs[1,0].set_title("Hasil Dynamic Threshold")
# axs[1,0].axis("off")
# plt.colorbar(img, ax=axs[1,0], shrink=0.6)
#
# # Histogram tampilan (dari MDInfFA)
#
#
# axs[1,1].hist(matrikFAasli.ravel(), bins=100, color='green', log=True)
# axs[1,1].set_title("hasil dynamic threshold")
# axs[1,1].set_xlabel('Nilai')
# axs[1,1].set_ylabel('Frekuensi (log)')
#
# Atur koordinat axis

# Khusus GUI interactive, seperti Qt, kita set juga ke toolbar


plt.tight_layout()
plt.show()
