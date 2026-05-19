import numpy as np
import pyvista as pv
from modul import mapping, seleksiRHD, seleksiBF, pilih, interpolasiLinier
from scipy.ndimage import median_filter
from skimage.feature import canny
from scipy.spatial import ConvexHull
# Parameter visualisasi
nama = 'deteksi wilayah air gunung rinjani'
latitude = -8.401782553201073
longitude = 116.39428802473712
radius = 300
seleksi = 'RHD'
interpolasi = '0'
deteksiAir = '1'
pohon = '0'

# Hitung ukuran visualisasi
radiusBaris = radius
radiusKolom = radius
ukuran_baris = radiusBaris * 2 + 1
ukuran_kolom = radiusKolom * 2 + 1
luas = ((ukuran_baris - 1) * 30) * ((ukuran_kolom - 1) * 30)

# Mapping koordinat
barisKoma, kolomKoma = mapping.mapping(latitude, longitude)
if seleksi == 'RHD':
    barisMatriks, kolomMatriks = seleksiRHD.seleksiRHD(barisKoma, kolomKoma)
else:
    barisMatriks, kolomMatriks = seleksiBF.seleksiBF(barisKoma, kolomKoma)

# Pilih data DEM
A, baris, kolom = pilih.pilih(barisMatriks, kolomMatriks, latitude, longitude)
ztitik = A[baris, kolom]
d1 = baris - radiusBaris - 1
d2 = kolom - radiusKolom - 1

# Potong data DEM untuk visualisasi
b = np.zeros((ukuran_baris, ukuran_kolom))
for i in range(ukuran_baris):
    for j in range(ukuran_kolom):
        b[i, j] = A[i + d1, j + d2]
b = np.flipud(b)
import numpy as np
from scipy.ndimage import median_filter
from skimage.feature import canny
from scipy.spatial import ConvexHull

luasWilayahAir = 0
if deteksiAir == '1':
    a = b.copy()
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
        b[bar[i], col[i]] = np.nan

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
if interpolasi == '1':
    b = interpolasiLinier.interpolasiLinier(b)

# Buat koordinat X dan Y untuk StructuredGrid
x = np.arange(0, ukuran_kolom)
y = np.arange(0, ukuran_baris)
X, Y = np.meshgrid(x, y)

# Buat StructuredGrid untuk PyVista
#b_fixed = np.flipud(np.rot90(b, k=1))
#b = b_fixed
grid = pv.StructuredGrid(X, Y, b,force_float=False)

# Visualisasi dengan PyVista
plotter = pv.Plotter()

b_rotated = np.rot90(np.fliplr(b),k=1)


plotter.add_mesh(grid, scalars=b_rotated.flatten(), cmap="jet", show_edges=False)
plotter.set_scale(1, 1, 0.0333)

plotter.show_axes()  # Menampilkan sumbu X, Y, Z
plotter.show_bounds()
plotter.view_xy()
plotter.show()
