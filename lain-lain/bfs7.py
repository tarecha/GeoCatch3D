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
from whitebox import WhiteboxTools
wbt = WhiteboxTools()


# Fungsi bantu untuk menampilkan raster
def show_raster(ax, path, title):
    with rasterio.open(path) as src:
        data = src.read(1)
#        data[data == src.nodata] = np.nan
        img = ax.imshow(data, cmap="bwr")
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(img, ax=ax, shrink=0.6)
        print("+++++++++++++++++++++++++++++++++++")
        print(src.crs)
        print(src.res)  # resolusi (X, Y

# Tampilkan subplot
fileExtractstreams = r'D:\maps\temp\old\fileExtractstreams.tif'
fileStreamslinkidentifier = r'D:\maps\temp\old\fileStreamslinkidentifier.tif'
fig, axs = plt.subplots(2, 2, figsize=(3.25, 3.25))
show_raster(axs[0,0], cfg.fileExtractstreams, "fileExtractstreams")
show_raster(axs[1,0], cfg.fileStreamslinkidentifier, "fileStreamslinkidentifier" )
show_raster(axs[0,1], fileExtractstreams, "fileExtractstreams old")
show_raster(axs[1,1], fileStreamslinkidentifier, "fileStreamslinkidentifier old" )
#show_raster(axs[0,1], cfg.fileBreachDepression, "c. Breach Depressions Least Cost" )
#show_raster(axs[1,1], cfg.fileFlowAccumulationBreach, "d. MDInfFA from Breach Depressions Least Cost" )

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
