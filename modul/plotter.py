import numpy as np
import matplotlib.pyplot as plt
import os, rasterio
from modul import config as cfg
from matplotlib.colors import LinearSegmentedColormap
plt.switch_backend('qt5agg')
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
cmapfa[0] = [1, 1, 1, 1]
custom_cmapfa = LinearSegmentedColormap.from_list("custom_cmapfa", cmapfa)



def d8_to_uv(d8_array):
    U = np.zeros_like(d8_array, dtype=float)
    V = np.zeros_like(d8_array, dtype=float)
    for val, (dx, dy) in D8_to_vector.items():
        mask = (d8_array == val)
        U[mask] = dx
        V[mask] = dy
    return U, V

def plot_streamplot(d8_array, title="D8 Flow Direction - Streamplot"):
    ny, nx = d8_array.shape
    x = np.arange(0, nx)
    y = np.arange(0, ny)
    X, Y = np.meshgrid(x, y)

    U, V = d8_to_uv(d8_array)

    plt.figure(figsize=(6, 6))
    plt.streamplot(X, Y, U, -V, color='blue', linewidth=1, arrowsize=1.5)
    plt.title(title)
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.gca().invert_yaxis()  # Sesuaikan agar baris 0 di atas seperti raster
    plt.grid(True, alpha=0.3)
    plt.show()
def plot_quiver(d8_array, title="D8 Flow Direction - Quiver Plot"):
    ny, nx = d8_array.shape
    x = np.arange(0, nx)
    y = np.arange(0, ny)
    X, Y = np.meshgrid(x, y)

    U, V = d8_to_uv(d8_array)

    plt.figure(figsize=(6, 6))
    plt.quiver(X, Y, U, -V, color='red', scale=1, scale_units='xy', angles='xy')
    plt.title(title)
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.gca().invert_yaxis()  # Agar baris 0 di atas seperti raster
    plt.grid(True, alpha=0.3)
    plt.show()


def plot(matrikplot, judul, z):
    plt.figure(figsize=(6, 6))
    # Tampilkan dengan colormap custom dan tanpa interpolasi halus
    im = plt.imshow(matrikplot, cmap=custom_cmapfa, interpolation='none')

    if z != "none":
        # Buat dan atur colorbar
        cbar = plt.colorbar(im)
        cbar.set_label(z, fontsize=16)  # ukuran font label
        cbar.ax.tick_params(labelsize=14)  # ukuran font tick labels

    plt.title(judul, fontsize=17)  # (opsional) perbesar title
    plt.xlabel('Column', fontsize=14)  # (opsional) perbesar label sumbu
    plt.ylabel('Row', fontsize=14)
    plt.xticks(fontsize=12)  # (opsional) perbesar tick axis
    plt.yticks(fontsize=12)

    plt.tight_layout()
    plt.show()

def plot_file(file, judul, z):
    if os.path.exists(file):
        with rasterio.open(file) as src:
            matrik = src.read(1)  # Ambil band pertama
           # matrik = np.flipud(matrik)
        plot(matrik, judul,z)

def konvertarray(file):
    with rasterio.open(file) as src:
        return src.read(1)
#plot_file(cfg.fileExtractstreams, "Stream link identifier", "none")

#plot_file(cfg.fileFlowAccumulationBreachThresholdKetinggian, "estrak", "Stream link id")
#lot_file(cfg.fileExtractstreamsbawah,"Extract stream 40th percentile", "Upstream contributing cell count")
#plot_file(cfg.fileExtractstreams,"Extract stream 90th percentile", "Upstream contributing cell count")
#plot_file(cfg.fileFlowAccumulationBreachD8,"D8 FA", "cell count")
#plot_quiver(konvertarray(cfg.filed8pointer),"quiver")
# plot_file(cfg.fileFlowAccumulationBreachD8, "(a) D8 FA", "Upstream contributing cell count")
#plot_file(cfg.fileStreamslinkidentifier, "Stream link identifier", "Stream link id")
# #plot_file(cfg.fileFlowAccumulationBreachMDInf, "(b) MD∞ FA", "Upstream contributing cell count")