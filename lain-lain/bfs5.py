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

# Inisialisasi dan atur direktori kerja
wbt = WhiteboxTools()
wbt.verbose = False

# Ganti dengan path ke file DEM kamu
dem_file = cfg.fileSeleksiDEM
work_dir = os.path.dirname(dem_file)
wbt.work_dir = cfg.fileFlowAccumulation

# Buat nama file output

breached_dem = os.path.join(work_dir, "breached.tif")
filled_dem = os.path.join(work_dir, "filled.tif")
flow_accum_breached = os.path.join(work_dir, "mdinf_accum_breached.tif")
flow_accum_filled = os.path.join(work_dir, "mdinf_accum_filled.tif")
flow_accum_asli = os.path.join(work_dir, "mdinf_accum_asli.tif")
pointer = os.path.join(work_dir, "pointer.tif")
dinfpointer = os.path.join(work_dir, "dinfpointer.tif")
dinfpointerfilled = os.path.join(work_dir, "dinfpointerfilled.tif")
dinfpointerbreached = os.path.join(work_dir, "dinfpointerbreached.tif")
flow_accum_workflow = os.path.join(work_dir, "flow_accum_workflow.tif")
dem_workflow = os.path.join(work_dir, "dem_workflow.tif")
sub_dem = os.path.join(work_dir, "subdem.tif")
# 1. BreachDepressions
wbt.d_inf_pointer(dem=dem_file, output=dinfpointer)
wbt.breach_depressions(dem=dem_file, output=breached_dem)
wbt.d_inf_pointer(dem=breached_dem, output=dinfpointerbreached)
# 2. FillDepressions (opsional untuk perbandingan visual)
wbt.fill_depressions(dem=dem_file, output=filled_dem)
wbt.d_inf_pointer(dem=filled_dem, output=dinfpointerfilled)
# 3. MD∞ Flow Accumulation (TIDAK butuh pointer)
wbt.md_inf_flow_accumulation(dem=breached_dem, output=flow_accum_breached, out_type="ca")

wbt.md_inf_flow_accumulation(dem=filled_dem, output=flow_accum_filled, out_type="ca")
wbt.md_inf_flow_accumulation(dem=dem_file, output=flow_accum_asli, out_type="ca")

wbt.flow_accumulation_full_workflow(dem=dem_file, out_dem=dem_workflow, out_pntr=pointer,
                                    out_accum=flow_accum_workflow,out_type="ca")

# Fungsi bantu untuk menampilkan raster
def show_raster(ax, path, title):
    with rasterio.open(path) as src:
        data = src.read(1)
        data[data == src.nodata] = np.nan
        img = ax.imshow(data, cmap="coolwarm")
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(img, ax=ax, shrink=0.6)
        print("+++++++++++++++++++++++++++++++++++")
        print(src.crs)
        print(src.res)  # resolusi (X, Y

# Tampilkan subplot
fig, axs = plt.subplots(3, 4, figsize=(24, 6))
show_raster(axs[0,0], dem_file, "Original DEM")
show_raster(axs[1,0], flow_accum_asli, "MDInfFA dari Original DEM" )
show_raster(axs[2,0], dinfpointer, "dinfpointer dari Original DEM" )

show_raster(axs[0, 1], filled_dem, "Filled Depressions")
show_raster(axs[1, 1], flow_accum_filled, "MDInfFA dari Filled Depressions")
show_raster(axs[2,1], dinfpointerfilled, "dinfpointer dari Filled Depressions" )

show_raster(axs[0, 2], breached_dem, "Breached Depressions")
show_raster(axs[1, 2], flow_accum_breached, "MDInfFA dari Breached Depressions")
show_raster(axs[2,2], dinfpointerbreached, "dinfpointer dari Breached Depressions" )

show_raster(axs[0, 3], dem_workflow, "DEM dari Workflow")
show_raster(axs[1, 3], flow_accum_workflow, "MDInfFA dari Workflow")
show_raster(axs[2, 3], pointer, "d8pointer dari Workflow")



plt.tight_layout()
plt.show()
