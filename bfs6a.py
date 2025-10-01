import numpy as np
import rasterio
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
from modul import config as cfg

import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import LinearSegmentedColormap
from whitebox import WhiteboxTools
wbt = WhiteboxTools()
cmapfa = plt.get_cmap("seismic")(np.linspace(0, 1, 32))
cmapfa[0] = [1, 1, 1, 1]
custom_cmapfa = LinearSegmentedColormap.from_list("custom_cmapfa", cmapfa)
# Inisialisasi dan atur direktori kerja
wbt.breach_depressions_least_cost(dem=cfg.fileSeleksiDEM, output=cfg.fileBreachDepression, dist=10)
wbt.md_inf_flow_accumulation(
        dem=cfg.fileSeleksiDEM,
        output=cfg.fileFlowAccumulationOri,
        out_type='cells'  # 'ca' = catchment area; bisa diganti 'cells' atau 'sca',

    )

wbt.md_inf_flow_accumulation(
        dem=cfg.fileBreachDepression,
        output=cfg.fileFlowAccumulationBreachMDInf,
        out_type='cells'  # 'ca' = catchment area; bisa diganti 'cells' atau 'sca',

    )
wbt.basins(d8_pntr=cfg.filed8pointer, output=cfg.fileBasins)
# Fungsi bantu untuk menampilkan raster
def show_raster(ax, path, title,z,color):
    with rasterio.open(path) as src:
        data = src.read(1)
        data[data == src.nodata] = 0
        img = ax.imshow(data, cmap=color)

        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(img, ax=ax, shrink=0.6,label=z)
        print("+++++++++++++++++++++++++++++++++++")
        print(src.crs)
        print(src.res)  # resolusi (X, Y
def show_raster_array(ax, array, judul, label,color):

    img = ax.imshow(array, cmap=custom_cmapfa)

    ax.set_title(judul)
    ax.axis("off")
    plt.colorbar(img, ax=ax, shrink=0.6,label=label)

# Tampilkan subplot
fig, axs = plt.subplots(1, 2, figsize=(3.25, 3.25))
show_raster(axs[0,0], cfg.fileExtractstreams, "a. Original DEM", "altitude meter","coolwarm" )
show_raster(axs[1,0], cfg.filewatershed, "b. Flow accumulation algorithm  from Original DEM","Upstream contributing cell count",custom_cmapfa)

with rasterio.open(cfg.fileFlowAccumulationBreachMDInf) as src:
    accum = src.read(1)
    accum[accum < 0] = 0
    accum[np.isnan(accum)] = 0
    accum[np.isinf(accum)] = 0
    maxaccum = np.max(accum)
with rasterio.open(cfg.filewatershed) as src:
    watershed = src.read(1)
    watershed[watershed<0] = 0
    watershed[np.isnan(watershed)] = 0
    watershed[np.isinf(watershed)] = 0
    maxwatershed = np.max(watershed)


accum_norm = accum / maxaccum if maxaccum != 0 else accum
watershed_norm = watershed / maxwatershed if maxwatershed != 0 else watershed

# Gabungkan informasi dari watershed (yang > 0) ke dalam array accum_norm
# Misalnya dengan penambahan nilai normalisasi (dapat disesuaikan dengan bobot)
combined = accum_norm.copy()
combined[watershed > 0] += watershed_norm[watershed > 0]  # nilai hanya ditambahkan jika ada DAS

# Jika ingin memastikan tetap dalam skala 0-1
combined = combined / np.max(combined)

# Jika ingin mengembalikan ke skala semula seperti skala accum
combined_scaled = combined * maxaccum

# Tampilkan dengan fungsi show_raster_array (gantilah 'hasil' dengan combined_scaled jika perlu)
show_raster_array(axs[1,1], combined_scaled, "a. Gabungan Flow Accum + Watershed", "Nilai Skalar Gabungan", "viridis")

show_raster(axs[0,1],cfg.fileStreamslinkidentifier,"stream link identifier", "id","coolwarm")

#show_raster(axs[0, 1], filled_dem, "Filled Depressions")
#show_raster(axs[1, 1], flow_accum_filled, "MDInfFA dari Filled Depressions")
# show_raster(axs[2,1], dinfpointerfilled, "dinfpointer dari Filled Depressions" )
#
# show_raster(axs[0, 2], breached_dem, "Breached Depressions")
# show_raster(axs[1, 2], flow_accum_breached, "MDInfFA dari Breached Depressions")
# show_raster(axs[2,2], dinfpointerbreached, "dinfpointer dari Breached Depressions" )
#
# show_raster(axs[0, 3], dem_workflow, "DEM dari Workflow")
# show_raster(axs[1, 3], flow_accum_workflow, "MDInfFA dari Workflow")
# show_raster(axs[2, 3], pointer, "d8pointer dari Workflow")
#


#plt.tight_layout()
plt.show()
