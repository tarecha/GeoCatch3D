
import numpy as np
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.pyplot as plt
import whitebox
from whitebox.whitebox_tools import WhiteboxTools
import tempfile
import os


from modul import mapping, seleksiRHD, seleksiBF, pilih, interpolasiLinier
from scipy.ndimage import median_filter
from skimage.feature import canny
from scipy.spatial import ConvexHull
# Parameter visualisasi
nama = 'deteksi wilayah air gunung rinjani'
latitude = -7.5
longitude = 112.5
radius = 100
seleksi = 'RHD'
interpolasi = '0'
deteksiAir = '0'
pohon = '0'

# Hitung ukuran visualisasi
radiusBaris = radius
radiusKolom = radius
ukuran_baris = radiusBaris * 2 + 1
ukuran_kolom = radiusKolom * 2 + 1
luas = ((ukuran_baris - 1) * 30) * ((ukuran_kolom - 1) * 30)

# Mapping koordinat
barisKoma, kolomKoma = mapping.MappingLatLongkeBarisKolom(latitude, longitude)
if seleksi == 'RHD':
    barisMatriks, kolomMatriks = seleksiRHD.seleksiRHD(barisKoma, kolomKoma)
else:
    barisMatriks, kolomMatriks = seleksiBF.seleksiBF(barisKoma, kolomKoma)

# Pilih data DEM
matrikBesar, baris, kolom = pilih.pilih(barisMatriks, kolomMatriks, latitude, longitude)

pixelBarisAwal = baris - radiusBaris
pixelKolomAwal = kolom - radiusKolom

# Potong data DEM untuk visualisasi
matrikKecil = np.zeros((ukuran_baris, ukuran_kolom), dtype=np.float32)
for i in range(ukuran_baris):
    for j in range(ukuran_kolom):
        #print(f"i: {i + d1}, j: {j + d2}")
        matrikKecil[i, j] = matrikBesar[i + pixelBarisAwal, j + pixelKolomAwal]


matrikKecil = np.flipud(matrikKecil) #pembalikan karena (0,0) di matrik dari kiri atas sedangkan grafik dari kiribawah




luasWilayahAir = 0
if deteksiAir == '1':
    a = matrikKecil.copy()
    m, n = a.shape
    b1 = a.reshape(1, m * n)
    c = np.bincount(b1.astype(int).flatten())
    x = np.argmax(c)

    bar, col = np.where(a == x)
    tempA = np.zeros((m, n))
    for i in range(len(bar)):
        tempA[bar[i], col[i]] = 1

    tempB = median_filter(tempA, size=(6, 6))
    bar, col = np.where(tempB == 1)
    for i in range(len(bar)):
        matrikKecil[bar[i], col[i]] = np.nan

    tempC = canny(tempB)
    bar, col = np.where(tempC == 1)

    susunan = np.column_stack((bar, col))
    m = susunan.shape[0]
    barisAir = np.zeros(m)
    kolomAir = np.zeros(m)
    tinggiAir = np.full(m, x)

    barisAwal = 0
    kolomAwal = 0
    counter = 0

    while susunan.size > 0:
        dmin = np.inf
        for j in range(susunan.shape[0]):
            d = (susunan[j, 0] - barisAwal) ** 2 + (susunan[j, 1] - kolomAwal) ** 2
            if d < dmin:
                dmin = d
                index = j

        barisAwal, kolomAwal = susunan[index]
        susunan = np.delete(susunan, index, axis=0)
        barisAir[counter] = barisAwal
        kolomAir[counter] = kolomAwal
        counter += 1

    if len(barisAir) > 2:
        hull = ConvexHull(np.column_stack((barisAir, kolomAir)))
        luasWilayahAir = hull.volume * 900

    print(f'Luas Wilayah Air: {luasWilayahAir} m^2')

# Interpolasi
if interpolasi == '1':  # Pemilihan interpolasi
    interval = 15
    kolomUtara = radiusKolom  * 2
    barisUtara = radiusBaris * 2  * 2
    kolomTengah = radiusKolom  * 2
    barisTengah = radiusBaris * 2
    ukuran_kolom = ukuran_kolom * 2 - 1
    ukuran_baris = ukuran_baris * 2 - 1
    matrikKecil = interpolasiLinier.interpolasiLinier(matrikKecil)  # Asumsi interpolasiLinier adalah modul/fungsi yang diimport

else:
    interval = 30
    kolomUtara = radiusKolom
    barisUtara = radiusBaris * 2
    kolomTengah = radiusKolom
    barisTengah = radiusBaris


# Buat koordinat X dan Y untuk StructuredGrid
x = np.arange(0,ukuran_kolom,dtype=np.float32)
y = np.arange(0, ukuran_baris,dtype=np.float32)

X, Y = np.meshgrid(x, y)
# Buat StructuredGrid untuk PyVista
#b_fixed = np.flipud(np.rot90(b, k=1))
#b = b_fixed
grid = pv.StructuredGrid(X, Y, matrikKecil)

# Visualisasi dengan PyVista
plotter = pv.Plotter()

matrikKecil = np.rot90(np.fliplr(matrikKecil), k=1)

# --- Analisis Flow Accumulation dengan Whitebox ---
# Buat direktori sementara untuk menyimpan file raster sementara
temp_dir = tempfile.mkdtemp()

input_raster_path = os.path.join(temp_dir, "dem.tif")
output_fd_path = os.path.join(temp_dir, "flow_direction.tif")
output_fa_path = os.path.join(temp_dir, "flow_accumulation.tif")

# Simpan matrikKecil sebagai raster GeoTIFF sementara
import rasterio
from rasterio.transform import from_origin

transform = from_origin(0, ukuran_baris, 1, 1)  # asumsi resolusi 1, bisa diatur sesuai DEM asli

with rasterio.open(
    input_raster_path,
    'w',
    driver='GTiff',
    height=matrikKecil.shape[0],
    width=matrikKecil.shape[1],
    count=1,
    dtype='float32',
    crs='+proj=latlong',
    transform=transform,
) as dst:
    dst.write(matrikKecil, 1)

# Jalankan whitebox tools
wbt = WhiteboxTools()
wbt.set_working_dir(temp_dir)

# Flow direction dan accumulation
wbt.d8_pointer(dem=input_raster_path, output=output_fd_path)
wbt.d8_flow_accumulation(input=output_fd_path, output=output_fa_path, out_type='cells')

# Baca kembali hasil flow accumulation
with rasterio.open(output_fa_path) as src:
    flow_accum = src.read(1)

# Normalisasi (log skala)
flow_accum_log = np.log1p(flow_accum)
flow_accum_norm = (flow_accum_log - np.min(flow_accum_log)) / (np.max(flow_accum_log) - np.min(flow_accum_log))

















plotter.set_scale(1, 1, 0.033333)

terrain_colors = plt.get_cmap("terrain")(np.linspace(0, 1, 256))
zmin = np.min(matrikKecil)
if zmin == 0:
    terrain_colors[0] = [1, 1, 1, 1]  # Ubah warna nilai terendah menjadi putih
custom_terrain = LinearSegmentedColormap.from_list("custom_terrain", terrain_colors)
plotter.add_mesh(grid, scalars=matrikKecil.flatten(), cmap=custom_terrain, show_edges=False,pickable=True)
# Tambahkan visualisasi flow accumulation (overlay semi transparan)
plotter.add_mesh(grid, scalars=flow_accum_norm.flatten(), cmap="Blues", opacity=0.4, show_edges=False, name="Flow Accumulation")

lastTextActor = None
def callback(point, idx):
    global lastTextActor
    barisKlik = (point[0])
    kolomKlik= (point[1])
    ketinggianKlik = (point[2])
    print(f"point: {point}")
    if lastTextActor is not None:
        plotter.remove_actor(lastTextActor)
    barisKonversi = barisMatriks - radiusBaris + barisKlik
    kolomKonversi = kolomMatriks - radiusKolom + kolomKlik
    latitudePoint,longitudePoint=mapping.MappingBarisKolomKeLatLong(barisKonversi, kolomKonversi, latitude, longitude, interval)
    lastTextActor=plotter.add_text(f"latitude: {latitudePoint}, longitude: {longitudePoint}, altitude : {ketinggianKlik} meter(s)", font_size=12, position="upper_left")



plotter.enable_point_picking(callback=callback, use_picker=True, show_point=True, color="red", point_size=5, show_message=False)








scale_factor = 0.05
barisUtara = barisUtara -1
# Buat garis
#line = pv.Line(pointA, pointB)
ketinggianTitikTengah = matrikKecil[barisTengah,kolomTengah]
ketinggianTitikUtara = matrikKecil[barisUtara,kolomUtara]
tinggicone = ukuran_baris * scale_factor
radiuscone = tinggicone * 0.05
zConeTengah = round(ketinggianTitikTengah + tinggicone / 2)
zConeUtara= round(ketinggianTitikUtara + tinggicone / 2)
coneTengah = pv.Cone(center=(kolomTengah,barisTengah, zConeTengah), radius=radiuscone, height=tinggicone, direction=(0, 0, 1))
coneUtara = pv.Cone(center=(kolomUtara,barisUtara,zConeUtara), radius=radiuscone, height=tinggicone, direction=(0, 0, 1))
plotter.add_mesh(coneTengah, color="red",specular=1.0,show_edges=True)
plotter.add_mesh(coneUtara, color="magenta",specular=1.0,show_edges=True)
points = np.array([
    [kolomTengah, barisTengah, zConeTengah],
    [kolomUtara, barisUtara, zConeUtara]
], dtype=float)

labels = ["center", "North"]
plotter.add_point_labels(points, labels,text_color='red', point_color='red', point_size=10, font_size=12, fill_shape=False,shadow=False)

print(f"ztitik: {ketinggianTitikTengah}, barisTengah: {barisTengah}, kolomTengah: {kolomTengah}")

plotter.show_axes()  # Menampilkan sumbu X, Y, Z
plotter.show_bounds(xtitle='Sumbu X', ytitle='Sumbu Y', ztitle='Ketinggian (m)')
plotter.show_axes_all()
plotter.view_xy()
plotter.show()
