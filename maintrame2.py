# maintrame_trame.py (versi lengkap siap copy-paste dengan GUI radio button dan penyimpanan screenshot)

import numpy as np
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import re
import time

import matplotlib.colors as mcolors
# Modul lokal
import modul.config as cfg
from modul import mapping, seleksiRHD, pilih, visualCallBackTrame, fileHandler, analisis, watershed as wts

# Trame (UI Web)
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from pyvista.trame.ui import plotter_ui
from trame.widgets import html, vuetify


blue_red = LinearSegmentedColormap.from_list('blue_red', ['blue' ,'yellow','red'])
# 2. Sampling jadi 64 warna (RGBA)
cmapfa = blue_red(np.linspace(0, 1, 32))  # bentuk: (64, 4)
# 3. Modifikasi warna pertama (misalnya jadi putih)
cmapfa[0] = [1, 1, 1, 1]  # R, G, B, A → putih solid
# 4. Buat colormap baru dari array warna
custom_cmapfa1 = LinearSegmentedColormap.from_list('custom_cmapfa1', cmapfa)

# Konfigurasi Trame Server
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller
state.items_list = [
    {"text": "Pertanian - campuran pasir (0.20)", "value": "0.20"},
    {"text": "Pertanian - geluh (0.40)", "value": "0.40"},
    {"text": "Pertanian - lempung (0.50)", "value": "0.50"},
    {"text": "Padang rumput - campuran pasir (0.15)", "value": "0.15"},
    {"text": "Padang rumput - geluh (0.35)", "value": "0.35"},
    {"text": "Padang rumput - lempung (0.45)", "value": "0.45"},
    {"text": "Hutan - campuran pasir (0.10)", "value": "0.10"},
    {"text": "Hutan - geluh (0.30)", "value": "0.30"},
    {"text": "Hutan - lempung (0.40)", "value": "0.4"},
    {"text": "User defined", "value": "user_defined"}
]
state.rainfall= [
    {"text": "Ponorogo 5 mm/jam", "value": "5"},
    {"text": "Malang 8 mm/jam", "value": "8"},
    {"text": "User defined", "value": "user_defined"}
]

ctrl.rainfall = None
ctrl.selected_option = None
#state.selected_option = []
#state.custom_option_input = []
state.curahhujan ="-"
state.koefisien = "-"
state.latitude_input = "-7.942544012073396" #bedengan
state.longitude_input = "112.54059325964216"
state.user_defined_input =""
state.user_defined_rainfall_input =""
state.latitude_input = "-8.311132" #lapangan terbang grati
state.longitude_input = "112.499991"
state.radius_input = str(cfg.radius)
state.latitude = "-"
state.longitude = "-"
state.ketinggian = "-"
state.maps_url = "Google Maps : klik kanan dahulu pada area visualisasi"
state.loading = False
state.alert_message = ""
state.alert_show = False
state.mesh_option = "flow"
state.ketinggiantitiktengah = "-"
state.luasdas = "-"
state.Qp = "-"
state.FA = "-"
state.luasanalisis ="-"
state.panjanghorizontal ="-"
state.panjangvertikal = "-"
state.jaraktitiktengah= "-"
state.jumlahoutlet = "-"
state.layout__title = "Geospatial Hydrological Analysis by Mochamad Agung Tarecha"
state.trame__title = "Geospatial Hydrological Analysis by Mochamad Agung Tarecha"
state.elevasimin = "-"
state.elevasimax = "-"

plotter = pv.Plotter(off_screen=True)
plotter.lighting = 'None'
plotter.set_scale(1, 1, 0.03333333)
# plotter.set_background("white")  # atau "gray"
# plotter.enable_lightkit()
viewer = None
@ctrl.add("view_update")
def view_update():
    # kosong, hanya untuk trigger remote viewer
    pass
def reset_plotter():
    plotter.clear()
    plotter.remove_actor("*")
    plotter.renderer.RemoveAllViewProps()
    plotter.set_scale(1, 1, 0.033333)
    if viewer:
        plotter.reset_camera()
        viewer.update()
        ctrl.view_update()
    print("Actor saat ini:", len(plotter.renderer.actors))
    print("Renderer props setelah clear:", len(plotter.renderer._actors))
    plotter.reset_camera()


@ctrl.add("run_analysis")
def run_analysis():
    global plotter, viewer

    if not viewer:
        print("❗ Viewer belum siap. Analisis dibatalkan.")
        return
    reset_plotter()
    try:
        lat_str = state.latitude_input.strip()
        lon_str = state.longitude_input.strip()
        rad_str = state.radius_input.strip()
        c_str = state.user_defined_input.strip()
        rainfall_str = state.user_defined_rainfall_input.strip()

        if not re.match(r"^-?\d+(\.\d+)?$", lat_str):
            raise ValueError("Latitude harus berupa angka desimal.")
        if not re.match(r"^-?\d+(\.\d+)?$", lon_str):
            raise ValueError("Longitude harus berupa angka desimal.")
        if not rad_str.isdigit():
            raise ValueError("Radius harus berupa bilangan bulat positif.")
        if state.selected_option == None:
            raise ValueError("Pilih koefisien")
        if (state.selected_option == "user_defined") & (c_str == ""):
            raise ValueError("Isi koefisien manual")
        if state.selected_option_rainfall == None:
            raise ValueError("Pilih curah hujan")

        print(f"rainfall_str {rainfall_str} state.rainfall {state.selected_option_rainfall}")
        if (state.selected_option_rainfall == "user_defined") & ((rainfall_str == "") or not (rainfall_str.isdigit())):
            raise ValueError("Curah hujan harus berupa bilangan bulat positif.")

        if c_str != "":
            if float(c_str) < 0 or float(c_str) > 1:
                raise ValueError("Koefisien harus pecahan 0 < C <= 1")
            cfg.koefisien = float(c_str)
        elif (state.selected_option != "user_defined"):
            cfg.koefisien = float(state.selected_option)
        print(f"koefisien di selek {cfg.koefisien}")
        state.koefisien = cfg.koefisien

        if rainfall_str != "":
            cfg.curahhujan = float(rainfall_str)
        elif (state.selected_option != "user_defined"):
            cfg.curahhujan = float(state.selected_option_rainfall)
        print(f"curah hujan  di selek {cfg.curahhujan}")
        state.curahhujan = cfg.curahhujan

        lat = float(lat_str)
        lon = float(lon_str)
        rad = int(rad_str)

        state.loading = True
        state.alert_show = False

        cfg.thresholdFlowAccumulation = (rad - 1) // 5
        print(f"thresholdFlowAccumulation: {cfg.thresholdFlowAccumulation}")
        radiusBaris = rad
        radiusKolom = rad
        ukuran_baris = radiusBaris * 2 + 1
        ukuran_kolom = radiusKolom * 2 + 1

        barisKoma, kolomKoma = mapping.MappingLatLongkeBarisKolom(lat, lon)
        barisMatriks, kolomMatriks = seleksiRHD.seleksiRHD(barisKoma, kolomKoma)
        matrikBesar, baris, kolom = pilih.pilih(barisMatriks, kolomMatriks, lat, lon)
        pixelBarisAwal = baris - radiusBaris
        pixelKolomAwal = kolom - radiusKolom

        matrikKecil = np.zeros((ukuran_baris, ukuran_kolom), dtype=np.float32)
        for i in range(ukuran_baris):
            for j in range(ukuran_kolom):
                matrikKecil[i, j] = matrikBesar[i + pixelBarisAwal, j + pixelKolomAwal]

        pixelBarisAwalKoordinat = barisMatriks - radiusBaris
        pixelKolomAwalKoordinat = kolomMatriks - radiusKolom
        print(f"pixelBarisAwalKoordinat {pixelBarisAwalKoordinat}")
        fileHandler.eksporTIF(matrikKecil, lat, lon, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat, cfg.fileSeleksiDEM, cfg.default_crs)
        matrikKecil = analisis.breachdepression()
        matrikKecil = np.flipud(matrikKecil)

        kolomUtara = radiusKolom
        barisUtara = radiusBaris * 2
        kolomTengah = radiusKolom
        barisTengah = radiusBaris

        x = np.arange(0, ukuran_kolom, dtype=np.float32)
        y = np.arange(0, ukuran_baris, dtype=np.float32)
        X, Y = np.meshgrid(x, y)
        grid = pv.StructuredGrid(X.copy(), Y.copy(), matrikKecil.copy())

        terrain_colors = plt.get_cmap("terrain")(np.linspace(0, 1, 256))
        zmin = np.min(matrikKecil)
        zmax = np.max(matrikKecil)
        state.elevasimin = int(zmin)
        state.elevasimax = int(zmax)
        if zmin == 0:
            terrain_colors[0] = [1, 1, 1, 1]
        custom_terrain = LinearSegmentedColormap.from_list("custom_terrain", terrain_colors)


        ketinggianTengah = matrikKecil[barisTengah, kolomTengah]
        state.ketinggiantitiktengah = float(ketinggianTengah)
        ketinggianUtara = matrikKecil[barisUtara - 1, kolomUtara]
        tingicone = max(rad * 0.5, 3)  # tinggi minimal 3 unit (agar tetap terlihat)
        radiuscone = tingicone * 0.05  # radius = 10% dari tinggi (proporsional)

        # Penempatan z: letakkan cone agar base-nya menempel terrain
        zConeTengah = ketinggianTengah + tingicone / 2
        zConeUtara = ketinggianUtara + tingicone / 2
        print(f"tingicone {tingicone}, radiuscone {radiuscone}")

        coneTengah = pv.Cone(center=(kolomTengah, barisTengah, zConeTengah), radius=radiuscone, height=tingicone, direction=(0, 0, 1))
        coneUtara = pv.Cone(center=(kolomUtara, barisUtara - 1, zConeUtara), radius=radiuscone, height=tingicone, direction=(0, 0, 1))
        plotter.add_mesh(coneTengah, color="red", specular=1.0, show_edges=True, smooth_shading=False,pickable=False)
        plotter.add_mesh(coneUtara, color="magenta", specular=1.0, show_edges=True, smooth_shading=False,pickable=False)
        meshoption = state.mesh_option
        print(f"meshoption {meshoption}")
        koordinatCekungan, matrikFAasli = analisis.importFlowAccumulation(matrikKecil.copy(), ketinggianTengah, lat, rad,meshoption, state)

        callback = visualCallBackTrame.make_callback(lat, lon, radiusBaris, radiusKolom, barisMatriks, kolomMatriks,
                                                     state,ketinggianTengah,matrikFAasli)
        plotter.disable_picking()
        plotter.enable_point_picking(callback=callback, use_picker=True, show_point=True, color="red", point_size=25,
                                     show_message=False)

       #fileHandler.eksporTIF(matrikFAthresholdketinggian, lat, lon, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat,  cfg.fileFlowAccumulationBreachThresholdKetinggian,cfg.default_crs)

        for row in koordinatCekungan:
            px, py = int(row[1]), int(row[0])
            pz = matrikKecil[py, px]
            cone = pv.Cone(center=(px, py, pz + tingicone), direction=(0, 0, -1), radius=radiuscone/6, height=tingicone*2)
            plotter.add_mesh(cone, color='cyan', smooth_shading=False,pickable=False, lighting=False,show_edges=False)
            time.sleep(0.05)



        if state.mesh_option == "flow":
            plotter.add_mesh(grid.copy(), scalars=np.flipud(np.rot90(matrikFAasli, k=1)), cmap=custom_cmapfa1, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "watershed":
            watershed=wts.getwatershed()
            plotter.add_mesh(grid.copy(), scalars=np.rot90(watershed, k=-1), cmap=custom_cmapfa1, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False,  lighting=False)
        elif state.mesh_option == "FAwatershed":
            watershed = wts.getFAwatershed(matrikFAasli)
            plotter.add_mesh(grid.copy(), scalars=np.rot90(watershed, k=-1), cmap=custom_cmapfa1, show_edges=True,
                             pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        else :
            plotter.add_mesh(grid.elevation().copy(), cmap=custom_terrain, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        plotter.reset_camera()
        viewer.update()
        if viewer:
            plotter.reset_camera()
            viewer.update()
            plotter.set_scale(1, 1, 0.033333)
            # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # screenshot_path = os.path.join(os.getcwd(), f"visualisasi_{timestamp}.png")
            # plotter.screenshot(screenshot_path)
            print(f"✅ Viewer update selesai. Siap di render")
        plotter.reset_camera()
        state.alert_message = "✅ Analisis berhasil dirender ulang "
        state.alert_show = True
        print("Lighting mode:", plotter.lighting)
        print("Actor saat ini:", len(plotter.renderer.actors))
    except Exception as e:
        state.alert_message = f"❌ Gagal: {str(e)}"
        state.alert_show = True
    finally:
        state.loading = False

with SinglePageLayout(server, toolbar=True, footer=False) as layout:
    with layout.content:
        with vuetify.VContainer(fluid=True):
            with vuetify.VRow():
                with vuetify.VCol(cols=9, style="height: 100vh;"):
                    viewer = plotter_ui(plotter, height="100%", return_viewer=True, interactive=True)
                with vuetify.VCol(cols=3):
                    with vuetify.VCard(class_="mb-3"):
                        vuetify.VCardTitle("Input Parameter")
                        vuetify.VTextField(v_model="latitude_input", label="Latitude", outlined=True, dense=True, hide_details=True, class_="mb-3",style="margin-bottom: 10px;")

                        vuetify.VTextField(v_model="longitude_input", label="Longitude", outlined=True, dense=True, hide_details=True, class_="mb-3",style="margin-bottom: 10px;")

                        vuetify.VTextField(v_model="radius_input", label="Radius (interval approx 30m)", type="number", outlined=True, dense=True, hide_details=True, class_="mb-3",style="margin-bottom: 10px;")

                        vuetify.VSelect(
                            # 2) v_model sebagai tuple (nama, default)
                            v_model=("selected_option", None),
                            # 3) items juga tuple (nama, default)
                            items=("items_list", ctrl.items_list),
                            item_text="text",  # tampilkan field `text`
                            item_value="value",  # gunakan field `value` sebagai v-model
                            label="Pilih Koefisien C SNI 2415:2016 ",
                            outlined=True,
                            dense=True,
                            style="margin-bottom: 5px;",
                            no_data_text="No data available",
                        )

                        # --- Tambahkan VTextField di bawahnya ---
                        vuetify.VTextField(
                            v_model="user_defined_input",  # v-model baru untuk menyimpan input manual
                            label="Masukkan Koefisien C manual",
                            outlined=True,
                            dense=True,
                            style="margin-bottom: 5px;",
                            # INI KUNCINYA: tampilkan hanya jika 'selected_option' adalah 'user_defined'
                            v_show="selected_option === 'user_defined'",
                        )

                        vuetify.VSelect(
                            # 2) v_model sebagai tuple (nama, default)
                            v_model=("selected_option_rainfall", None),
                            # 3) items juga tuple (nama, default)
                            items=("rainfall", ctrl.rainfall),
                            item_text="text",  # tampilkan field `text`
                            item_value="value",  # gunakan field `value` sebagai v-model
                            label="Pilih Curah Hujan (mm/jam)",
                            outlined=True,
                            dense=True,
                            style="margin-bottom: 5px;",
                            no_data_text="No data available",
                        )

                        # --- Tambahkan VTextField di bawahnya ---
                        vuetify.VTextField(
                            v_model="user_defined_rainfall_input",  # v-model baru untuk menyimpan input manual
                            label="Masukkan curah hujan manual (mm/jam)",
                            outlined=True,
                            dense=True,
                            style="margin-bottom: 5px;",
                            # INI KUNCINYA: tampilkan hanya jika 'selected_option' adalah 'user_defined'
                            v_show="selected_option_rainfall === 'user_defined'",
                        )


                        #cfg.koefisien = state.selected_option
                        # TextField yang hanya tampil jika opsi 'user_defined' dipilih

                        vuetify.VCardTitle("Display Mode")
                        with vuetify.VRadioGroup(v_model="mesh_option", class_="mb-3"):
                            vuetify.VRadio(label="Flow Accumulation (FA)", value="flow")
                            vuetify.VRadio(label="Watershed", value="watershed")
                            vuetify.VRadio(label="FA + Watershed", value="FAwatershed")
                            vuetify.VRadio(label="Terrain Elevation", value="terrain")
                        vuetify.VBtn("Analysys", color="primary", click=ctrl.run_analysis)
                        vuetify.VProgressLinear(indeterminate=True, v_show="loading", color="deep-purple", class_="mt-3")
                        vuetify.VAlert(type="info", v_model="alert_show", v_text="alert_message", class_="mt-3")

                    with vuetify.VCard():
                        vuetify.VCardTitle("Informasi Titik")
                        html.Div("Informasi tampil pada rendering mode 'remote'")
                        html.Div("Elevasi Min: {{ elevasimin }} meter")
                        html.Div("Elevasi Titik Tengah: {{ ketinggiantitiktengah }} meter")
                        html.Div("Elevasi Max: {{ elevasimax }} meter")
                        html.Div("Luas analisis: {{ luasanalisis }} km2")
                        html.Div("Panjang horizontal: {{ panjanghorizontal }} km")
                        html.Div("Panjang vertikal: {{ panjangvertikal }} km")
                        html.Div("Jumlah outlet: {{ jumlahoutlet }} ")
                        html.Div("Latitude pointer: {{ latitude }}", classes="mt-2")
                        html.Div("Longitude pointer: {{ longitude }}")

                        html.Div("Jarak pointer-midpoint: {{ jaraktitiktengah }} km")
                        html.Div("Elevasi pointer: {{ ketinggian }} meter")
                        html.Div("Jumlah sel kontributif: {{ FA }} sel")
                        html.Div("Luas watershed: {{ luasdas }} km2")
                        html.Div("Estimasi debit puncak: {{ Qp }} m3/detik")
                        html.Div("Koefisien: {{ koefisien }}")
                        html.Div("Curah hujan: {{ curahhujan }} mm/jam")
                        html.A(v_bind_href="maps_url", v_text="maps_url", target="_blank", style="color: blue; text-decoration: underline;")

if __name__ == "__main__":
    server.start(port=8081, address="0.0.0.0")
