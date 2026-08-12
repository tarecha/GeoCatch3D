import numpy as np, random

from modul import konverter
from modul import mapping, rationalmethod, watershed as wts, config as cfg

def clear_state(state):
    state.latitude = "-"
    state.longitude = "-"
    state.jaraktitiktengah = "-"
    state.ketinggian = "-"
    state.ketinggianhulu = "-"
    state.height_perpixel_m = "-"
    state.width_perpixel_m = "-"
    state.diagonal_perpixel_m = "-"
    state.area_per_pixel_m2 = "-"
    state.jarakaAliranUtama_km = "-"
    state.FlowAccum = "-"
    state.FlowAccumMDInf = "-"
    state.luasdas = "-"
    state.TC = "-"
    state.I_mm_perjam = "-"
    state.Qp = "-"
    state.alert_message = "-"
    state.alert_show = False
    state.estimasi_url = "#"
    state.deltaelevasi = "-"
    state.deltaelevasioutlet_pointer = "-"
    state.kemiringan = "-"



def make_callback(latitude, longitude, radiusBaris, radiusKolom, barisMatriks, kolomMatriks, state, ketinggiantengah, flow_accum_MDInf, flow_accum_D8, matriktributaryidentifier, matrikKecil,transformasi, plotter,custom_cmapfa1, grid,coneTengah, coneUtara,tingicone,pv,radiuscone, viewer, ctrl):
   #flow_accum_D8_flip = np.flipud(flow_accum_D8.copy())

    countklik =0
    outlet = []
    print(f"countcllik awal {countklik}")
    tampilflowaccum = np.flipud(flow_accum_D8.copy())
    tampilflowaccum = np.where(tampilflowaccum < 0, 0, tampilflowaccum)
    flow_accum_MDInf = np.flipud(flow_accum_MDInf)
    def callback(point, idx):
        #clear key tiap klik
        nonlocal countklik
        countklik +=1
        print(f"countcllik {countklik}")
        clear_state(state)

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
        print(f"barisFA = {barisFA}, kolomFA {kolomFA}")
        latitudePoint, longitudePoint = mapping.MappingBarisKolomMatrikKeLatLong(
            barisKonversi, kolomKonversi, latitude, longitude)
        print(f"call back latitudePoint {latitudePoint} longitudePoint {longitudePoint} ")
        FA = round(flow_accum_MDInf[int(barisFA), int(kolomFA)], 2)
        FAD8 = round(flow_accum_D8[int(barisFA), int(kolomFA)], 2)
        print(f"call back flow_accum_MDInf FA {FA} ")
        print(f"call back flow_accum_D8 FA {FAD8} ")
        state.FlowAccum = str(FAD8)
        state.FlowAccumMDInf  = str(FA)

        luaswateshed, state.area_per_pixel_m2, state.height_perpixel_m, state.width_perpixel_m, state.diagonal_perpixel_m = konverter.cells_to_km2(FA, latitudePoint)
        state.luasdas = round(luaswateshed,4)
        print(f"luasdas sesudah pembulatan= {state.luasdas}")
        state.Qp = rationalmethod.hitungdebit(A=luaswateshed, baris =int(barisFA), kolom=int(kolomFA),flow_accum_D8=flow_accum_D8,matriktributaryidentifier=matriktributaryidentifier,matrikKecil=matrikKecil,state=state, transformasi=transformasi)
        state.jaraktitiktengah = round(konverter.hitungjarak(barisKlik,kolomKlik,latitude),2)
        print(f"jaraktitiktengah {state.jaraktitiktengah}")
        #plot(matrikFAasli, "matrik fa")
        # Set ke state agar bisa ditampilkan di UI
        #state.ketinggiantitiktengah = str(ketinggiantengah)
        # state.latitude = format(latitudePoint, ".8f")
        # state.longitude = format(longitudePoint, ".8f")

        state.latitude = format(latitudePoint, ".6f")
        state.longitude = format(longitudePoint, ".6f")
        state.ketinggian = round(ketinggianKlik,2)
        state.deltaelevasioutlet_pointer = round(ketinggianKlik - ketinggiantengah,2)
        state.estimasi_url = f"{cfg.estimasi_url}B1={state.Qp}&B2={state.TC}"
        state.maps_url = f"{cfg.maps_url}{state.latitude},{state.longitude}"
        state.maps_text = "Link Google Maps"
        print(f"titik tengah : {ketinggiantengah} ")
        print("latitude longitude ketinggian link ketinggiantitiktengah")
        print(state.latitude, state.longitude, state.ketinggian, state.maps_url, state.ketinggiantitiktengah)
        print(f"di call back barisFA {barisFA} dan  kolomFA {kolomFA}")

        nonlocal outlet
        if state.multidas_option and state.mesh_option == "watershedinteractive":
            outlet.append([barisFA, kolomFA, countklik])
        else:
            outlet.clear()
            outlet.append([barisFA, kolomFA, 1])
            # 1. Cari dan kumpulkan semua nama actor yang berawalan "actor_pointer"
            daftar_hapus = [nama for nama in plotter.actors.keys() if nama.startswith('actor_pointer')]

            # 2. Hapus actor tersebut dari plotter satu per satu
            for nama in daftar_hapus:
                plotter.remove_actor(nama)
                print(f"{nama} berhasil dihapus.")

            # (Opsional) Render ulang plotter agar perubahannya langsung terlihat di layar
            plotter.render()

        koordinatpourpoint = np.array(outlet)
        print(f"koordinatpourpoint all")

        if state.mesh_option == "watershedinteractive":
            for row in koordinatpourpoint:
                print(" ".join(str(int(x)) if float(x).is_integer() else str(x) for x in row))
            wts.eksporshpinteraktive(koordinatpourpoint, transformasi, radiusBaris,state)
            print("Actor saat ini:", len(plotter.renderer.actors))
            plotter.clear_actors()
            print("Actor saat ini setelah di remove:", len(plotter.renderer.actors))







            watershed = wts.getFAwatershedinteractive(tampilflowaccum)
            matrikScalar = np.rot90(watershed, k=-1)

            #matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            #plotter.add_mesh(coneTengah, color="red", specular=1.0, show_edges=True, smooth_shading=False,
            #                 pickable=False)
            #plotter.add_mesh(coneUtara, color="magenta", specular=1.0, show_edges=True, smooth_shading=False,
            #                 pickable=False)

            plotter.add_mesh(grid, scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True,
                             pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
           
            plotter.add_mesh(coneTengah, color="red", specular=1.0, show_edges=True, smooth_shading=False,
                             pickable=False)
            plotter.add_mesh(coneUtara, color="magenta", specular=1.0, show_edges=True, smooth_shading=False,
                             pickable=False)

             # merubah orientasi karena pyvista 0,0 di kiri bawah


                #print(f"baris error 2")
        actorid = 0
        daftar_warna = [
            'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'orange', 'lime', 'hotpink', 'dodgerblue', 'gold',
            'springgreen', 'blueviolet', 'crimson'
        ]
        for row in koordinatpourpoint:
            actorid += 1
            barisCone = ((radiusBaris * 2)) - int(row[0])
            kolomCone = row[1]
            px, py = int(kolomCone), int(barisCone)
            pz = matrikKecil[py, px]
            print(f"titik cone baru px {px} py {py} pz {pz}")
            cone = pv.Cone(center=(px, py, pz + tingicone+10), direction=(0, 0, -1), radius=radiuscone*0.8,
                           height=tingicone * 2+20)
            print(f"add actor_pointer{actorid}")


            if actorid == 1 :
                warna_urut = 'orange'
            else:
                indeks_warna = (actorid - 1) % len(daftar_warna)
                warna_urut = daftar_warna[indeks_warna]

            plotter.add_mesh(cone, name=f'actor_pointer{actorid}', color=warna_urut, smooth_shading=False, pickable=False, lighting=False,
                             show_edges=True)
        viewer.update()
        ctrl.view_update()
        print("--- Daftar Actor di Plotter ---")
        # Mencetak semua nama actor yang ada di plotter
        print("Daftar nama actor:", list(plotter.actors.keys()))




        state.flush()
        #print(f"baris error 3")

    return callback
