from OpenGL.wrapper import none_or_pass

from modul import config as cfg  # Mengimpor file konfigurasi, berisi path dan parameter
from modul import konverter, fileHandler, watershed, plotter as pla
import numpy as np              # Untuk manipulasi array numerik
import rasterio                 # Untuk membaca file raster GeoTIFF
import os                       # Untuk operasi file & path
from whitebox.whitebox_tools import WhiteboxTools  # Library untuk analisis geospasial


# Raster tampilan


#menghitung panjang x lebar visualsisasi menggunakan epsg EPSG:4326
# Ambil path direktori sementara dari konfigurasi
temp_dir = cfg.pathTempMaps

# Inisialisasi alat WhiteboxTools
wbt = WhiteboxTools()
wbt.set_working_dir(temp_dir)  # Set direktori kerja

# Fungsi utama untuk menjalankan analisis Flow Accumulation menggunakan algoritma MD∞

def breachdepression():
    # --- Analisis Flow Accumulation dengan Whitebox (MD∞) ---
    # Breaching depressions (mengatasi cekungan palsu) pada DEM menggunakan metode least-cost
    wbt.breach_depressions_least_cost(
        dem=cfg.fileSeleksiDEM,
        output=cfg.fileBreachDepression,
        min_dist=True,
        fill=True,
        flat_increment=0.01,
        dist=2
    )
    if os.path.exists(cfg.fileBreachDepression):
        with rasterio.open(cfg.fileBreachDepression) as src:
            matrikbreachdepression = src.read(1)  # Ambil band pertama
            #transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil fileBreachDepression tidak ditemukan")

    return matrikbreachdepression

def analisisFlowAccumulation():

    # Hitung flow accumulation menggunakan metode MD∞ (Multiple-Direction Infinite)
    wbt.md_inf_flow_accumulation(
        dem=cfg.fileBreachDepression,
        output=cfg.fileFlowAccumulationBreachMDInf,
        out_type='cells'
    )
    wbt.d8_pointer(dem=cfg.fileBreachDepression, output=cfg.filed8pointer)
    wbt.d8_flow_accumulation(i=cfg.filed8pointer, output=cfg.fileFlowAccumulationBreachD8, out_type="cells", pntr=True)

    # Baca hasil dari file GeoTIFF hasil flow accumulation
    if os.path.exists(cfg.fileFlowAccumulationBreachMDInf):
        with rasterio.open(cfg.fileFlowAccumulationBreachMDInf) as src:
            flow_accum_MDInf = src.read(1) # Ambil band pertama
            transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil flow_accum_MDInf tidak ditemukan")

    if os.path.exists(cfg.fileFlowAccumulationBreachD8):
        with rasterio.open(cfg.fileFlowAccumulationBreachD8) as src:
            flow_accum_D8 = src.read(1)  # Ambil band pertama
            #transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil flow_accum_MDInf tidak ditemukan")

    if os.path.exists(cfg.filed8pointer):
        with rasterio.open(cfg.filed8pointer) as src:
            d8fd = src.read(1)  # Ambil band pertama
            #transformasi = src.transform
    else:
        raise FileNotFoundError("Hasil flow_accum_MDInf tidak ditemukan")



    # Catatan: Normalisasi logaritmik dinonaktifkan, bisa diaktifkan jika perlu skala log


    return flow_accum_MDInf, flow_accum_D8, transformasi  # Kembalikan matriks flow accumulation



# Fungsi untuk mengimpor dan memproses flow accumulation hanya pada area tertentu (matrikKecil)
def importFlowAccumulation(matrikKecil, titikTengah, latitude_deg, radius, meshoption,state):
    try:
        # Jalankan analisis flow accumulation dan simpan matriks hasil asli
        flow_accum_MDINF,flow_accum_D8,transformasi = analisisFlowAccumulation()

        # Salin dan balikkan matriks secara vertikal (flip up-down)
        matrikFA = flow_accum_D8.copy()


        # Bersihkan data dari NaN dan inf
        print(f"sum 1 {np.sum(matrikFA)}")
        matrikFA[np.isnan(matrikFA)] = 0
        matrikFA[np.isinf(matrikFA)] = 0
        print(f"sum 2 {np.sum(matrikFA)}")

        # Nol-kan bagian yang nilainya di bawah titik tengah dari matrikKecil
        # delta ketinggian titik tengah dengan outlet bisa di set
        # hal ini akan terlihat bedanya di dataran rendah bisa tidak relevan jika deltanya beda dikit

        matrikKecil = np.flipud(matrikKecil)
        tinggi, lebar = matrikKecil.shape
        # matrikecil2 = matrikKecil.copy()
        for i in range(tinggi):
            for j in range(lebar):
               #print(f"i {i}, j {j}")
                if matrikKecil[i, j] <= titikTengah:
                    matrikFA[i, j] = 0
                    # matrikecil2[i, j] = 0


        #simpan file tif FA dengan threshold ketinggian

        fileHandler.eksporTIF2(matrikOut=matrikFA, fullPath=cfg.fileFlowAccumulationBreachD8Thresholdketinggian, transformasi=transformasi,
                               crs=cfg.default_crs)

        # print(f"titik tengah {titikTengah}")
        # print(f"max matrik kecil {np.max(matrikecil2)}")
        # print(f"min matrik kecil {np.min(matrikecil2[matrikecil2>0])}")
        # pla.plot(matrikecil2,"a","a")
       #fileHandler.eksporTIF2(matrikOut=matrikFA, fullPath=cfg.fileFlowAccumulationBreachThresholdKetinggian, transformasi=transformasi, crs=cfg.default_crs)
        #pla.plot(matrikFA,"D8 FA with elevation threshold","Upstream contributing cell count")
        #seleksi percentile 90
        #seleksimeanmedian

        # Hitung nilai unik dan jumlah kemunculannya ambil nilai yang lebih dari 1
        # 0 atau 1 berarti tidak mengalir ke sel tersebut
        nilaiFAunik = np.unique(matrikFA.astype(int)) #cari nilai fa unik
        nilaiFAunik = nilaiFAunik[nilaiFAunik > 0][::-1] #urutkan yang terbesar
        print(f"nilaiFAunik {nilaiFAunik}")
        for row in nilaiFAunik:
            print(row)
        print(nilaiFAunik.dtype)
        for row in nilaiFAunik: #cetak nilai fa unik dari yang terbesar
            print(f"nilaiFAunik {row}")

        dynamicthreshold = np.percentile(nilaiFAunik, cfg.percentile)




        print(f"dynamicthreshold {dynamicthreshold}")


        #ekstraksi stream
        #matrikFAwatershed = matrikFA.copy()
        # plot(matrikFA, "before 1 matrikfa")
        # plot(matrikFAwatershed, "before 1  matrikFAwatershed")

        matrikFA[matrikFA < dynamicthreshold] = 0
        #matrikFAwatershed[matrikFAwatershed < dynamicthresholdbawah] = 0
        # plot(matrikFA, "before 2 matrikfa")
        # plot(matrikFAwatershed, "before 2  matrikFAwatershed")

        matrikFA[matrikFA >= dynamicthreshold] = 1
        #matrikFAwatershed[matrikFAwatershed>=dynamicthresholdbawah] = 1
        #
        # plot(matrikFA,"after matrikfa")
        # plot(matrikFAwatershed, "after matrikFAwatershed")
       # plt.plot(matrikFAwatershed, "Extract stream 20th percentile", "Upstream contributing cell count")

        #simpan matrik ekstraksi ke tif
        fileHandler.eksporTIF2(matrikOut=matrikFA, fullPath=cfg.fileExtractstreams,transformasi=transformasi, crs=cfg.default_crs)
        #fileHandler.eksporTIF2(matrikOut=matrikFAwatershed, fullPath=cfg.fileExtractstreamsbawah, transformasi=transformasi,
        #                       crs=cfg.default_crs)
        #bagian identifikasi stream
        wbt.stream_link_identifier(d8_pntr=cfg.filed8pointer, streams=cfg.fileExtractstreams,
                                   output=cfg.fileStreamslinkidentifier, zero_background=True)
        with rasterio.open(cfg.fileStreamslinkidentifier) as src:
            matrikstreamkinkidentifier = np.flipud(src.read(1))
            #pla.plot(matrikstreamkinkidentifier, "matrikstreamkinkidentifier", "meter")
        matrikKecil = np.flipud(matrikKecil)
        # flow_accum_MDINF = np.flipud(flow_accum_MDINF)

        rows, cols = np.nonzero(matrikstreamkinkidentifier)
        values = matrikstreamkinkidentifier[rows, cols]
        # print(f"values {values}")
        # Gabungkan menjadi array N x 3 (baris, kolom, nilai)
        stackstream = np.stack((rows, cols, values), axis=1)
        # print(f"identifier {values}")
        # print(f"stackstream {stackstream}, {stackstream.dtype}")
        outlet = []
        #clusters = max(values)  # jumlah cluster
        clusters = np.unique(stackstream[:, 2])
        print(clusters)
        elv = 0
        flow_accum_MDINF = np.flipud(flow_accum_MDINF)#dibalik menyesuaikan pyvista baris 0 di bawah
        for cid in clusters:
            cluster_data = stackstream[stackstream[:, 2] == cid]
            # print(f"cluster_data {cluster_data}, {cluster_data.dtype}")
            max_FA = -np.inf
            altitude = -np.inf
            luasdas = 0
            best_row, best_col = -1, -1

            for row, col, _ in cluster_data:
                nilai = matrikFA[int(row), int(col)]
                print(f"row {row}, col {col}, nilai {nilai}")
                if (nilai > max_FA) & (matrikKecil[row, col] > titikTengah):
                #if (nilai > max_FA):
                    max_FA = nilai
                    max_FAMDIF = flow_accum_MDINF[int(row), int(col)]
                    best_row, best_col = row, col
                    elv = matrikKecil[row, col]
                    luasdas = konverter.cells_to_km2(flow_accum_MDINF[row, col], latitude_deg)

            outlet.append([best_row, best_col, cid, max_FAMDIF, elv, luasdas])
            # print(f"outlet {outlet}")
            # for row in outlet:
            #     print(row)

        # print("\n1 Outlet sebelum diurutkan berdasarkan max_FA:")
        # for row in outlet:
        #     print(row)
        outlet = sorted(outlet, key=lambda x: x[3])
        # print("\n2 Outlet sebelum diurutkan berdasarkan cid:")
        # for row in outlet:
        #     print(row)
        for i, row in enumerate(outlet):
            row[2] = i + 1  # ubah CID di kolom ke-3
        # print("\n 3 Outlet setelah diurutkan berdasarkan max_FA:")
        # for row in outlet:
        #     print(row)
        koordinatpourpoint = np.array(outlet)
        print(f"koordinatpourpoint before")
        for row in koordinatpourpoint:
            print(" ".join(str(int(x)) if float(x).is_integer() else str(x) for x in row))


#==============================================================================
        # hapus pasangan titik yang berdekatan (keduanya dihapus)
        to_remove = set()
        for i, p1 in enumerate(koordinatpourpoint):
            for j, p2 in enumerate(koordinatpourpoint):
                if i >= j:
                    continue
                r1, c1 = p1[0], p1[1]
                r2, c2 = p2[0], p2[1]
                if abs(r1 - r2) <= 3 and abs(c1 - c2) <= 3:
                    to_remove.add(i)
                    to_remove.add(j)

        # simpan hanya titik yang tidak termasuk pasangan berdekatan
        koordinatpourpoint = np.array([
            p for i, p in enumerate(koordinatpourpoint)
            if i not in to_remove
        ])
# ==============================================================================




        print(f"koordinatpourpoint after")
        for row in koordinatpourpoint:
            print(" ".join(str(int(x)) if float(x).is_integer() else str(x) for x in row))



        if meshoption in ("watershed", "FAwatershed"):
            watershed.eksporshp(koordinatpourpoint, transformasi, radius)

        cellanaliss = (radius * 2)
        state.luasanalisis, state.panjanghorizontal, state.panjangvertikal = konverter.cells_to_km_dual(cellanaliss, latitude_deg)

        # Tampilkan koordinat cekungan
        urutan = 1
        for i, j, cid, max_FA, elv, luasdas in  koordinatpourpoint:
            print(f"{urutan} : Baris: {i:>3}, Kolom: {j:>3}, cid {cid},Hasil FA jumlah cells {max_FA:>7.2f}, Luas daerah tangkapan AIR (A) {luasdas:>7.2f} km2, Elevasi: {elv:>7.2f}")
            urutan += 1
        state.jumlahoutlet = np.max(koordinatpourpoint[:,2])

        return koordinatpourpoint, flow_accum_MDINF
        #return koordinatpourpoint, matrikstreamkinkidentifier # Kembalikan hasil dan matriks asli
    # else:
    #     # Jika threshold terlalu tinggi (melebihi jumlah nilai unik)
    #     print("❌ Index thresholdFlowAccumulation melebihi panjang hasil. Perhitungan dibatalkan.")
    #     return [], flow_accum_MDINF

    except Exception as e:
        # Tangani error jika terjadi kesalahan saat proses
        print(f"[ERROR] Gagal impor GeoTIFF: {e}")
