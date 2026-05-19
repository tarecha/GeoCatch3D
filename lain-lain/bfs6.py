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
blue_red = LinearSegmentedColormap.from_list('blue_red', ['blue','red'])
# 2. Sampling jadi 64 warna (RGBA)
cmapfa = blue_red(np.linspace(0, 1, 6))  # bentuk: (64, 4)
# 3. Modifikasi warna pertama (misalnya jadi putih)
cmapfa[0] = [1, 1, 1, 1]  # R, G, B, A → putih solid
# 4. Buat colormap baru dari array warna
custom_cmapfa1 = LinearSegmentedColormap.from_list('custom_cmapfa1', cmapfa)

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

# Tampilkan subplot
fig, axs = plt.subplots(1, 2, figsize=(3.25, 3.25))
#show_raster(axs[0,0], cfg.fileSeleksiDEM, "a. Original DEM", "elevation meter","bwr" )
show_raster(axs[0], cfg.fileFlowAccumulationOri, "a. Flow accumulation tanpa Breach Depressions Least Cost","Jumlah sel yang berkontribusi di hulu",custom_cmapfa1)
#show_raster(axs[0,1], cfg.fileBreachDepression, "c. Breach Depressions Least Cost from original DEM","elevation meter","bwr" )
show_raster(axs[1], cfg.fileFlowAccumulationBreachMDInf, "b. Flow accumulation dengan Breach Depressions Least Cost","Jumlah sel yang berkontribusi di hulu",custom_cmapfa1)

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
