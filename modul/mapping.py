
def MappingLatLongkeBarisKolom(latitude, longitude):
    """
    Fungsi untuk menyamakan koordinat bumi dan posisi matriks.
    Mengonversi latitude dan longitude menjadi baris dan kolom seperti pada script MATLAB.
    """
    print(latitude, longitude)
    # Hitung baris (latitude)
    if latitude >= 0:
        latitude = abs(latitude)
        baris_batas_bawah = int(latitude)
        baris_belakang_koma = latitude - baris_batas_bawah
        baris_koma = (baris_belakang_koma * 3600)
        baris_koma = 3600 - baris_koma
    else:
        latitude = abs(latitude)
        baris_batas_bawah = int(latitude)
        baris_belakang_koma = latitude - baris_batas_bawah
        baris_koma = (baris_belakang_koma * 3600)



    #Hitung kolom (longitude)
    if longitude >= 0:
        longitude = abs(longitude)
        kolom_batas_bawah = int(longitude)
        kolom_belakang_koma = longitude - kolom_batas_bawah
        kolom_koma = (kolom_belakang_koma * 3600)
    else:
        longitude = abs(longitude)
        kolom_batas_bawah = int(longitude)
        kolom_belakang_koma = longitude - kolom_batas_bawah
        kolom_koma = (kolom_belakang_koma * 3600)
        kolom_koma = 3600 - kolom_koma
    return baris_koma, kolom_koma




# def MappingBarisKolomPyvistaKeLatLong(barisMatriks, kolomMatriks, latitude, longitude,interval):
#     if interval == 30:
#         archsecond = 3600
#         step = 1/archsecond
#
#     else:
#         archsecond = 7200
#         step = 1 / archsecond
#
#     print(f"MappingBarisKolomPyvistaKeLatLong barisMatriks: {barisMatriks},kolomMatriks: {kolomMatriks},latitude: {latitude}, longitude: {longitude}")
#     # 1 arch second = 3601 titik
#     if latitude >= 0:
#         latitudeKoma = step * barisMatriks
#         latitudetanpaKoma = int(abs(latitude))
#         latitudePoint = round(latitudetanpaKoma + latitudeKoma, 4)
#     else:
#         latitudeKoma = step * (3600 - barisMatriks)
#         latitudetanpaKoma = int(abs(latitude)) * -1
#         latitudePoint = round(latitudetanpaKoma - latitudeKoma, 4)
#
#
#     if longitude >= 0:
#         longitudeKoma = step * kolomMatriks
#         longitudetanpaKoma = int(abs(longitude))
#         longitudePoint = round(longitudetanpaKoma + longitudeKoma, 4)
#     else:
#         longitudeKoma = step * (3600 - kolomMatriks)
#         longitudetanpaKoma = int(abs(longitude)) * -1
#         longitudePoint = round(longitudetanpaKoma - longitudeKoma, 4)
#     print(f"MappingBarisKolomPyvistaKeLatLong latitudePoint: {latitudePoint}, longitudePoint: {longitudePoint}")
#
#     return latitudePoint,longitudePoint


def MappingBarisKolomMatrikKeLatLong(barisMatriks, kolomMatriks, latitude, longitude):
    archsecond = 3600
    step = 1 / archsecond


    #print(f"MappingBarisKolomMatrixKeLatLong barisMatriks: {barisMatriks},kolomMatriks: {kolomMatriks},latitude: {latitude}, longitude: {longitude}")

    if latitude >= 0:
        latitudeKoma = step * barisMatriks
        latitudetanpaKoma = int(abs(latitude))
        latitudePoint = round(latitudetanpaKoma + latitudeKoma, 6)
    else:
        latitudeKoma = step * barisMatriks
        latitudetanpaKoma = int(abs(latitude)) * -1
        latitudePoint = round(latitudetanpaKoma - latitudeKoma, 6)

    if longitude >= 0:
        longitudeKoma = step * kolomMatriks
        longitudetanpaKoma = int(abs(longitude))
        longitudePoint = round(longitudetanpaKoma + longitudeKoma, 6)
    else:
        longitudeKoma = step * (archsecond - kolomMatriks)
        longitudetanpaKoma = int(abs(longitude)) * -1
        longitudePoint = round(longitudetanpaKoma - longitudeKoma, 6)
    #print(f"MappingBarisKolomMatrixKeLatLong latitudePoint: {latitudePoint}, longitudePoint: {longitudePoint}")

    return latitudePoint, longitudePoint




