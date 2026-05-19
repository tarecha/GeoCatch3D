import rasterio, os, numpy as np
from modul import plotter as plt, config as cfg
from rasterio.transform import from_origin
from whitebox.whitebox_tools import WhiteboxTools
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap
blue_red = LinearSegmentedColormap.from_list('blue_red', ['blue', 'green', 'yellow', 'red'])
# 2. Sampling jadi 64 warna (RGBA)
cmapfa = blue_red(np.linspace(0, 1, 32))  # bentuk: (64, 4)
# 3. Modifikasi warna pertama (misalnya jadi putih)
cmapfa[0] = [1, 1, 1, 1]  # R, G, B, A → putih solid
custom_cmapfa1 = LinearSegmentedColormap.from_list('custom_cmapfa1', cmapfa)
tif_path = r"D:\cc\perbandingan demnas dataran tinggi\DEMNAS_1508-32_v1.0.tif"
src_tif = tif_path
fixed_tif = r"D:\cc\perbandingan demnas dataran tinggi\DEMNAS_1608-11_v1.0fixed.tif"
tif_path = fixed_tif
with rasterio.open(src_tif) as src:
    data = src.read(1)
    meta = src.meta.copy()

print(meta)
# SET CRS (DEMNAS biasanya EPSG:4326)
meta.update({
    "crs": "EPSG:4326"
    #,
    #"transform": from_origin(112.75, -7.75, 0.00010278, 0.000075007501)
    # ⚠️ GANTI origin & resolusi sesuai metadata DEM kamu
})

with rasterio.open(fixed_tif, "w", **meta) as dst:
    dst.write(data, 1)

print("GeoTIFF fixed:", fixed_tif)

wbt = WhiteboxTools()

# tif_path = r"D:\cc\DEMNAS_1607-43_v1.0_fixed.tif"

tif_pathbreach = r"D:\cc\perbandingan demnas dataran tinggi\breach.tif"
tif_d8fd = r"D:\cc\perbandingan demnas dataran tinggi\tif_d8fd.tif"
tif_d8fa = r"D:\cc\perbandingan demnas dataran tinggi\tif_d8fa.tif"
tif_mdinf = r"D:\cc\perbandingan demnas dataran tinggi\tif_mdinf.tif"
tif_stream = r"D:\cc\perbandingan demnas dataran tinggi\tif_stream.tif"
tif_streammdinf =  r"D:\cc\perbandingan demnas dataran tinggi\tif_streammdinf.tif"

print(f"tif_path: {tif_path}")
wbt.breach_depressions_least_cost( dem=tif_path, output=tif_pathbreach, min_dist=True, fill=True, flat_increment=0.01, dist=2 )
wbt.d8_pointer(dem=tif_pathbreach, output=tif_d8fd)
wbt.d8_flow_accumulation(i=tif_d8fd, output=tif_d8fa, out_type="cells", pntr=True)
wbt.extract_streams(flow_accum=tif_d8fa,output=tif_stream,threshold=685)

#wbt.extract_streams(flow_accum=tif_d8fa,output=tif_streammdinf,threshold=cfg.thresholdminextractstreamshulu)
#plt.plot_file(tif_stream,"tif_stream","FA")

with rasterio.open(tif_path) as src:
    data = src.read(1)
    meta = src.meta.copy()

ukuran_baris = 1000
ukuran_kolom = 1000
matrikBesar =data
pixelBarisAwal = 0
pixelKolomAwal = 750

matrikKecil = np.zeros((ukuran_baris, ukuran_kolom), dtype=np.float32)
for i in range(ukuran_baris):
    for j in range(ukuran_kolom):
        matrikKecil[i, j] = matrikBesar[i + pixelBarisAwal, j + pixelKolomAwal]
#tif_stream=tif_d8fa
print(f"file stream { tif_stream}")
if os.path.exists( tif_stream):
    with rasterio.open( tif_stream) as src:
        tampilflowaccum = src.read(1)  # Ambil band pertama
        print(f"tampilflowaccum {tampilflowaccum.shape}")

        # transformasi = src.transform
else:
    raise FileNotFoundError("Hasil fileBreachDepression tidak ditemukan")
matrikKecilFA = np.zeros((ukuran_baris, ukuran_kolom), dtype=np.float32)
for i in range(ukuran_baris):
    for j in range(ukuran_kolom):
        matrikKecilFA[i, j] = tampilflowaccum[i + pixelBarisAwal, j + pixelKolomAwal]



plotter = pv.Plotter()
plotter.lighting = 'None'
plotter.set_scale(1, 1, 0.125)
matrikKecil = np.flipud(matrikKecil)
x = np.arange(0, ukuran_kolom, dtype=np.float32)
y = np.arange(0, ukuran_baris, dtype=np.float32)
X, Y = np.meshgrid(x, y)
grid = pv.StructuredGrid(X.copy(), Y.copy(), matrikKecil.copy())
#np.flipud(np.rot90(tampilflowaccum, k=1))
#plotter.add_mesh(grid.elevation().copy(), cmap='terrain', show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
plotter.add_mesh(grid.copy(), scalars=np.rot90(matrikKecilFA,k=-1), cmap='coolwarm', show_edges=True,
                  pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
plotter.view_xy()
plotter.show()