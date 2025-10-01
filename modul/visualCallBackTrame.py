import numpy as np

from modul import konverter
from modul import mapping, rationalmethod


def make_callback(latitude, longitude, radiusBaris, radiusKolom, barisMatriks, kolomMatriks, state, ketinggiantengah, matrikFAasli):
    matrikFAasli = np.flipud(matrikFAasli)
    def callback(point, idx):
        kolomKlik = point[0] - radiusKolom
        barisKlik = point[1] - radiusBaris
        ketinggianKlik = point[2]
        print(f"poin 1 = {point[1] }, poin 0 = {point[0] }")
        print(f"barisKlik = {barisKlik}, kolomKlik {kolomKlik}")

        barisKonversi = barisMatriks - barisKlik
        kolomKonversi = kolomMatriks + kolomKlik
        print(f"callback barisKonversi {barisKonversi} kolomKonversi {kolomKonversi}")
        barisFA  = radiusBaris - barisKlik
        kolomFA  = point[0]
        state.baris = barisFA
        state.kolom = kolomFA
        # print(f"barisFA = {barisFA}, kolomFA {kolomFA}")
        latitudePoint, longitudePoint = mapping.MappingBarisKolomMatrikKeLatLong(
            barisKonversi, kolomKonversi, latitude, longitude)
        print(f"call back latitudePoint {latitudePoint} longitudePoint {longitudePoint} ")
        state.FA = round(matrikFAasli[int(barisFA), int(kolomFA)],2)
        luaswateshed = konverter.cells_to_km2(matrikFAasli[int(barisFA), int(kolomFA)], latitudePoint)
        state.luasdas = round(luaswateshed,4)
        print(f"luasdas sesudah pembulatan= {state.luasdas}")
        state.Qp = rationalmethod.hitungdebit(luaswateshed)
        state.jaraktitiktengah = round(konverter.hitungjarak(barisKlik,kolomKlik,latitude),2)
        print(f"jaraktitiktengah {state.jaraktitiktengah}")
        #plot(matrikFAasli, "matrik fa")
        # Set ke state agar bisa ditampilkan di UI
        state.ketinggiantitiktengah = str(round( ketinggiantengah))
        # state.latitude = format(latitudePoint, ".8f")
        # state.longitude = format(longitudePoint, ".8f")

        state.latitude = format(latitudePoint, ".6f")
        state.longitude = format(longitudePoint, ".6f")
        state.ketinggian = round(ketinggianKlik,None)
        state.maps_url = f"https://www.google.com/maps?q={state.latitude},{state.longitude}"
        print(f"titik tengah : {ketinggiantengah} ")
        print("latitude longitude ketinggian link ketinggiantitiktengah")
        print(state.latitude, state.longitude, state.ketinggian, state.maps_url, state.ketinggiantitiktengah)
        state.flush()
    return callback
