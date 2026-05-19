
import numpy as np
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap
import rasterio, os
import matplotlib.pyplot as plt
import modul.config as cfg

from modul import mapping, seleksiRHD, seleksiBF, pilih, visualCallBack, fileHandler, analisis

# Parameter visualisasi
nama = 'deteksi wilayah air gunung rinjani'

latitude =    -7.9535971422581335
longitude =  112.46697402028734
radius = 100
seleksi = 'RHD'

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


pixelBarisAwalKoordinat = barisMatriks - radiusBaris
pixelKolomAwalKoordinat = kolomMatriks - radiusKolom
#fileHandler.eksporTIF(matrikKecil, latitude, longitude, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat, cfg.fileFlowAccumulationBreachThresholdKetinggian,cfg.default_crs)
fileHandler.eksporTIF(matrikKecil, latitude, longitude, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat, cfg.fileSeleksiDEM, cfg.default_crs)

matrikKecil = np.flipud(matrikKecil) #pembalikan karena (0,0) di matrik dari kiri atas sedangkan grafik dari kiribawah





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
grid = pv.StructuredGrid(X, Y, matrikKecil,force_float=False)

# Visualisasi dengan PyVista
plotter = pv.Plotter()



zmin = np.min(matrikKecil)
print(f"zmin: {zmin}")


plotter.set_scale(1, 1, 0.033333)

terrain_colors = plt.get_cmap("terrain")(np.linspace(0, 1, 256))
zmin = np.min(matrikKecil)
if zmin == 0:
    terrain_colors[0] = [1, 1, 1, 1]  # Ubah warna nilai terendah menjadi putih
custom_terrain = LinearSegmentedColormap.from_list("custom_terrain", terrain_colors)











scale_factor = 0.05
barisUtara = barisUtara -1
# Buat garis
#line = pv.Line(pointA, pointB)
ketinggianTitikTengah = matrikKecil[barisTengah,kolomTengah]
ketinggianTitikUtara = matrikKecil[barisUtara,kolomUtara]
tinggicone = 20.0
radiuscone = 1
zConeTengah = round(ketinggianTitikTengah + tinggicone / 2)
zConeUtara= round(ketinggianTitikUtara + tinggicone / 2)
coneTengah = pv.Cone(center=(kolomTengah,barisTengah, zConeTengah), radius=radiuscone, height=tinggicone, direction=(0, 0, 1))
coneUtara = pv.Cone(center=(kolomUtara,barisUtara,zConeUtara), radius=radiuscone, height=tinggicone, direction=(0, 0, 1))



points = np.column_stack((0, 0, zConeTengah))
print(f"points: {points}")
cloud = pv.PolyData(points)
glyphs = cloud.glyph(geom=coneTengah, scale=False)
#plotter.add_mesh(glyphs, color='yellow')
plotter.add_mesh(coneTengah, color="red",specular=1.0,show_edges=True)
plotter.add_mesh(coneUtara, color="magenta",specular=1.0,show_edges=True)


#print("matrikKecil:")
# for row in matrikKecil:
#     print('\t'.join(f"{val:>3}" for val in row))


koordinatCekungan, matrikFAasli, matrikFAthresholdketinggian = analisis.importFlowAccumulation(matrikKecil, ketinggianTitikTengah,latitude)
fileHandler.eksporTIF(matrikFAthresholdketinggian, latitude, longitude, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat,  cfg.fileFlowAccumulationBreachThresholdKetinggian,cfg.default_crs)
#matrikFAaslicallback = np.rot90(matrikFAasli.copy(), k=-1)
matrikFAaslicallback = np.flipud(matrikFAasli.copy())
callback = visualCallBack.make_callback(
    plotter, latitude, longitude,
    radiusBaris, radiusKolom, barisMatriks, kolomMatriks, matrikFAaslicallback
)

plotter.enable_point_picking(callback=callback, use_picker=True, show_point=True, color="red", point_size=15, show_message=False)



for row in koordinatCekungan:
    px = row[1]
    py = row[0]
    pz = matrikKecil[py, px]
    print(f"px: {px}, py: {py}, pz: {pz}")


    height = 4.0
    radius = 0.1
    center = (px, py, pz + height)  # agar tabung berdiri di atas DEM
    direction = (0, 0, -1)  # arah ke bawah jika mau, tapi cylinder default berdiri

    cylinder = pv.Cylinder(center=center, direction=direction, radius=radius, height=height)
    plotter.add_mesh(cylinder, color='red')

if os.path.exists(cfg.fileBreachDepression):
    with rasterio.open(cfg.fileBreachDepression) as src:
            filebreach = src.read(1)
else:
    raise FileNotFoundError(f"Hasil flow accumulation tidak ditemukan ")

#filebreach = np.flipud(filebreach)
#grid2 = pv.StructuredGrid(X, Y, filebreach)

#print(f"ztitik: {ketinggianTitikTengah}, barisTengah: {barisTengah}, kolomTengah: {kolomTengah}")
#plotter.add_mesh(grid.copy(), scalars=np.rot90(matrikFAasli, k=-1) ,show_edges=False, cmap='coolwarm', opacity=1,show_scalar_bar=False)
#plotter.add_mesh(grid.elevation(), cmap=custom_terrain, show_edges=True,pickable=True, show_scalar_bar=False)
# Salin mesh dan beri data ke cell_data
grid_copy = grid.copy()
grid_copy.cell_data["flow"] = np.rot90(matrikFAasli, k=-1).ravel(order="F")

# Tampilkan mesh dengan data dari sel
plotter.add_mesh(
    grid_copy,
    scalars="flow",              # referensi nama di cell_data
    cmap="coolwarm",
    show_edges=False,
    opacity=1,
    show_scalar_bar=False
)

#plotter.show_axes()  # Menampilkan sumbu X, Y, Z
#plotter.show_bounds(xtitle='Longitude', ytitle='Latitude', ztitle='Ketinggian (m)')
#plotter.show_axes_all()
plotter.view_xy()
plotter.show()
