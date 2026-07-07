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

    #untukhitung rational method
    wbt.extract_streams(flow_accum=cfg.fileFlowAccumulationBreachD8, output=cfg.fileExtractstreamsHulu, threshold=cfg.thresholdminextractstreamshulu)
    wbt.tributary_identifier(d8_pntr=cfg.filed8pointer, streams=cfg.fileExtractstreamsHulu,output=cfg.filetributaryidentifier)


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
            minFAD8 = np.min(flow_accum_D8)
            print(f"minFAD8 {minFAD8}")
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
    if os.path.exists(cfg.filetributaryidentifier):
        with rasterio.open(cfg.filetributaryidentifier) as src:
            matriktributaryidentifier = src.read(1)  # Ambil band pertama

    else:
        raise FileNotFoundError("Hasil filetributaryidentifier tidak ditemukan")

    return flow_accum_MDInf, flow_accum_D8, transformasi,matriktributaryidentifier  # Kembalikan matriks flow accumulation



# Fungsi untuk mengimpor dan memproses flow accumulation hanya pada area tertentu (matrikKecil)
def importFlowAccumulation(matrikKecil, titikTengah, latitude_deg, radius, meshoption,state):
    try:
        # Jalankan analisis flow accumulation dan simpan matriks hasil asli
        flow_accum_MDINF,flow_accum_D8,transformasi,matriktributaryidentifier = analisisFlowAccumulation()

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
        #tinggi, lebar = matrikKecil.shape
        # matrikecil2 = matrikKecil.copy()
        # for i in range(tinggi):
        #     for j in range(lebar):
        #        #print(f"i {i}, j {j}")
        #         if matrikKecil[i, j] <= titikTengah:
        #             matrikFA[i, j] = 0
        #             # matrikecil2[i, j] = 0

        # KODE OPTIMASI (Seketika selesai) kode baru gantikan loop bersyarat diatas
        matrikFA[matrikKecil <= titikTengah] = 0


        #simpan file tif FA dengan threshold ketinggian
        print(f"fa threshold elevasi 1")
        if cfg.demomode:
            pla.plot(matrikFA,"FA threshold elevasi", "Flow Accumulation Cell Count")
        fileHandler.eksporTIF2(matrikOut=matrikFA, fullPath=cfg.fileFlowAccumulationBreachD8Thresholdketinggian, transformasi=transformasi,
                               crs=cfg.default_crs)
        matrikFAD8elevasi = matrikFA.copy()
        # print(f"titik tengah {titikTengah}")R
        # print(f"max matrik kecil {np.max(matrikecil2)}")
        # print(f"min matrik kecil {np.min(matrikecil2[matrikecil2>0])}")
        # pla.plot(matrikecil2,"a","a")
       #fileHandler.eksporTIF2(matrikOut=matrikFA, fullPath=cfg.fileFlowAccumulationBreachThresholdKetinggian, transformasi=transformasi, crs=cfg.default_crs)
        #pla.plot(matrikFA,"D8 FA with elevation threshold","Upstream contributing cell count")
        #seleksi percentile 90
        #seleksimeanmedian

        # Hitung nilai unik dan jumlah kemunculannya ambil nilai yang lebih dari 1
        # 0 atau 1 berarti tidak mengalir ke sel tersebut
        # Ambil hanya piksel yang ada aliran airnya (hemat memori sangat drastis)
        matrikFA_valid = matrikFA[matrikFA > 0].astype(int)
        # Cari nilai unik hanya dari data yang sudah disaring
        nilaiFAunik = np.unique(matrikFA_valid)[::-1]
        # print(f"nilaiFAunik {nilaiFAunik}")
        # for row in nilaiFAunik:
        #     print(row)
        # print(nilaiFAunik.dtype)
        # for row in nilaiFAunik: #cetak nilai fa unik dari yang terbesar
        #     print(f"nilaiFAunik {row}")

        dynamicthreshold = round(np.percentile(nilaiFAunik, cfg.percentile),2)
        # dynamicthresholdmin = np.percentile(nilaiFAunik, cfg.percentilemin)
        # cfg.thresholdminextractstreamshulu = dynamicthresholdmin
        # print(f"cfg.thresholdminextractstreamshulu  {cfg.thresholdminextractstreamshulu} ")
        state.dynamicthreshold = dynamicthreshold



        print(f"dynamicthreshold {dynamicthreshold}")


        #ekstraksi stream
        #matrikFAwatershed = matrikFA.copy()
        # plot(matrikFA, "before 1 matrikfa")
        # plot(matrikFAwatershed, "before 1  matrikFAwatershed")
        #pla.plot(matrikFA, "before 2  matrikFAwatershed", "FA")
        matrikFA[matrikFA < dynamicthreshold] = 0
        #matrikFAwatershed[matrikFAwatershed < dynamicthresholdbawah] = 0
        #plot(matrikFA, "before 2 matrikfa")


        matrikFA[matrikFA >= dynamicthreshold] = 1
        #matrikFAwatershed[matrikFAwatershed>=dynamicthresholdbawah] = 1
        #
        # plot(matrikFA,"after matrikfa")
        #pla.plot(matrikFA, "after 2  matrikFAwatershed", "FA")
       # plt.plot(matrikFAwatershed, "Extract stream 20th percentile", "Upstream contributing cell count")

        #simpan matrik ekstraksi ke tif
        fileHandler.eksporTIF2(matrikOut=matrikFA, fullPath=cfg.fileExtractstreams,transformasi=transformasi, crs=cfg.default_crs)
        #wbt.extract_streams(flow_accum=cfg.fileFlowAccumulationBreachMDInf, output=cfg.fileExtractstreamsHuluMDINF,
         #                   threshold=cfg.thresholdminextractstreamshulu)

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


        #==========================================================================
        #bagian mengurutkan titik FA yang besar dari setiap aliran kemudian menghapusnya jika merupakan aliran cabang
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
        flow_accum_D8 = np.flipud(flow_accum_D8)
        flow_accum_MDINF = np.flipud(flow_accum_MDINF)#dibalik menyesuaikan pyvista baris 0 di bawah
        for cid in clusters:
            cluster_data = stackstream[stackstream[:, 2] == cid]
            # print(f"cluster_data {cluster_data}, {cluster_data.dtype}")
            # max_FA = -np.inf
            # elv = -np.inf
            # luasdas = 0
            # best_row, best_col = -1, -1
            #
            # for row, col, _ in cluster_data:
            #     nilai = flow_accum_D8[int(row), int(col)]
            #     print(f"row {row}, col {col}, nilai {nilai}")
            #     if (nilai > max_FA) & (matrikKecil[row, col] > titikTengah):
            #     #if (nilai > max_FA):
            #
            #         max_FA = nilai
            #         max_FAMDIF = flow_accum_MDINF[int(row), int(col)]
            #         print(f"max_FA {max_FA}")
            #         print(f"max_FAMDIF {max_FAMDIF}")
            #         #max_FAMDIF = max_FA
            #         best_row, best_col = row, col
            #         elv = matrikKecil[row, col]
            #         luasdas = konverter.cells_to_km2(flow_accum_MDINF[row, col], latitude_deg)[0]
            #
            # outlet.append([best_row, best_col, cid, max_FAMDIF, elv, luasdas])

            #optimasi kecepatan kode
            # Inisialisasi nilai bawaan jika tidak ada yang memenuhi syarat
            max_FA = -np.inf
            max_FAMDIF = 0  # Tambahkan inisialisasi ini agar tidak error saat di-append jika tidak ada yang valid
            elv = -np.inf
            luasdas = 0
            best_row, best_col = -1, -1

            # Konversi kolom menjadi integer array agar bisa dipakai sebagai indeks
            rows_idx = cluster_data[:, 0].astype(int)
            cols_idx = cluster_data[:, 1].astype(int)

            # Ambil array nilai FA dan Ketinggian secara simultan tanpa loop
            nilai_fa_arr = flow_accum_D8[rows_idx, cols_idx]
            ketinggian_arr = matrikKecil[rows_idx, cols_idx]

            # Buat kondisi mask (hanya yang elevasi > titikTengah)
            valid_mask = ketinggian_arr > titikTengah

            if np.any(valid_mask):
                # Ekstrak data yang valid saja (yang elevasinya di atas titikTengah)
                valid_rows = rows_idx[valid_mask]
                valid_cols = cols_idx[valid_mask]
                valid_fa = nilai_fa_arr[valid_mask]

                # Temukan index dari nilai FA tertinggi di dalam array yang sudah divalidasi
                best_idx = np.argmax(valid_fa)

                # Assign nilai akhir berdasarkan index terbaik
                max_FA = valid_fa[best_idx]
                best_row = valid_rows[best_idx]
                best_col = valid_cols[best_idx]

                elv = matrikKecil[best_row, best_col]
                max_FAMDIF = flow_accum_MDINF[best_row, best_col]
                luasdas = konverter.cells_to_km2(max_FAMDIF, latitude_deg)[0]

                # (Opsional) Jika ingin tetap print nilai max seperti kode asli:
                print(f"max_FA {max_FA}")
                print(f"max_FAMDIF {max_FAMDIF}")

            # Masukkan ke list outlet
            outlet.append([best_row, best_col, cid, max_FAMDIF, elv, luasdas])
            # print(f"outlet {outlet}")
            # for row in outlet:
            #     print(row)

        print("\n1 Outlet sebelum diurutkan berdasarkan max_FA:")
        for row in outlet:
            print(row)
        outlet = sorted(outlet, key=lambda x: x[3])
        print("\n2 Outlet sebelum diurutkan berdasarkan cid:")
        for row in outlet:
            print(row)
        for i, row in enumerate(outlet):
            row[2] = i + 1  # ubah CID di kolom ke-3
        print("\n 3 Outlet setelah diurutkan berdasarkan max_FA:")
        for row in outlet:
            print(row)
        koordinatpourpoint = np.array(outlet)
        print(f"koordinatpourpoint before")
        for row in koordinatpourpoint:
            print(" ".join(str(int(x)) if float(x).is_integer() else str(x) for x in row))


#==============================================================================
        # hapus pasangan titik yang berdekatan (keduanya dihapus)
        # pastikan baris & kolom bertipe integer
        koordinatpourpoint[:, 0:2] = koordinatpourpoint[:, 0:2].astype(int)

        # untuk debugging: cek nilai baris dan kolom
        print("\nKoordinat sebelum filter:")
        for row in koordinatpourpoint:
            print(*row)

        # hapus pasangan titik yang berdekatan (keduanya dihapus)
        #menghapus aliran percabangan
        # to_remove = set()
        # n = len(koordinatpourpoint)
        # for i in range(n):
        #     r1, c1 = koordinatpourpoint[i, 0], koordinatpourpoint[i, 1]
        #     for j in range(i + 1, n):
        #         r2, c2 = koordinatpourpoint[j, 0], koordinatpourpoint[j, 1]
        #         if abs(r1 - r2) <= cfg.thresholdojarakutletbedekatan and abs(c1 - c2) <= cfg.thresholdojarakutletbedekatan:
        #             print(f"Hapus pasangan dekat: index {i} ({r1},{c1}) dan {j} ({r2},{c2})")
        #             to_remove.add(i)
        #             to_remove.add(j)

        #optimasi
            # Ekstrak kolom baris dan kolom saja
            coords = koordinatpourpoint[:, 0:2].astype(int)

            # Hitung selisih jarak absolut (baris dan kolom) untuk semua kombinasi titik sekaligus
            diff_row = np.abs(coords[:, 0, None] - coords[:, 0])
            diff_col = np.abs(coords[:, 1, None] - coords[:, 1])

            # Cek kondisi threshold
            close_mask = (diff_row <= cfg.thresholdojarakutletbedekatan) & (
                        diff_col <= cfg.thresholdojarakutletbedekatan)

            # Abaikan jarak titik dengan dirinya sendiri (diagonal matriks bernilai False)
            np.fill_diagonal(close_mask, False)

            # Dapatkan index titik mana saja yang melanggar kondisi
            to_remove_arr = np.where(close_mask)[0]
            to_remove = set(to_remove_arr)

        koordinatpourpoint = np.delete(koordinatpourpoint, list(to_remove), axis=0)

        print("\nKoordinat sesudah filter:")
        for row in koordinatpourpoint:
            print(*row)
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
            state.jumlahoutlet = urutan
            urutan += 1

        print(f"oke")




        return koordinatpourpoint, flow_accum_MDINF, np.flipud(flow_accum_D8),matriktributaryidentifier,transformasi, matrikFAD8elevasi
        #return koordinatpourpoint, matrikstreamkinkidentifier # Kembalikan hasil dan matriks asli
    # else:
    #     # Jika threshold terlalu tinggi (melebihi jumlah nilai unik)
    #     print("❌ Index thresholdFlowAccumulation melebihi panjang hasil. Perhitungan dibatalkan.")
    #     return [], flow_accum_MDINF

    except Exception as e:
        # Tangani error jika terjadi kesalahan saat proses
        print(f"[ERROR] Gagal impor GeoTIFF: {e}")
