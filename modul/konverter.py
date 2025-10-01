import numpy as np

def cells_to_km_dual(dimensi, latitude_deg):

    res_deg = 1 / 3600
    # 1 derajat lintang = ~111.32 km (konstan)
    deg_lat_km = 111.32
    # 1 derajat bujur = 111.32 × cos(latitude)
    deg_lon_km = deg_lat_km * np.cos(np.radians(latitude_deg))

    panjang_vertikal_km = round(dimensi * res_deg * deg_lat_km, 2)
    panjang_horizontal_km = round(dimensi * res_deg * deg_lon_km, 2)
    luas_km2 = round(panjang_horizontal_km * panjang_vertikal_km,4)
    return luas_km2, panjang_horizontal_km, panjang_vertikal_km

#digunakan bila out_type mdinf FA adalah "cells"
#fungsi ini lebih disukai karena dapat melihat jumlah sel yang berkontribusi
#nilai dari fungsi cells_to_km2 dan deg_to_km2 sama
def cells_to_km2(n_cells, latitude_deg):
    """
    Mengonversi jumlah sel raster EPSG:4326 (derajat) menjadi luas dalam km²,
    dengan menyesuaikan ukuran piksel terhadap lintang (latitude).

    Parameters:
    -----------
    n_cells : int atau array
        Jumlah sel (grid cells).
    latitude_deg : float
        Lintang lokasi dalam derajat.
    res_deg : float
        Resolusi raster dalam derajat (default 1 arcsecond = 1/3600 deg).

    Returns:
    --------
    luas_km2 : float atau array
        Total luas area dalam kilometer persegi.
    """
    res_deg = 1 / 3600
    # Panjang 1 derajat lintang dalam meter
    deg_lat_m = 111_320
    # Panjang 1 derajat bujur tergantung lintang
    deg_lon_m = deg_lat_m * np.cos(np.radians(latitude_deg))

    # Ukuran piksel dalam meter
    pixel_height_m = res_deg * deg_lat_m
    pixel_width_m  = res_deg * deg_lon_m

    # Luas 1 piksel dalam m²
    area_per_pixel_m2 = pixel_height_m * pixel_width_m

    # Luas total dalam km²
    luas_km2 = round((n_cells * area_per_pixel_m2) / 1_000_000,4)
    return luas_km2

#digunakan bila out_type mdinf FA adalah "ca"
def deg2_to_km2(area_deg2, latitude_deg):
    """
    Mengonversi luas area dari derajat kuadrat (°²) ke kilometer persegi (km²),
    dengan memperhitungkan pengaruh lintang (latitude) terhadap ukuran bujur.

    Parameters:
    -----------
    area_deg2 : float atau array
        Luas area dalam derajat kuadrat (°²), biasanya hasil dari flow accumulation.
    latitude_deg : float
        Lintang lokasi area tersebut (dalam derajat).

    Returns:
    --------
    area_km2 : float atau array
        Luas area dalam kilometer persegi (km²).
    """
    # Panjang 1 derajat lintang dalam meter
    deg_lat_m = 111_320  # meter (rata-rata)
    # Panjang 1 derajat bujur tergantung lintang
    deg_lon_m = deg_lat_m * np.cos(np.radians(latitude_deg))

    # Luas 1° × 1° dalam meter persegi di lintang tersebut
    area_per_deg2_m2 = deg_lat_m * deg_lon_m

    # Konversi ke km²
    area_km2 = (area_deg2 * area_per_deg2_m2) / 1_000_000
    return area_km2

def hitungjarak(baris, kolom, latitude_deg):
    """

    """

    jarakselbaris = abs(baris)
    jarakselkolom = abs(kolom)
    res_deg = 1 / 3600
    # 1 derajat lintang = ~111.32 km (konstan)
    deg_lat_km = 111.32
    # 1 derajat bujur = 111.32 × cos(latitude)
    deg_lon_km = deg_lat_km * np.cos(np.radians(latitude_deg))

    panjang_vertikal_km = jarakselbaris * res_deg * deg_lat_km
    panjang_horizontal_km = jarakselkolom * res_deg * deg_lon_km
    jarakselkm = np.sqrt((panjang_horizontal_km) ** 2 + (panjang_vertikal_km) ** 2)

    return jarakselkm