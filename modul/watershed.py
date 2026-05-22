import numpy as np
import rasterio
import os

#from main import state
from modul import config as cfg, fileHandler
from whitebox.whitebox_tools import WhiteboxTools

wbt = WhiteboxTools()
# def plot(matrikplot, judul):
#     plt.figure(figsize=(6, 6))
#     # Tampilkan dengan colormap 'viridis' dan tanpa interpolasi halus
#     im = plt.imshow(matrikplot, cmap='coolwarm', interpolation='nearest', origin='upper')
#     plt.colorbar(im, label='Nilai matrikKecil')
#     plt.title(judul)
#     plt.xlabel('Kolom')
#     plt.ylabel('Baris')
#     plt.show()


def eksporshp(koordinatpourpoint,transformasi,radius):

    # 1. Baca D8 pointer raster
    dimensi = (radius * 2)+1
    matrikPoutpoint = np.zeros((dimensi, dimensi), dtype=np.uint8)
    print(f"di exportshp before max {np.max(matrikPoutpoint)} min {np.min(matrikPoutpoint)}")
    print("koordinat ")
    for row, col, slid, *_ in koordinatpourpoint:
        row = (dimensi-1) - int(row) #merubah orientasi karena pyvista 0,0 di kiri bawah
        matrikPoutpoint[int(row),int(col)] = 1
        print(f"slid {slid} baris {int(row)} kolom {int(col)}")
    #plt.plot(matrikstream,"potential outlet","nilai")
    matrikPoutpoint[matrikPoutpoint <= 0] = 0
    print(f"matrik pour point shape {matrikPoutpoint.shape}")
    print(f"di exportshp after max {np.max(matrikPoutpoint)} min {np.min(matrikPoutpoint)}")

    fileHandler.eksporTIF2(matrikOut=matrikPoutpoint, fullPath=cfg.filepourpoint, transformasi=transformasi,
                           crs=cfg.default_crs)


    wbt.raster_to_vector_points(i=cfg.filepourpoint, output=cfg.filepourpointshp)
    #tidak perlu jeson snap to pour point karena titik nya sudah tepat dalam outlet / stream
    #wbt.jenson_snap_pour_points(pour_pts=cfg.filepourpointshp,streams=cfg.fileExtractstreamsbawah,output=cfg.filesnappourpointshp, snap_dist=5)
    wbt.watershed(d8_pntr=cfg.filed8pointer, pour_pts=cfg.filepourpointshp, output=cfg.filewatershed)
    #wbt.watershed(d8_pntr=cfg.filed8pointer, pour_pts=cfg.filepourpointshp, output=cfg.filewatershedinteractive)

def eksporshpinteraktive(koordinatpourpoint,transformasi,radius, state):

    # 1. Baca D8 pointer raster
    dimensi = (radius * 2)+1
    matrikPoutpoint = np.zeros((dimensi, dimensi), dtype=np.uint8)
    print(f"di exportshp before max {np.max(matrikPoutpoint)} min {np.min(matrikPoutpoint)}")
    print("koordinat ")
    for row, col, slid, *_ in koordinatpourpoint:
        #row = (dimensi-1) - int(row) #merubah orientasi karena pyvista 0,0 di kiri bawah
        matrikPoutpoint[int(row),int(col)] = 1
        print(f"slid {slid} baris {int(row)} kolom {int(col)}")
    #plt.plot(matrikstream,"potential outlet","nilai")
    matrikPoutpoint[matrikPoutpoint <= 0] = 0
    print(f"matrik pour point shape {matrikPoutpoint.shape}")
    print(f"di exportshp after max {np.max(matrikPoutpoint)} min {np.min(matrikPoutpoint)}")

    fileHandler.eksporTIF2(matrikOut=matrikPoutpoint, fullPath=cfg.filepourpoint, transformasi=transformasi,
                           crs=cfg.default_crs)
    print(f"berhasil eksport tif interaktif")


    wbt.raster_to_vector_points(i=cfg.filepourpoint, output=cfg.filepourpointshp)

    if state.snap_option == True:
        wbt.jenson_snap_pour_points(pour_pts=cfg.filepourpointshp, streams=cfg.fileExtractstreamsHulu, output=cfg.filepourpointshp, snap_dist = cfg.snap_dist)

    print(f"berhasil raster_to_vector_points interaktif")
    #tidak perlu jeson snap to pour point karena titik nya sudah tepat dalam outlet / stream
    #wbt.jenson_snap_pour_points(pour_pts=cfg.filepourpointshp,streams=cfg.fileExtractstreamsbawah,output=cfg.filesnappourpointshp, snap_dist=5)
    #wbt.watershed(d8_pntr=cfg.filed8pointer, pour_pts=cfg.filepourpointshp, output=cfg.filewatershed)
    wbt.watershed(d8_pntr=cfg.filed8pointer, pour_pts=cfg.filepourpointshp, output=cfg.filewatershedinteractive)
    print(f"watershed {cfg.filewatershedinteractive}")

#matrik gambar watershednya saja
def getwatershed():
    if os.path.exists(cfg.filewatershed):
        with rasterio.open(cfg.filewatershed) as src:
            watershed = src.read(1)  # Ambil band pertama
            print(f"buka file watershed")
            print(watershed.min(), watershed.max())
            # transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil watershed tidak ditemukan")

    print(f"max {np.max(watershed)} min {np.min(watershed)}")
    watershed[watershed < 0] = 0
    print(f"setelah diganti max {np.max(watershed)} min {np.min(watershed)}")
    return  watershed




#matrik gambar watershed dikombinasi FA
def getFAwatershed(matrikFA):
    if os.path.exists(cfg.filewatershed):
        with rasterio.open(cfg.filewatershed) as src:
            watershed = src.read(1)  # Ambil band pertama

            # transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil watershed tidak ditemukan")



    print(f"max {np.max(watershed)} min {np.min(watershed)}")
    watershed[watershed < 0] = 0

    vals, counts = np.unique(watershed[watershed != 0], return_counts=True)

    # 2. Urutkan berdasarkan frekuensi (paling sedikit → paling banyak)
    sorted_vals = vals[np.argsort(counts)]  # urutan nilai dari jarang ke sering

    # 3. Buat mapping ke label baru (mulai dari 1)
    lookup = np.zeros(np.max(watershed) + 1, dtype=int)  # array mapping index-nya langsung
    lookup[sorted_vals] = np.arange(1, len(sorted_vals) + 1)

    # 4. Terapkan mapping ke seluruh array
    result = lookup[watershed]  # lookup berbasis indeks langsung

    # ✅ Hasil akhir
    # print("Array asli:\n", watershed)
    # print("Array setelah relabel:\n", result)
    # print("Lookup table:", lookup)
    watershed = result



    print(f"setelah diganti max {np.max(watershed)} min {np.min(watershed)}")
    matrikFA = np.flipud(matrikFA)
    maxaccum = np.max(matrikFA)
    maxwatershed = np.max(watershed)

    accum_norm = matrikFA / maxaccum if maxaccum != 0 else matrikFA
    watershed_norm = watershed / maxwatershed if maxwatershed != 0 else watershed

    # Gabungkan informasi dari watershed (yang > 0) ke dalam array accum_norm
    # Misalnya dengan penambahan nilai normalisasi (dapat disesuaikan dengan bobot)
    combined = accum_norm.copy()
    mask= (watershed > 0) & (matrikFA < cfg.thresholdminextractstreamshulu)

    combined[mask] += watershed_norm[mask]

    #combined[watershed > 0] += watershed_norm[watershed > 0]  # nilai hanya ditambahkan jika ada DAS

    # Jika ingin memastikan tetap dalam skala 0-1
    combined = combined / np.max(combined)

    # Jika ingin mengembalikan ke skala semula seperti skala accum
    combined_scaled = combined * maxaccum


    return  combined_scaled


def getFAwatershedinteractive(matrikFA):
    if os.path.exists(cfg.filewatershedinteractive):
        with rasterio.open(cfg.filewatershedinteractive) as src:
            watershed = src.read(1)  # Ambil band pertama

            # transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil watershed tidak ditemukan")



    print(f"max interactive {np.max(watershed)} min interactive {np.min(watershed)}")
    watershed[watershed < 0] = 0

    vals, counts = np.unique(watershed[watershed != 0], return_counts=True)

    # 2. Urutkan berdasarkan frekuensi (paling sedikit → paling banyak)
    sorted_vals = vals[np.argsort(counts)]  # urutan nilai dari jarang ke sering

    # 3. Buat mapping ke label baru (mulai dari 1)
    lookup = np.zeros(np.max(watershed) + 1, dtype=int)  # array mapping index-nya langsung
    lookup[sorted_vals] = np.arange(1, len(sorted_vals) + 1)

    # 4. Terapkan mapping ke seluruh array
    result = lookup[watershed]  # lookup berbasis indeks langsung

    # ✅ Hasil akhir
    # print("Array asli:\n", watershed)
    # print("Array setelah relabel:\n", result)
    # print("Lookup table:", lookup)
    watershed = result



    print(f"setelah diganti max {np.max(watershed)} min {np.min(watershed)}")
    matrikFA = np.flipud(matrikFA)
    maxaccum = np.max(matrikFA)
    minaccum = np.min(matrikFA)
    print(f"interaktif maxaccum {maxaccum} minaccum {minaccum}")
    maxwatershed = np.max(watershed)

    accum_norm = matrikFA / maxaccum if maxaccum != 0 else matrikFA
    watershed_norm = watershed / maxwatershed if maxwatershed != 0 else watershed

    # Gabungkan informasi dari watershed (yang > 0) ke dalam array accum_norm
    # Misalnya dengan penambahan nilai normalisasi (dapat disesuaikan dengan bobot)
    combined = accum_norm.copy()
    mask= (watershed > 0) & (matrikFA < cfg.thresholdwatershedinteractive)

    combined[mask] += watershed_norm[mask]

    #combined[watershed > 0] += watershed_norm[watershed > 0]  # nilai hanya ditambahkan jika ada DAS

    # Jika ingin memastikan tetap dalam skala 0-1
    combined = combined / np.max(combined)

    # Jika ingin mengembalikan ke skala semula seperti skala accum
    combined_scaled = combined * maxaccum


    return  combined_scaled