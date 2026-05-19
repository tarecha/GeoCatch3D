import numpy as np
import rasterio
from whitebox.whitebox_tools import WhiteboxTools
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')
from modul import config as cfg

# Setup
wbt = WhiteboxTools()
wbt.set_working_dir(cfg.pathTempMaps)  # Ganti folder


fig, axs = plt.subplots(3, 4, figsize=(10, 10))

#==============================================================================
with rasterio.open(cfg.fileSeleksiDEM) as dem_src:
    matrik= dem_src.read(1)
    matrikA = matrik

im1 = axs[0, 0].imshow(matrik, cmap='coolwarm')
axs[0, 0].set_title("DEM ASLI")
axs[0, 0].axis('on')
fig.colorbar(im1, ax=axs[0, 0], shrink=0.8)
tif_path = "D:\\cc\\DEMNAS_1607-43_v1.0.tif"
tif_pathout = "D:\\cc\\oke pakai iniDEMNAS_1607-43_v1.0out.tif"
#==============================================================================
wbt.breach_depressions(
    tif_path,
    tif_pathout
)

with rasterio.open(tif_pathout) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[0, 1].imshow(matrik, cmap='coolwarm')
axs[0, 1].set_title("breach depression")
axs[0, 1].axis('on')
fig.colorbar(im1, ax=axs[0, 1], shrink=0.8)

#==============================================================================
wbt.fill_depressions(
    cfg.fileSeleksiDEM,
    cfg.fileoutput
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[0, 2].imshow(matrik, cmap='coolwarm')
axs[0, 2].set_title("Fill depression")
axs[0, 2].axis('on')
fig.colorbar(im1, ax=axs[0, 2], shrink=0.8)
#==============================================================================

#==============================================================================
wbt.sink(
    cfg.fileSeleksiDEM,
    cfg.fileoutput
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[0, 3].imshow(matrik, cmap='coolwarm')
axs[0, 3].set_title("Sink")
axs[0, 3].axis('on')
fig.colorbar(im1, ax=axs[0, 3], shrink=0.8)

#==============================================================================
wbt.d8_pointer(
    cfg.fileSeleksiDEM,
    cfg.filed8pointer
)

with rasterio.open(cfg.filed8pointer) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[1, 0].imshow(matrik, cmap='coolwarm')
axs[1, 0].set_title("D8 pointer")
axs[1, 0].axis('on')
fig.colorbar(im1, ax=axs[1, 0], shrink=0.8)




#==============================================================================
wbt.md_inf_flow_accumulation(
    cfg.fileSeleksiDEM,
    cfg.fileoutput,
    out_type='ca'
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[1, 1].imshow(matrik, cmap='coolwarm')
axs[1, 1].set_title("Flow accum mdinf")
axs[1, 1].axis('on')
fig.colorbar(im1, ax=axs[1,1], shrink=0.8)

#==============================================================================
wbt.d8_flow_accumulation(
    cfg.fileSeleksiDEM,
    cfg.fileoutput,
    out_type='ca'
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[1, 2].imshow(matrik, cmap='coolwarm')
axs[1, 2].set_title("Flow accum d8")
axs[1, 2].axis('on')
fig.colorbar(im1, ax=axs[1,2], shrink=0.8)

#==============================================================================
wbt.basins(
    cfg.filed8pointer,
    cfg.fileoutput
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[1, 3].imshow(matrik, cmap='coolwarm')
axs[1, 3].set_title("basins")
axs[1, 3].axis('on')
fig.colorbar(im1, ax=axs[1,3], shrink=0.8)


#==============================================================================
wbt.d_inf_flow_accumulation(
    cfg.fileSeleksiDEM,
    cfg.fileoutput,
    out_type='ca'
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[2, 0].imshow(matrik, cmap='coolwarm')
axs[2, 0].set_title("Flow accum dinf")
axs[2, 0].axis('on')
fig.colorbar(im1, ax=axs[2,0], shrink=0.8)

#==============================================================================
wbt.fd8_flow_accumulation(
    cfg.fileSeleksiDEM,
    cfg.fileoutput,
    out_type='ca'
)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[2, 1].imshow(matrik, cmap='coolwarm')
axs[2, 1].set_title("Flow accum fd8")
axs[2, 1].axis('on')
fig.colorbar(im1, ax=axs[2,1], shrink=0.8)


#==============================================================================
wbt.qin_flow_accumulation(
    cfg.fileSeleksiDEM,
    cfg.fileoutput,

)

with rasterio.open(cfg.fileoutput) as dem_src:
    matrik= dem_src.read(1)

im1 = axs[2, 2].imshow(matrik, cmap='coolwarm')
axs[2, 2].set_title("Flow accum Qin")
axs[2, 2].axis('on')
fig.colorbar(im1, ax=axs[2,2], shrink=0.8)


#==============================================================================
wbt.flow_accumulation_full_workflow(
    dem=cfg.fileSeleksiDEM,
    out_dem=cfg.fileoutput,
    out_accum=cfg.fileFlowAccumulation,
    out_pntr=cfg.filed8pointer,
    out_type='ca',

    log=False,
    clip=False,
    esri_pntr=False


)

with rasterio.open(cfg.fileFlowAccumulation) as dem_src:
    matrik= dem_src.read(1)

print("kesamaan matrik")
print(np.array_equal(matrikA, matrik))
mask =matrikA != matrik
print("Perbedaan terdapat di posisi:")
print(np.argwhere(mask))

im1 = axs[2, 3].imshow(matrik, cmap='coolwarm')
axs[2, 3].set_title("full workflow")
axs[2, 3].axis('on')
fig.colorbar(im1, ax=axs[2,3], shrink=0.8)
#
# #==============================================================================
# wbt.dev_from_mean_elev(
#     dem_filled, fileTPI, filterx=3, filtery=3
# )
# wbt.less_than(
#     fileTPI, 0.0, fileTPINegatif
# )
#
# with rasterio.open(fileTPINegatif) as demTPI_src:
#     matrikDEMTPI = demTPI_src.read(1)
#     matrikDEMTPI_meta = demTPI_src.meta
# im3= axs[0, 2].imshow(matrikDEMTPI, cmap='coolwarm')
# axs[0, 2].set_title("TPI Negatif")
# axs[0, 2].axis('on')
# fig.colorbar(im3, ax=axs[0, 2], shrink=0.8)
# #==============================================================================
# wbt.subtract(
#     dem, dem_filled, cfg.fileFillDepressionSub
# )
#
# with rasterio.open(cfg.fileFillDepressionSub) as demfilled_src:
#     matrikDEMFilled = demfilled_src.read(1)
#     matrikDEMFilled_meta = demfilled_src.meta
#
#
# im2= axs[1, 0].imshow(matrikDEMFilled, cmap='coolwarm')
# axs[1, 0].set_title("depression")
# axs[1, 0].axis('on')
# fig.colorbar(im2, ax=axs[1, 0], shrink=0.8)
#
# #=============================================
# wbt.md_inf_flow_accumulation(
#         dem=cfg.fileFillDepressionSub,
#         output=cfg.fileFAdariFillDepressionSub,
#         out_type='ca'  # 'ca' = catchment area; bisa diganti 'cells' atau 'sca',
#
#     )
#
# with rasterio.open(cfg.fileFAdariFillDepressionSub) as demfilled_src:
#     matrikDEMFilled = demfilled_src.read(1)
#     matrikDEMFilled_meta = demfilled_src.meta
#
#
# flow_accum_log = np.log1p(matrikDEMFilled)
# flow_accum_norm = (flow_accum_log - np.min(flow_accum_log)) / (np.max(flow_accum_log) - np.min(flow_accum_log))
#
#
# im2= axs[1, 1].imshow(flow_accum_norm, cmap='coolwarm')
# axs[1, 1].set_title("fa dari depression sub normalisasi ")
# axs[1, 1].axis('on')
# fig.colorbar(im2, ax=axs[1, 1], shrink=0.8)
#
# matrikFA = flow_accum_norm
# matrikFA[np.isnan(matrikFA)] = 0
# matrikFA[np.isinf(matrikFA)] = 0
# unik, jumlah = np.unique(matrikFA, return_counts=True)
# hasil = sorted(zip(unik, jumlah), key=lambda x: x[0], reverse=True)
#
# thresholdFlowAccumulation, jumlahkeluar = hasil[cfg.thresholdFlowAccumulation]
# matrikFA[matrikFA < thresholdFlowAccumulation] = 0
#
# im2= axs[1, 2].imshow(matrikFA, cmap='coolwarm')
# axs[1, 2].set_title("fa dari depression sub normalisasi threshold ")
# axs[1, 2].axis('on')
# fig.colorbar(im2, ax=axs[1, 2], shrink=0.8)
#
#
# #==============================================================================
#
#
# with rasterio.open(flow_acc) as demTPI_src:
#     matrikDEMTPI = demTPI_src.read(1)
#     matrikDEMTPI_meta = demTPI_src.meta
# im3= axs[2, 0].imshow(matrikDEMTPI, cmap='coolwarm')
# axs[2, 0].set_title("Flow ACC")
# axs[2, 0].axis('on')
# fig.colorbar(im3, ax=axs[2, 0], shrink=0.8)
#
# #====================================
# flow_accum_log = np.log1p(matrikDEMTPI)
# flow_accum_norm = (flow_accum_log - np.min(flow_accum_log)) / (np.max(flow_accum_log) - np.min(flow_accum_log))
#
# im3= axs[2, 1].imshow(flow_accum_norm, cmap='coolwarm')
# axs[2, 1].set_title("Flow ACC norm ")
# axs[2, 1].axis('on')
# fig.colorbar(im3, ax=axs[2, 1], shrink=0.8)
#
# #==============================
# matrikFA = flow_accum_norm
# matrikFA[np.isnan(matrikFA)] = 0
# matrikFA[np.isinf(matrikFA)] = 0
# unik, jumlah = np.unique(matrikFA, return_counts=True)
# hasil = sorted(zip(unik, jumlah), key=lambda x: x[0], reverse=True)
#
# thresholdFlowAccumulation, jumlahkeluar = hasil[cfg.thresholdFlowAccumulation]
# print(f"index: {cfg.thresholdFlowAccumulation}, thresholdFlowAccumulation: {thresholdFlowAccumulation}, jumlahkeluar: {jumlahkeluar}")
# print("Hasil unik")
# print("nilai FA |  jumlah")
# for i, row in enumerate(hasil[:cfg.thresholdFlowAccumulation + 1]):  # +1 kalau mau termasuk indeks tersebut
#     print(f"Index {i}: ", end='')
#     print('\t'.join(f"{val:>3}" for val in row))
#
# # Terapkan threshold: buang nilai kecil
# matrikFA[matrikFA < thresholdFlowAccumulation] = 0
# im3= axs[2, 2].imshow(matrikFA, cmap='coolwarm')
# axs[2, 2].set_title("Flow ACC threshold ")
# axs[2, 2].axis('on')
# fig.colorbar(im3, ax=axs[2, 2], shrink=0.8)

fig.subplots_adjust(wspace=0.3, hspace=0.3)
plt.show()
