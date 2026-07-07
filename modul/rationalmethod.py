from modul import config as cfg, plotter as plt, fileHandler
from whitebox.whitebox_tools import WhiteboxTools
import numpy as np
import math

temp_dir = cfg.pathTempMaps
# Inisialisasi alat WhiteboxTools
wbt = WhiteboxTools()
wbt.set_working_dir(temp_dir)  # Set direktori kerja

def hitungdebit(A, baris, kolom,flow_accum_D8,matriktributaryidentifier,matrikKecil,state,transformasi):
    print(f"koefisien di fungsi {cfg.koefisien}")
    print(f"curah hujan di fungsi {cfg.curahhujan}")

    tc = hitungtimeconcentration(baris, kolom,flow_accum_D8,matriktributaryidentifier,matrikKecil,state,transformasi)
    print(f"time concentration {tc}")
    state.TC = tc
    if tc >= cfg.threshodwaktuTC_jam:
        I = intensitasMonobe_r24(cfg.curahhujan, tc)
        state.I_mm_perjam = I
        print(f"I_mm_per_hour {I}")
        Qp = round(0.278 * float(cfg.koefisien) * I * A, 2)
        return Qp
    else:
        state.alert_message = f"---Debit tidak dapat dihitung karena dibawah threshold waktu TC realistis {cfg.threshodwaktuTC_jam} jam, coba pilih aliran lain atau naikkan radius analisis---"
        state.alert_show = True
        return  f"---Debit tidak dapat dihitung karena dibawah threshold waktu TC realistis {cfg.threshodwaktuTC_jam} jam, coba pilih aliran lain atau naikkan radius analisis---"


def hitungtimeconcentration(barishilir, kolomhilir, flow_accum_D8, matriktributaryidentifier,matrikKecil,state,trasnformasi):
    matrikKecil = np.flipud(matrikKecil)
    #metode kirpich
    #


    tributaryid = matriktributaryidentifier[barishilir,kolomhilir]
    thresholdFAtitik = flow_accum_D8[barishilir,kolomhilir]
    #cari jalur aliran air berdasarkan tributaryid dari barishilir dan kolomhilir / ketika klik kanan di area visualisasi
    mask = (matriktributaryidentifier==tributaryid) & (matriktributaryidentifier>0) &  (flow_accum_D8<=thresholdFAtitik)
    jumlahselstreamutama = np.count_nonzero(mask)
    # ----------------------------------------------------------------------------------
    #mencari titik hulu dari jalur mask yang memiliki flow accumulaion terkecil

    streamUtama = np.argwhere(mask == 1)
    min_val = np.inf
    barishulu = None
    kolomhulu = None

    for r, c in streamUtama:
        nilai = flow_accum_D8[r, c]

        if nilai < min_val:
            min_val = nilai
            barishulu = r
            kolomhulu = c
    # ----------------------------------------------------------------------------------

    #
    # plt.plot_file(file=cfg.filetributaryidentifier,judul="tributaryidentifier", z="id")
    maskelevasi = np.ma.masked_where(~mask, matrikKecil)
    maskeFA= np.ma.masked_where(~mask, flow_accum_D8)
    #plt.plot_file(file=cfg.fileFlowAccumulationBreachD8, judul="fileFlowAccumulationBreachD8", z="upstream cell")
    if cfg.demomode:
        plt.plot(matrikplot=mask, judul="Panjang aliran utama", z="")
    #plt.plot(matrikplot=maskelevasi, judul="Mask panjang aliran utama", z="threshold")
    fileHandler.eksporTIF2(maskeFA,cfg.filemaskFAhilirhulu, trasnformasi,cfg.default_crs)
    if barishulu==None and kolomhulu == None:

        elevasiHilir = round(matrikKecil[barishilir, kolomhilir], 2)
        elevasiHulu = elevasiHilir
        state.ketinggianhulu = elevasiHulu
    else:
        elevasiHulu = round(matrikKecil[barishulu,kolomhulu],2)
        elevasiHilir = round(matrikKecil[barishilir,kolomhilir],2)
        state.ketinggianhulu = elevasiHulu


    print(f"elevasiHulu : {elevasiHulu} - elevasiHilir : {elevasiHilir}")
    print(
        f"tributary id: {tributaryid}\n"
        f"baris hulu: {barishulu}\n"
        f"kolom hulu: {kolomhulu}\n"
        f"elevasi hulu: {elevasiHulu}\n"
        f"baris hilir: {barishilir}\n"
        f"kolom hilir: {kolomhilir}\n"
         f"elevasi hilir: {elevasiHilir}\n"
        f"jumlah sel stream utama: {jumlahselstreamutama}"
    )

    tinggi1sel = state.height_perpixel_m
    lebar1sel = state.width_perpixel_m
    diagonal1sel = state.diagonal_perpixel_m
    print(f"tinggi1sel {tinggi1sel}, lebar1sel {lebar1sel}, diagonal1sel {diagonal1sel}")

    perhitungansel = count_adjacent_pairs(mask)
    print(f"jumlah sel stream utama: {jumlahselstreamutama}")
    print(f"interval horizontal {perhitungansel["intervalhorizontal"] }")
    print(f"interval vertikal  {perhitungansel["intervalvertikal"]}")
    print(f"interval diagonal {perhitungansel["intervaldiagonal"]}")
    print(f"total jarak interval {perhitungansel["intervalhorizontal"] +perhitungansel["intervalvertikal"]+perhitungansel["intervaldiagonal"]}")
    


    jarakintervalhorizontal = round(perhitungansel["intervalhorizontal"] * lebar1sel,2)
    jarakintervalvertikal= round(perhitungansel["intervalvertikal"] * tinggi1sel,2)
    jarakintervaldiagonal = round(perhitungansel["intervaldiagonal"] * diagonal1sel,2)




    print(f"jarakselhorizontal {jarakintervalhorizontal}")
    print(f"jarakselvertikal {jarakintervalvertikal}")
    print(f"jarakseldiagonal {jarakintervaldiagonal}")

    jarakintervaltotal_m = jarakintervalhorizontal + jarakintervalvertikal + jarakintervaldiagonal
    state.jarakaAliranUtama_km = round(jarakintervaltotal_m / 1000,2)

    if jarakintervaltotal_m > 0:
        tc = kirpich_tc_from_intervals(jarakintervaltotal_m, elevasiHulu, elevasiHilir)
        tc_hour = tc["Tc_hours"]
        state.kemiringan = round(tc["slope_S"],4)
        state.deltaelevasi = round(tc["delta_h_m"],4)
        return round(tc_hour,2)
    else:
        return 0


def count_adjacent_pairs(mask):
    """
    Hitung pasangan tetangga sekali saja, tetapi untuk diagonal
    kita abaikan pasangan diagonal yang "redundan" ketika
    orthogonal neighbour di antaranya sudah ada (L-shape).
    Returns dict with counts.
    """
    M = np.asarray(mask).astype(bool)
    H, W = M.shape

    def shift(a, dr, dc):
        res = np.zeros_like(a, dtype=bool)
        if dr >= 0:
            rsrc = slice(0, H-dr); rdst = slice(dr, H)
        else:
            rsrc = slice(-dr, H); rdst = slice(0, H+dr)
        if dc >= 0:
            csrc = slice(0, W-dc); cdst = slice(dc, W)
        else:
            csrc = slice(-dc, W); cdst = slice(0, W+dc)
        res[rdst, cdst] = a[rsrc, csrc]
        return res

    # dasar shifts
    right  = shift(M, 0, 1)   # pasangan (r,c) & (r,c+1)
    down   = shift(M, 1, 0)   # pasangan (r,c) & (r+1,c)
    dright = shift(M, 1, 1)   # pasangan (r,c) & (r+1,c+1)
    dleft  = shift(M, 1, -1)  # pasangan (r,c) & (r+1,c-1)
    left   = shift(M, 0, -1)  # pasangan (r,c) & (r,c-1)

    # pasangan orthogonal (tetap)
    cnt_right = int(np.count_nonzero(M & right))
    cnt_down  = int(np.count_nonzero(M & down))

    # kandidat diagonal (base cell at r,c has diagonal mate at r+1,c+1 or r+1,c-1)
    dright_cand = M & dright
    dleft_cand  = M & dleft

    # exclude dright where there is an orthogonal neighbour bridging the corner
    # i.e. if right[r,c] or down[r,c] True then diagonal (r,c)-(r+1,c+1) is redundant
    dright_filtered = dright_cand & ~(right | down)

    # exclude dleft where left[r,c] or down[r,c] True
    dleft_filtered  = dleft_cand  & ~(left  | down)

    cnt_dright = int(np.count_nonzero(dright_filtered))
    cnt_dleft  = int(np.count_nonzero(dleft_filtered))

    intervalhorizontal = cnt_right
    intervalvertikal = cnt_down
    intervaldiagonal = cnt_dright + cnt_dleft

    return {
        'intervalhorizontal': intervalhorizontal,
        'intervalvertikal' : intervalvertikal,
        'intervaldiagonal' : intervaldiagonal,
        'pairs_per_direction': {
            'right': cnt_right,
            'down' : cnt_down,
            'down_right': cnt_dright,
            'down_left' : cnt_dleft
        }
    }



def kirpich_tc_from_intervals(jarakintervaltotal, elevasiHulu, elevasiHilir):
    """
    Hitung waktu konsentrasi (Kirpich) dari:
      - jarakintervaltotal: bisa berupa total jarak (meter) ATAU jumlah interval/sel (integer)
      - elevasiHulu, elevasiHilir: elevasi hulu dan hilir (meter)
      - cell_size: jika diberikan, jarakintervaltotal dianggap sebagai jumlah sel -> L = jarakintervaltotal * cell_size
    Returns dict { 'L_m', 'delta_h', 'slope', 'Tc_min', 'Tc_sec' }
    """

    constant = 0.0195


    L_m = float(jarakintervaltotal)


    # beda elevasi
    delta_h = float(elevasiHulu) - float(elevasiHilir)

    # Validasi input dasar
    # if L_m <= 0:
    #     raise ValueError("Panjang L harus > 0 (periksa jarakintervaltotal / cell_size).")
    # if delta_h <= 0:
    #     raise ValueError("Delta elevasi (elevasiHulu - elevasiHilir) harus > 0.")

    # kemiringan rata-rata S (m/m)
    S = delta_h / L_m


    # rumus Kirpich (hasil dalam menit)
    Tc_min = constant * (L_m ** 0.77) * (S ** -0.385)
    Tc_sec = Tc_min * 60.0
    Tc_hour = Tc_min / 60.0

    return {
        'L_m': L_m,
        'delta_h_m': delta_h,
        'slope_S': S,
        'Tc_minutes': Tc_min,
        'Tc_seconds': Tc_sec,
        'Tc_hours' : Tc_hour
    }


def intensitasMonobe_r24(R24_mm, Tc_hours):
    """

    Hitung intensitas hujan (I, mm/jam) berdasarkan rumus:
        I = (R24 / 24) * (24 / Tc)

    Args:
        R24_mm (float): curah hujan 24 jam (mm)
        Tc_hours (float): waktu konsentrasi (jam)

    Returns:
        dict: {
            'R24_mm': float,     # curah hujan 24 jam (mm)
            'Tc_hours': float,   # waktu konsentrasi (jam)
            'I_mm_per_hour': float  # intensitas hujan (mm/jam)
        }
    """
    if R24_mm <= 0:
        raise ValueError("R24_mm harus > 0 (curah hujan 24 jam dalam mm).")
    if Tc_hours <= 0:
        raise ValueError("Tc_hours harus > 0 (waktu konsentrasi dalam jam).")

    I =  (R24_mm / 24.0) * ((24.0 / Tc_hours) ** (2.0/3.0))
    print(f"tipe data I/jam {type(I)}")
    return round(I,2)

# ===== Contoh penggunaan =====
# R24 = 100.0   # mm
# Tc = 2.5      # jam
# hasil = intensitas_r24(R24, Tc)
# print(f"Intensitas hujan (I) = {hasil['I_mm_per_hour']:.2f} mm/jam")

