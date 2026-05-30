import os
import modul.config as cfg


def generateFileDEM(latitude, longitude):
    """
    Fungsi untuk membuat nama file DEM berdasarkan latitude dan longitude.
    """
    # Path untuk header


    nama1 = cfg.headerDem

    nama2 = cfg.footerDem

    # Penyesuaian longitude untuk batas -180 hingga 180
    if longitude >= 180:
        longitude = (longitude - 1) * -1
    elif longitude <= -180:
        longitude = (longitude + 1) * -1

    # Format latitude
    numlatitude = int(abs(latitude)) + 1 if latitude < 0 else int(abs(latitude))
    strlatitude = 'S' if latitude < 0 else 'N'
    strnumlatitude = f'{numlatitude:02d}'

    # Format longitude
    numlongitude = int(abs(longitude)) + 1 if longitude < 0 else int(abs(longitude))
    strlongitude = 'W' if longitude < 0 else 'E'
    strnumlongitude = f'{numlongitude:03d}'

    # Gabungkan semua bagian nama file

    filename = os.path.join(cfg.pathMaps, f"{nama1}{strlatitude}{strnumlatitude}{strlongitude}{strnumlongitude}{nama2}")

    return filename


