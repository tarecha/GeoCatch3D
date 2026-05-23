# --- LETAKKAN DI BARIS PALING ATAS (BARIS 1) ---
from trame.app import get_server
server = get_server(client_type="vue3")
state, ctrl = server.state, server.controller

# --- IMPORT MODULE LAINNYA DI BAWAHNYA ---
import numpy as np
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import re
import time, os


# Modul lokal AGUNG222
import modul.config as cfg
from modul import plotter as pla, curahhujan, mapping, seleksiRHD, pilih, visualCallBackTrame, fileHandler, analisis, watershed as wts
import modul.konverter as knv

# Import Trame UI (Pastikan pakai vuetify3)
from trame.ui.vuetify3 import SinglePageLayout
from pyvista.trame.ui import plotter_ui
from trame.widgets import html, vuetify3 as vuetify



state.items_list = curahhujan.tabelkoefisien
state.rainfall= curahhujan.tabelcurahhujan

ctrl.rainfall = cfg.defautrainfall
ctrl.selected_option = cfg.defautselected_option
#state.selected_option = []
#state.custom_option_input = []
state.curahhujan ="-"
state.koefisien = "-"
state.latitude_input = str(cfg.latitude)
state.longitude_input = str(cfg.longitude)
# state.latitude_input = "-8.302212" #tambakrejo1
# state.longitude_input = "112.670139"
state.user_defined_input =""
state.user_defined_rainfall_input =""
# state.latitude_input = "-8.31063999" #lapangan terbang grati
# state.longitude_input = "112.49429999"

state.radius_input = str(cfg.radius)
state.latitude = "-"
state.longitude = "-"
state.ketinggian = "-"
state.ketinggianhulu = "-"
state.I_mm_perjam = "-"
state.TC = "-"
state.maps_url = "#"
state.maps_text = "Google Maps : klik kanan dahulu pada area visualisasi"
state.estimasi_text = "Link estimasi"
state.estimasi_url = cfg.linkestimasi
state.kemiringan = "-"
state.deltaelevasi = "-"
state.loading = False
state.alert_message = ""
state.alert_show = False
state.mesh_option = cfg.defaultmeshoption
state.snap_option = False
state.multidas_option = False
state.ketinggiantitiktengah = "-"
state.luasdas = "-"
state.Qp = "-"
state.FlowAccum= "-"
state.FlowAccumMDInf = "-"
state.luasanalisis ="-"
state.panjanghorizontal ="-"
state.panjangvertikal = "-"
state.jaraktitiktengah= "-"
state.height_perpixel_m = "-"
state.width_perpixel_m = "-"
state.diagonal_perpixel_m = "-"
state.area_per_pixel_m2 ="-"
state.jumlahoutlet = "-"
state.jarakaAliranUtama_km = "-"
#state.layout__title = "Geospatial Hydrological Analysis by Mochamad Agung Tarecha"
state.trame__title = "by Tarecha"
state.elevasimin = "-"
state.elevasimax = "-"
state.dynamicthreshold = "-"
state.deltaelevasioutlet_pointer= "-"
plotter = pv.Plotter(off_screen=True)
#plotter.lighting = 'None'
plotter.set_scale(1, 1, 0.03333333)
# plotter.set_background("white")  # atau "gray"
# plotter.enable_lightkit()
dummy_awal = pv.Cube()
plotter.add_mesh(dummy_awal, name="dummy_awal", opacity=0.0)
plotter.render() #
viewer = None
@ctrl.add("view_update")
def view_update():
    # kosong, hanya untuk trigger remote viewer
    pass
def reset_plotter():
    plotter.clear()
    plotter.clear_actors()
    plotter.remove_actor("*")
    plotter.renderer.RemoveAllViewProps()
    plotter.set_scale(1, 1, 0.033333)
    #if viewer:
    #    plotter.reset_camera()
    #    viewer.update()
    #   ctrl.view_update()

    print("Actor saat ini:", len(plotter.renderer.actors))
    print("Renderer props setelah clear:", len(plotter.renderer._actors))
    #plotter.reset_camera()
    time.sleep(0.5)


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
    state.luasdas = "-"
    state.TC = "-"
    state.I_mm_perjam = "-"
    state.Qp = "-"
    state.alert_message = "-"
    state.alert_show = False
    state.estimasi_url = "#"
    state.dynamicthreshold = "-"
    state.deltaelevasi ="-"
    state.deltaelevasioutlet_pointer= "-"
    state.kemiringan = "-"
@ctrl.set("run_analysis")
def run_analysis():


    clear_state(state)
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

        ketinggianmaxmatrikKecil = np.max(matrikKecil)
        print(f"ketinggianmax {ketinggianmaxmatrikKecil}")
        if ketinggianmaxmatrikKecil == 0:
            raise ValueError(
                f"Tidak ditemukan daratan. Cek input koordinat apakah lautan ? atau cek keberadaan file dataset GDEM ASTER.")

        pixelBarisAwalKoordinat = barisMatriks - radiusBaris
        pixelKolomAwalKoordinat = kolomMatriks - radiusKolom
        print(f"pixelBarisAwalKoordinat {pixelBarisAwalKoordinat}")
        #ganti mssatrik kecil yang merupakan dem original dengan dem yang sudah di breach depression
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
        print(f"ketinggianTengah di maintrame depression breach {ketinggianTengah}")
        state.ketinggiantitiktengah = round(ketinggianTengah,2)
        ketinggianUtara = matrikKecil[barisUtara - 1, kolomUtara]

        rasio = max(rad * 0.5, 20)  # tinggi minimal 3 unit (agar tetap terlihat)
        radiuscone = (rasio * 0.05)  # radius = 10% dari tinggi (proporsional)
        tingicone = rasio * 2

        # Penempatan z: letakkan cone agar base-nya menempel terrain
        zConeTengah = ketinggianTengah + tingicone / 2
        zConeUtara = ketinggianUtara + tingicone / 2
        print(f"tingicone {tingicone}, radiuscone {radiuscone}")

        coneTengah = pv.Cone(center=(kolomTengah, barisTengah, zConeTengah), radius=radiuscone, height=tingicone, direction=(0, 0, -1))
        coneUtara = pv.Cone(center=(kolomUtara, barisUtara - 1, zConeUtara), radius=radiuscone, height=tingicone, direction=(0, 0, -1))

        plotter.add_mesh(coneTengah, color="red", specular=1.0, show_edges=True, smooth_shading=False,pickable=False)
        plotter.add_mesh(coneUtara, color="magenta", specular=1.0, show_edges=True, smooth_shading=False,pickable=False)
        meshoption = state.mesh_option
        print(f"meshoption {meshoption}")
        koordinatCekungan, flow_accum_MDInf,flow_accum_D8,matriktributaryidentifier,transformasi, matrikFAD8elevasi = analisis.importFlowAccumulation(matrikKecil.copy(), ketinggianTengah, lat, rad,meshoption, state)

        tampilflowaccum = np.flipud(flow_accum_D8.copy())
        print(f"min tampilflowaccum {np.min(tampilflowaccum)}")
        tampilflowaccum = np.where(tampilflowaccum < 0, 0, tampilflowaccum)

        tampilflowaccumelevation = np.flipud(matrikFAD8elevasi.copy())
        print(f"min tampilflowaccumelevation {np.min(tampilflowaccumelevation)}")
        tampilflowaccumelevation = np.where(tampilflowaccumelevation < 0, 0, tampilflowaccumelevation)

       #fileHandler.eksporTIF(matrikFAthresholdketinggian, lat, lon, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat,  cfg.fileFlowAccumulationBreachThresholdKetinggian,cfg.default_crs)
         #jika Watershednya dipilih interaktif gk perlu calon embung ditampilkan
        if state.mesh_option != "watershedinteractive":
            for row in koordinatCekungan:
                px, py = int(row[1]), int(row[0])
                pz = matrikKecil[py, px]
                cone = pv.Cone(center=(px, py, pz + tingicone), direction=(0, 0, -1), radius=radiuscone, height=tingicone*2)
                plotter.add_mesh(cone, color='cyan', smooth_shading=False,pickable=False, lighting=False,show_edges=True)
                time.sleep(0.05)


        #rubah cmap agar nilai paling rendah warna putih
        blue_red = LinearSegmentedColormap.from_list('blue_red', ['blue','green','yellow','red'])
        # 2. Sampling jadi 64 warna (RGBA)
        cmapfa = blue_red(np.linspace(0, 1, 32))  # bentuk: (64, 4)
        # 3. Modifikasi warna pertama (misalnya jadi putih)
        cmapfa[0] = [1, 1, 1, 1]  # R, G, B, A → putih solid


        # minflowaccum = np.min(tampilflowaccum)
        # maskminus = tampilflowaccum == 0
        # pla.plot(maskminus, "mask minus", "nilai")
        # maskminus = np.ma.masked_where(maskminus, tampilflowaccum)
        # pla.plot(maskminus, "mask minus flow", "nilai")
        # if minflowaccum < 2:
        #     for i in range(4):
        #         cmapfa[i] = [1, 1, 1, 1]
        #     print(f"maxflowaccum {minflowaccum} di if")
        #     print(cmapfa)
        # else:
        #     print(f"maxflowaccum {minflowaccum} di else")
        #     print(cmapfa)
        # 4. Buat colormap baru dari array warna
        custom_cmapfa1 = LinearSegmentedColormap.from_list('custom_cmapfa1', cmapfa)

        if state.mesh_option == "flow":
            matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "flowelevation":
            matrikScalar = np.flipud(np.rot90(tampilflowaccumelevation, k=1))
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "watershed":
            watershed=wts.getwatershed()
            matrikScalar = np.rot90(watershed, k=-1)
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False,  lighting=False)
        elif state.mesh_option == "watershedinteractive":
            #watershed = wts.getFAwatershedinteractive(tampilflowaccum)
            #matrikScalar = np.rot90(watershed, k=-1)
            matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True,
                             pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "FAwatershed":
            watershed = wts.getFAwatershed(tampilflowaccum)
            matrikScalar = np.rot90(watershed, k=-1)
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True,
                             pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)
        else :
            matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            plotter.add_mesh(grid.elevation().copy(), cmap=custom_terrain, show_edges=True, pickable=True, show_scalar_bar=False, smooth_shading=False, lighting=False)

        #save file scalarnya untuk keperluan laporan
        matrikScalar = np.rot90(matrikScalar, k=1)
        fileHandler.eksporTIF3(matrikOut=matrikScalar, fullPath=cfg.fileScalar, transformasi=transformasi,
                               cmap_obj=custom_cmapfa1, crs=cfg.default_crs)
        plotter.reset_camera()
        viewer.update()



        if viewer:
            plotter.reset_camera()
            viewer.update()
            #penyesuaian projection
            y,x = knv.cells_to_km2(1,lat)[2:4]
            print(f"scale {x}, {y}")
            plotter.set_scale(  x, y , 1)
            # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # screenshot_path = os.path.join(os.getcwd(), f"visualisasi_{timestamp}.png")
            # plotter.screenshot(screenshot_path)
            print(f"✅ Viewer update selesai. Siap di render")
        plotter.reset_camera()
        state.alert_message = "✅ Analisis berhasil dirender ulang "
        state.alert_show = True
        time.sleep(0.5)
        callback = visualCallBackTrame.make_callback(lat, lon, radiusBaris, radiusKolom, barisMatriks, kolomMatriks,
                                                     state, ketinggianTengah, flow_accum_MDInf, flow_accum_D8,
                                                     matriktributaryidentifier, matrikKecil.copy(),transformasi, plotter, custom_cmapfa1,grid,coneTengah, coneUtara,tingicone,pv,radiuscone, viewer, ctrl)
        plotter.disable_picking()
        time.sleep(0.5)
        plotter.enable_point_picking(callback=callback, tolerance=0.025, use_picker=True, show_point=True, color="red", point_size=25,
                                     show_message=False)



        #print("Lighting mode:", plotter.lighting)
        print("Actor saat ini:", len(plotter.renderer.actors))
    except Exception as e:
        state.alert_message = f"❌ Gagal: {str(e)}"
        state.alert_show = True
    finally:
        state.loading = False

with SinglePageLayout(server, toolbar=True, footer=False) as layout:
    layout.title.set_text("GeoCatch 3D - Sistem Analisis Identifikasi Lokasi Potensial Embung dan DAS.")
    with layout.content:
        with vuetify.VContainer(fluid=True):
            with vuetify.VRow():
                with vuetify.VCol(cols=9, style="height: 100vh;"):
                    viewer = plotter_ui(plotter, height="100%", return_viewer=True, interactive=True, default_server_rendering=True)
                    with vuetify.VCard():
                        vuetify.VCardTitle("Informasi Kontrol")
                        html.Div("1. Klik kiri drag = rotasi bebas.")
                        html.Div("2. Klik kiri drag + ctrl = rotasi z.")
                        html.Div("3. Klik kiri drag + shift = move (pan).")
                        html.Div("4. Scroll = zoom in / zoom out.")
                        html.Div("5. Klik kanan = pilih sel.")

                        vuetify.VCardTitle("Catatan Penting")
                        html.Div("1. Luas watershed / DAS valid bila tidak terpotong tepi area analisis.")
                        html.Div("2. Lokasi outlet valid bila tidak berada di tepi area analisis.")

                        vuetify.VCardTitle("Display Mode")
                        html.Div("Flow Accumulation (FA) = menampilkan akumulasi aliran.")
                        html.Div("FA threshold elevation = menampilkan akumulasi aliran yang berada diatas titik tengah (asumsi lahan target).")
                        html.Div("Watershed = menampilkan daerah aliran sungai (DAS).")
                        html.Div("FA + Watershed = menampilkan FA dikombinasi DAS.")
                        html.Div("FA + Watershed Interactive = menampilkan FA dikombinasi DAS interaktif klik kanan dahulu.")
                        html.Div("Terrain elevation = menampilkan colormap sesuai elevasi.")
                        html.Div("")
                        html.Div("Fitur : ")
                        html.Div(
                            "1 . Reposisi pointer ke jaringan terdekat = titik DAS otomatis dipindahkan ke jaringan aliran terdekat hingga 3 sel.")
                        html.Div(
                            "Saat fitur reposisi aktif, informasi titik tetap dihitung berdasarkan sel awal yang dipilih. Pilih sel secara presisi agar hasil Informasi Titik sesuai.")
                        html.Div(
                            "2. Multi seleksi DAS = deliniasi beberapa DAS sekaligus pada titik yang dipilih.")
                    with html.Div(style="display: flex; gap: 15px; margin-top: 10px;"):
                        html.A("( Dokumentasi )",
                               href="https://tarecha.wordpress.com/publikasi-ilmiah/",
                               target="_blank",
                               style="color: blue; text-decoration: underline;")

                        html.A("( Tutorial )",
                               href="https://tarecha.wordpress.com/wp-content/uploads/2026/05/tutorial-penggunaan.pdf",
                               target="_blank",
                               style="color: blue; text-decoration: underline;")

                        html.A("(Surat Pencatatan Ciptaan No. 001234288)",
                               href="https://tarecha.wordpress.com/wp-content/uploads/2026/05/suratciptaan_ec002026065878.pdf",
                               target="_blank",
                               style="color: blue; text-decoration: underline;")
                        html.Div(
                            "Vue v3")
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
                            item_title="text",  # tampilkan field `text`
                            item_value="value",  # gunakan field `value` sebagai v-model
                            label="Pilih Koefisien C SNI 2415:2016 ",
                            outlined=True,
                            dense=True,

                            no_data_text="No data available",
                        )

                        # --- Tambahkan VTextField di bawahnya ---
                        vuetify.VTextField(
                            v_model="user_defined_input",  # v-model baru untuk menyimpan input manual
                            label="Masukkan Koefisien C manual",
                            outlined=True,
                            dense=True,

                            # INI KUNCINYA: tampilkan hanya jika 'selected_option' adalah 'user_defined'
                            v_show="selected_option === 'user_defined'",
                        )

                        vuetify.VSelect(
                            # 2) v_model sebagai tuple (nama, default)
                            v_model=("selected_option_rainfall", None),
                            # 3) items juga tuple (nama, default)
                            items=("rainfall", ctrl.rainfall),
                            item_title="text",  # tampilkan field `text`
                            item_value="value",  # gunakan field `value` sebagai v-model
                            label="Pilih Curah Hujan (mm/hari)",
                            outlined=True,
                            dense=True,

                            no_data_text="No data available",
                        )

                        # --- Tambahkan VTextField di bawahnya ---
                        vuetify.VTextField(
                            v_model="user_defined_rainfall_input",  # v-model baru untuk menyimpan input manual
                            label="Masukkan curah hujan manual (mm/hari)",
                            outlined=True,
                            dense=True,

                            # INI KUNCINYA: tampilkan hanya jika 'selected_option' adalah 'user_defined'
                            v_show="selected_option_rainfall === 'user_defined'",
                        )


                        #cfg.koefisien = state.selected_option
                        # TextField yang hanya tampil jika opsi 'user_defined' dipilih

                        vuetify.VCardTitle("Display Mode")
                        with vuetify.VRadioGroup(v_model="mesh_option", class_="mb-3"):
                            vuetify.VRadio(label="Flow Accumulation (FA)", value="flow")
                            vuetify.VRadio(label="FA threshold elevation", value="flowelevation")
                            vuetify.VRadio(label="Watershed", value="watershed")
                            vuetify.VRadio(label="FA + Watershed", value="FAwatershed")
                            vuetify.VRadio(label="FA + Watershed Interactive", value="watershedinteractive")
                            vuetify.VRadio(label="Terrain elevation", value="terrain")
                        vuetify.VCheckbox(
                            v_model=("snap_option", False),
                            label="Reposisi pointer ke jaringan terdekat",
                            dense=True,

                            v_show="mesh_option === 'watershedinteractive'",
                        )
                        vuetify.VCheckbox(
                            v_model=("multidas_option", False),
                            label="Multi seleksi DAS",
                            dense=True,

                            v_show="mesh_option === 'watershedinteractive'",
                        )
                        vuetify.VBtn("Analysys", color="primary", click=ctrl.run_analysis)
                        vuetify.VProgressLinear(indeterminate=True, v_show="loading", color="deep-purple", class_="mt-3")
                        vuetify.VAlert(type="info", v_model="alert_show", v_text="alert_message", class_="mt-3")

                    with vuetify.VCard():
                        vuetify.VCardTitle("Informasi Titik")
                        html.Div("Informasi tampil pada rendering mode 'remote'")
                        html.Div("Elevasi Min: '{{ elevasimin }}' meter")
                        html.Div("Elevasi Titik Tengah: '{{ ketinggiantitiktengah }}' meter")
                        html.Div("Elevasi Max: '{{ elevasimax }}' meter")


                        html.Div("Panjang horizontal: '{{ panjanghorizontal }}' km")
                        html.Div("Panjang vertikal: '{{ panjangvertikal }}' km")
                        html.Div("Luas analisis: '{{ luasanalisis }}' km²")

                        html.Div("Jumlah lokasi potensial embung: '{{ jumlahoutlet }}' ")
                        html.Div("Latitude pointer: '{{ latitude }}'", classes="mt-2")
                        html.Div("Longitude pointer: '{{ longitude }}'")
                        html.Div("Delta elevasi midpoint-(pointer): '{{ deltaelevasioutlet_pointer }}' m")
                        html.Div("Jarak pointer-midpoint: '{{ jaraktitiktengah }}' km")

                        html.Div("Tinggi 1 sel: '{{ height_perpixel_m  }}' m")
                        html.Div("Lebar 1 sel: '{{ width_perpixel_m  }}' m")
                        html.Div("Diagonal 1 sel: '{{ diagonal_perpixel_m  }}' m")
                        html.Div("Luas 1 sel : '{{ area_per_pixel_m2 }}' m²")
                        html.Div("Jumlah D8 FA: '{{ FlowAccum }}' sel")
                        html.Div("Jumlah MD∞ FA: '{{ FlowAccumMDInf }}' sel")
                        html.Div("Luas DAS (MD∞ * luas 1 sel): '{{ luasdas }}' km²")
                        html.Div("Dynamic Threshold FA: '{{ dynamicthreshold }}' sel")


                        html.Div("TC Kirpich")
                        html.Div("Elevasi hilir (pointer): '{{ ketinggian }}' meter")

                        html.Div("Elevasi hulu: '{{ ketinggianhulu }}' meter")
                        html.Div("Delta elevasi hulu-(pointer): '{{ deltaelevasi }}' m")
                        html.Div("Kemiringan hulu - hilir: '{{ kemiringan }}'")

                        html.Div("Panjang aliran utama : '{{jarakaAliranUtama_km}}' km")
                        html.Div("Time concentration: '{{TC}}' jam")


                        html.Div("Intensitas hujan Monobe")
                        html.Div("Curah hujan: '{{ curahhujan }}' mm/hari")
                        html.Div("Intensitas hujan: '{{I_mm_perjam}}' mm/jam")


                        html.Div("Metode Rasional")
                        html.Div("Koefisien: '{{ koefisien }}'")
                        html.Div("Estimasi debit puncak: '{{ Qp }}' m³/detik")

                        html.A(v_bind_href="maps_url", v_text="maps_text", target="_blank", style="color: blue; text-decoration: underline;")
                        html.Div("")
                        html.A(v_bind_href="estimasi_url", v_text="estimasi_text", target="_blank",
                               style="color: blue; text-decoration: underline;")

if __name__ == "__main__":
    print(f"Akses melalui webrowser dari PC lain dengan IP : ")
    os.system("ipconfig | findstr IPv4")  # Ini akan langsung mencetak IP kamu dsi terminal
    server.start(host="0.0.0.0", port=80, argv=[])
