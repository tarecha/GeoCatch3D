import os
import rasterio
import numpy as np
from rasterio.transform import from_origin
from modul import mapping, config as cfg, analisis

def eksporTIF(matrikOut, latitude, longitude,
              pixelKolomAwalKoordinat, pixelBarisAwalKoordinat,fullPath,
              crs='EPSG:4326' ):
    try:
        # Cek bentuk array
        if matrikOut.ndim != 2:
            raise ValueError("matrikOut harus 2 dimensi")

        latAwal, longAwal = mapping.MappingBarisKolomMatrikKeLatLong(
            pixelBarisAwalKoordinat, pixelKolomAwalKoordinat,
            latitude, longitude
        )
        # print(f"""
        # pixelBarisAwalKoordinat:  {pixelBarisAwalKoordinat}
        # pixelKolomAwalKoordinat:  {pixelKolomAwalKoordinat}
        # latitude               :  {latitude}
        # longitude              :  {longitude}
        #
        # latAwal                :  {latAwal}
        # longAwal               :  {longAwal}
        # """"")

        # Pilih step berdasarkan interval
        step = 1 / 3600

        # print(f"[DEBUG] Step nya: {step}")
        # print(f"[DEBUG] Lat awal: {latAwal}")
        # print(f"[DEBUG] Long awal: {longAwal}")
        # Transformasi spasial
        transform = from_origin(longAwal, latAwal, step, -step)  # catatan: -step agar arah latitude turun
        print(f"transform2 {transform}")
        # Bangun path

        os.makedirs(os.path.dirname(fullPath), exist_ok=True)

        # print(f"[INFO] Menyimpan ke: {fullPath}")
        # print(f"[DEBUG] Shape: {matrikOut.shape}, dtype: {matrikOut.dtype}")
        # print(f"[DEBUG] Transform: {transform}")

        # Simpan GeoTIFF
        with rasterio.open(
            fullPath, 'w',
            driver='GTiff',
            height=matrikOut.shape[0],
            width=matrikOut.shape[1],
            count=1,
            dtype='int16',
            #dtype=matrikOut.dtype,
            crs=crs,
            transform=transform,
            nodata=0,
        ) as dst:
            dst.write(matrikOut, 1)

        # print(f"[SUKSES] GeoTIFF berhasil disimpan ke {fullPath}")


    except Exception as e:
        print(f"[ERROR] Gagal menyimpan GeoTIFF: {e}")

def eksporTIF2(matrikOut,fullPath, transformasi, crs='EPSG:4326' ):
    try:
        # Cek bentuk array
        if matrikOut.ndim != 2:
            raise ValueError("matrikOut harus 2 dimensi")
        minout = np.min(matrikOut)
        print(f"matrikOut.dtype {matrikOut.dtype}, minout {minout}")

        # print(f"""
        # pixelBarisAwalKoordinat:  {pixelBarisAwalKoordinat}
        # pixelKolomAwalKoordinat:  {pixelKolomAwalKoordinat}
        # latitude               :  {latitude}
        # longitude              :  {longitude}
        #
        # latAwal                :  {latAwal}
        # longAwal               :  {longAwal}
        # """"")

        # Pilih step berdasarkan interval

        # Bangun path

        os.makedirs(os.path.dirname(fullPath), exist_ok=True)

        # print(f"[INFO] Menyimpan ke: {fullPath}")
        # print(f"[DEBUG] Shape: {matrikOut.shape}, dtype: {matrikOut.dtype}")
        # print(f"[DEBUG] Transform: {transform}")
        # print(f"di file handle max {np.max(matrikOut)} min {np.min(matrikOut)}")
        # print(f"di file handle dtipe {matrikOut.dtype}")
        # Simpan GeoTIFF
        with rasterio.open(
            fullPath, 'w',
            driver='GTiff',
            height=matrikOut.shape[0],
            width=matrikOut.shape[1],
            count=1,
            dtype='int16',
            #dtype=matrikOut.dtype,
            crs=crs,
            transform=transformasi,
            nodata=0,
        ) as dst:
            dst.write(matrikOut, 1)

        # print(f"[SUKSES] GeoTIFF berhasil disimpan ke {fullPath}")


    except Exception as e:
        print(f"[ERROR] Gagal menyimpan GeoTIFF: {e}")

def eksporTIF3(matrikOut, fullPath, transformasi, cmap_obj, crs='EPSG:4326'):
    try:
        if matrikOut.ndim != 2:
            raise ValueError("matrikOut harus 2 dimensi")

        matrikOut = matrikOut.astype(float)

        mask_nan = np.isnan(matrikOut)

        minout = np.nanmin(matrikOut)
        maxout = np.nanmax(matrikOut)

        print(f"matrikOut.dtype {matrikOut.dtype}, minout {minout}, maxout {maxout}")

        os.makedirs(os.path.dirname(fullPath), exist_ok=True)

        # ---------------- NORMALISASI ---------------- #
        if maxout > minout:
            matrik_norm = (matrikOut - minout) / (maxout - minout)
        else:
            matrik_norm = np.zeros_like(matrikOut, dtype=float)

        matrik_norm = np.clip(matrik_norm, 0, 1)

        # ---------------- COLORMAP ---------------- #
        matrik_warna = cmap_obj(matrik_norm)
        matrik_warna[mask_nan] = [0, 0, 0, 0]

        matrik_rgb = (matrik_warna[:, :, :3] * 255).astype('uint8')

        # ================= TAMBAHAN TITIK MERAH ================= #
        H, W = matrik_rgb.shape[:2]

        cy = H // 2
        cx = W // 2

        radius = int(min(H, W) * 0.01)  # 3%

        # buat grid koordinat
        y, x = np.ogrid[:H, :W]

        # mask lingkaran
        mask_circle = (x - cx)**2 + (y - cy)**2 <= radius**2

        # apply warna merah
        matrik_rgb[mask_circle] = [255, 0, 0]
        # ======================================================== #

        # ---------------- WRITE TIFF ---------------- #
        with rasterio.open(
                fullPath,
                'w',
                driver='GTiff',
                height=H,
                width=W,
                count=3,
                dtype='uint8',
                crs=crs,
                transform=transformasi,
                nodata=None,
        ) as dst:
            dst.write(matrik_rgb[:, :, 0], 1)
            dst.write(matrik_rgb[:, :, 1], 2)
            dst.write(matrik_rgb[:, :, 2], 3)

        print("filehandler 3 oke")

    except Exception as e:
        print(f"[ERROR] Gagal menyimpan GeoTIFF: {e}")