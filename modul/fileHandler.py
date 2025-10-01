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
            dtype=matrikOut.dtype,
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
            dtype=matrikOut.dtype,
            crs=crs,
            transform=transformasi,
            nodata=0,
        ) as dst:
            dst.write(matrikOut, 1)

        # print(f"[SUKSES] GeoTIFF berhasil disimpan ke {fullPath}")


    except Exception as e:
        print(f"[ERROR] Gagal menyimpan GeoTIFF: {e}")

