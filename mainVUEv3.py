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
import webbrowser
import threading
import socket
import glob, os
import time
# Modul lokal AGUNG222
import modul.config as cfg
from modul import curahhujan, mapping, seleksiRHD, pilih, visualCallBackTrame, fileHandler, analisis, watershed as wts
import modul.konverter as knv

# Import Trame UI (Pastikan pakai vuetify3)
from trame.ui.vuetify3 import SinglePageLayout
from pyvista.trame.ui import plotter_ui
from trame.widgets import html, vuetify3 as vuetify

state.items_list = curahhujan.tabelkoefisien
state.rainfall = curahhujan.tabelcurahhujan

ctrl.rainfall = cfg.defautrainfall
ctrl.selected_option = cfg.defautselected_option
state.curahhujan = "-"
state.koefisien = "-"
state.mulai_analisis = False
state.latitude_input = str(cfg.latitude)
state.longitude_input = str(cfg.longitude)
state.user_defined_input = ""
state.user_defined_rainfall_input = ""

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
state.FlowAccum = "-"
state.FlowAccumMDInf = "-"
state.luasanalisis = "-"
state.panjanghorizontal = "-"
state.panjangvertikal = "-"
state.jaraktitiktengah = "-"
state.height_perpixel_m = "-"
state.width_perpixel_m = "-"
state.diagonal_perpixel_m = "-"
state.area_per_pixel_m2 = "-"
state.jumlahoutlet = "-"
state.jarakaAliranUtama_km = "-"
state.trame__title = "by Tarecha"
state.elevasimin = "-"
state.elevasimax = "-"
state.dynamicthreshold = "-"
state.deltaelevasioutlet_pointer = "-"

plotter = pv.Plotter(off_screen=True)
plotter.set_scale(1, 1, 0.03333333)
dummy_awal = pv.Cube()
plotter.add_mesh(dummy_awal, name="dummy_awal", opacity=0.0)
plotter.render()
viewer = None


@ctrl.set("view_update")
def view_update():
    # kosong, hanya untuk trigger remote viewer
    pass


def reset_plotter():
    plotter.clear()
    plotter.clear_actors()
    plotter.remove_actor("*")
    plotter.renderer.RemoveAllViewProps()
    print("Actor saat ini:", len(plotter.renderer.actors))
    print("Renderer props setelah clear:", len(plotter.renderer._actors))


def bersihkan_ramdisk():
    # Mengambil semua file di dalam folder temp
    files = glob.glob(os.path.join(cfg.pathTempMaps, '*'))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            pass  # Abaikan jika ada file yang sedang dikunci/digunakan


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
    state.deltaelevasi = "-"
    state.deltaelevasioutlet_pointer = "-"
    state.kemiringan = "-"


#@ctrl.set("run_analysis")
#def run_analysis():
@state.change("mulai_analisis")
def run_analysis(mulai_analisis, **kwargs):
    # Jika sinyalnya False, abaikan
    if not mulai_analisis:
        return
    try:
        #state.loading = True



        bersihkan_ramdisk()

        clear_state(state)
        global plotter, viewer

        if not viewer:
            print("❗ Viewer belum siap. Analisis dibatalkan.")
            return

            # =========================================================================
            # 1. VALIDASI DAN PERSIAPAN INPUT PARAMETER
            # =========================================================================
            # Bersihkan semua input dari spasi berlebih
        lat_str = state.latitude_input.strip()
        lon_str = state.longitude_input.strip()
        rad_str = state.radius_input.strip()
        c_str = state.user_defined_input.strip()
        rainfall_str = state.user_defined_rainfall_input.strip()

        # Validasi Koordinat dan Radius
        if not re.match(r"^-?\d+(\.\d+)?$", lat_str):
            raise ValueError("Latitude harus berupa angka desimal.")
        if not re.match(r"^-?\d+(\.\d+)?$", lon_str):
            raise ValueError("Longitude harus berupa angka desimal.")
        if not rad_str.isdigit():
            raise ValueError(f"Radius harus berupa bilangan bulat positif. Min 1 dan max {cfg.maxRadius}")

        if int(rad_str) > cfg.maxRadius or int(rad_str) <= 0:
            raise ValueError(f"Radius harus berupa bilangan bulat positif. Min 1 dan max {cfg.maxRadius}")

        # Konversi koordinat dan radius
        lat = float(lat_str)
        lon = float(lon_str)
        rad = int(rad_str)
        meshoption = state.mesh_option

        # Validasi dan Pengisian Koefisien (C)
        if state.selected_option is None:
            raise ValueError("Pilih koefisien!")

        if state.selected_option == "user_defined":
            if c_str == "":
                raise ValueError("Koefisien harus pecahan 0 < C <= 1")
            if not c_str.replace('.', '', 1).isdigit():
                raise ValueError("Koefisien harus pecahan 0 < C <= 1")

            c_val = float(c_str)
            if c_val <= 0 or c_val > 1:
                raise ValueError("Koefisien harus pecahan 0 < C <= 1")
            cfg.koefisien = c_val
        else:
            cfg.koefisien = float(state.selected_option)

        state.koefisien = cfg.koefisien
        print(f"Koefisien diselek: {cfg.koefisien}")

        # Validasi dan Pengisian Curah Hujan
        if state.selected_option_rainfall is None:
            raise ValueError("Pilih curah hujan!")

        if state.selected_option_rainfall == "user_defined":
            if rainfall_str == "":
                raise ValueError("Curah hujan harus berupa angka positif.")
            if not rainfall_str.replace('.', '', 1).isdigit():
                raise ValueError("Curah hujan harus berupa angka positif.")
            cfg.curahhujan = float(rainfall_str)
        else:
            cfg.curahhujan = float(state.selected_option_rainfall)

        state.curahhujan = cfg.curahhujan
        print(f"Curah hujan diselek: {cfg.curahhujan}")

        # =========================================================================
        # 2. EKSTRAKSI DEM & PRE-PROCESSING (BREACH DEPRESSION)
        # =========================================================================
        radiusBaris = rad
        radiusKolom = rad
        ukuran_baris = radiusBaris * 2 + 1
        ukuran_kolom = radiusKolom * 2 + 1

        barisKoma, kolomKoma = mapping.MappingLatLongkeBarisKolom(lat, lon)
        barisMatriks, kolomMatriks = seleksiRHD.seleksiRHD(barisKoma, kolomKoma)
        t0 = time.perf_counter()
        matrikBesar, baris, kolom = pilih.pilih(barisMatriks, kolomMatriks, lat, lon)
        t1 = time.perf_counter()
        print(f"Waktu Proses pilih: {t1 - t0:.4f} detik")
        pixelBarisAwal = baris - radiusBaris
        pixelKolomAwal = kolom - radiusKolom

        matrikKecil = matrikBesar[pixelBarisAwal: pixelBarisAwal + ukuran_baris,
                      pixelKolomAwal: pixelKolomAwal + ukuran_kolom].astype(np.float32).copy()

        ketinggianmaxmatrikKecil = np.max(matrikKecil)
        print(f"ketinggianmax {ketinggianmaxmatrikKecil}")
        if ketinggianmaxmatrikKecil == 0:
            raise ValueError(
                f"Tidak ditemukan daratan. Cek input koordinat apakah lautan ? atau cek keberadaan file dataset GDEM ASTER.")

        pixelBarisAwalKoordinat = barisMatriks - radiusBaris
        pixelKolomAwalKoordinat = kolomMatriks - radiusKolom
        print(f"pixelBarisAwalKoordinat {pixelBarisAwalKoordinat}")

        # Ekspor TIF Original
        fileHandler.eksporTIF(matrikKecil, lat, lon, pixelKolomAwalKoordinat, pixelBarisAwalKoordinat,
                              cfg.fileSeleksiDEM, cfg.default_crs)

        # Eksekusi Breach Depression
        matrikKecil = analisis.breachdepression()
        matrikKecil = np.flipud(matrikKecil)

        # =========================================================================
        # 3. PROSES BERAT HIDROLOGI (WHITEBOX TOOLS & PENGOLAHAN MATRIKS)
        # =========================================================================
        kolomTengah = radiusKolom
        barisTengah = radiusBaris
        ketinggianTengah = matrikKecil[barisTengah, kolomTengah]

        print(f"ketinggianTengah di maintrame depression breach {ketinggianTengah}")
        state.ketinggiantitiktengah = round(ketinggianTengah, 2)
        print(f"meshoption {meshoption}")

        koordinatCekungan, flow_accum_MDInf, flow_accum_D8, matriktributaryidentifier, transformasi, matrikFAD8elevasi = analisis.importFlowAccumulation(
            matrikKecil.copy(), ketinggianTengah, lat, rad, meshoption, state)

        tampilflowaccum = np.flipud(flow_accum_D8.copy())
        print(f"min tampilflowaccum {np.min(tampilflowaccum)}")
        tampilflowaccum = np.where(tampilflowaccum < 0, 0, tampilflowaccum)

        tampilflowaccumelevation = np.flipud(matrikFAD8elevasi.copy())
        print(f"min tampilflowaccumelevation {np.min(tampilflowaccumelevation)}")
        tampilflowaccumelevation = np.where(tampilflowaccumelevation < 0, 0, tampilflowaccumelevation)

        # =========================================================================
        # 4. PERSIAPAN DATA VISUAL 3D (GRID, WARNA, MARKER/CONE)
        # =========================================================================
        kolomUtara = radiusKolom
        barisUtara = radiusBaris * 2

        x = np.arange(0, ukuran_kolom, dtype=np.float32)
        y = np.arange(0, ukuran_baris, dtype=np.float32)
        X, Y = np.meshgrid(x, y)
        grid = pv.StructuredGrid(X, Y, matrikKecil)

        # Setup Warna Terrain
        terrain_colors = plt.get_cmap("terrain")(np.linspace(0, 1, 256))
        zmin = np.min(matrikKecil)
        zmax = np.max(matrikKecil)
        state.elevasimin = int(zmin)
        state.elevasimax = int(zmax)
        if zmin == 0:
            terrain_colors[0] = [1, 1, 1, 1]
        custom_terrain = LinearSegmentedColormap.from_list("custom_terrain", terrain_colors)

        # Setup Parameter Cone Marker
        ketinggianUtara = matrikKecil[barisUtara - 1, kolomUtara]
        rasio = max(rad * 0.5, 20)
        radiuscone = (rasio * 0.05)
        tingicone = rasio * 2
        zConeTengah = ketinggianTengah + tingicone / 2
        zConeUtara = ketinggianUtara + tingicone / 2
        print(f"tingicone {tingicone}, radiuscone {radiuscone}")

        coneTengah = pv.Cone(center=(kolomTengah, barisTengah, zConeTengah), radius=radiuscone, height=tingicone,
                             direction=(0, 0, -1))
        coneUtara = pv.Cone(center=(kolomUtara, barisUtara - 1, zConeUtara), radius=radiuscone, height=tingicone,
                            direction=(0, 0, -1))

        # Setup Colormap Flow Accumulation (FA)
        blue_red = LinearSegmentedColormap.from_list('blue_red', ['blue', 'green', 'yellow', 'red'])
        cmapfa = blue_red(np.linspace(0, 1, 32))
        cmapfa[0] = [1, 1, 1, 1]
        custom_cmapfa1 = LinearSegmentedColormap.from_list('custom_cmapfa1', cmapfa)

        # =========================================================================
        # 5. RENDERING MESH KE PLOTTER (BAGIAN BAWAH)
        # =========================================================================
        reset_plotter()

        plotter.add_mesh(coneTengah, color="red", specular=1.0, show_edges=True, smooth_shading=False, pickable=False)
        plotter.add_mesh(coneUtara, color="magenta", specular=1.0, show_edges=True, smooth_shading=False,
                         pickable=False)

        # Jika opsi bukan interactive, tambahkan cone untuk cekungan embung
        if state.mesh_option != "watershedinteractive":
            for row in koordinatCekungan:
                px, py = int(row[1]), int(row[0])
                pz = matrikKecil[py, px]
                cone = pv.Cone(center=(px, py, pz + tingicone), direction=(0, 0, -1), radius=radiuscone,
                               height=tingicone * 2)
                plotter.add_mesh(cone, color='cyan', smooth_shading=False, pickable=False, lighting=False,
                                 show_edges=True)

        # Render Grid berdasarkan opsi
        if state.mesh_option == "flow":
            matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True,
                             show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "flowelevation":
            matrikScalar = np.flipud(np.rot90(tampilflowaccumelevation, k=1))
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True,
                             show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "watershed":
            watershed = wts.getwatershed()
            matrikScalar = np.rot90(watershed, k=-1)
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True,
                             show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "watershedinteractive":
            matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True,
                             show_scalar_bar=False, smooth_shading=False, lighting=False)
        elif state.mesh_option == "FAwatershed":
            watershed = wts.getFAwatershed(tampilflowaccum)
            matrikScalar = np.rot90(watershed, k=-1)
            plotter.add_mesh(grid.copy(), scalars=matrikScalar, cmap=custom_cmapfa1, show_edges=True, pickable=True,
                             show_scalar_bar=False, smooth_shading=False, lighting=False)
        else:
            matrikScalar = np.flipud(np.rot90(tampilflowaccum, k=1))
            plotter.add_mesh(grid.elevation().copy(), cmap=custom_terrain, show_edges=True, pickable=True,
                             show_scalar_bar=False, smooth_shading=False, lighting=False)

        # =========================================================================
        # 6. EXPORT FILE REPORT & UPDATE SCALING VIEWER
        # =========================================================================
        matrikScalar = np.rot90(matrikScalar, k=1)
        fileHandler.eksporTIF3(matrikOut=matrikScalar, fullPath=cfg.fileScalar, transformasi=transformasi,
                               cmap_obj=custom_cmapfa1, crs=cfg.default_crs)

        if viewer:
            plotter.reset_camera()
            viewer.update()
            y, x = knv.cells_to_km2(1, lat)[2:4]
            print(f"scale {x}, {y}")
            plotter.set_scale(x, y, 1)
            print(f"✅ Viewer update selesai. Siap di render")

        plotter.reset_camera()
        state.alert_message = "✅ Rendering is done."
        state.alert_show = True
        print("Actor saat ini:", len(plotter.renderer.actors))

        # =========================================================================
        # 7. KONFIGURASI CALLBACK POINT PICKING (PALING BAWAH)
        # =========================================================================
        callback = visualCallBackTrame.make_callback(lat, lon, radiusBaris, radiusKolom, barisMatriks, kolomMatriks,
                                                     state, ketinggianTengah, flow_accum_MDInf, flow_accum_D8,
                                                     matriktributaryidentifier, matrikKecil.copy(), transformasi,
                                                     plotter, custom_cmapfa1, grid, coneTengah, coneUtara, tingicone,
                                                     pv, radiuscone, viewer, ctrl)

        plotter.disable_picking()
        plotter.enable_point_picking(callback=callback, tolerance=0.025, use_picker=True, show_point=True, color="red",
                                     point_size=25,
                                     show_message=False)

    except Exception as e:
        state.alert_message = f"❌ Gagal: {str(e)}"
        state.alert_show = True
        print(f"Terjadi error: {e}")
    finally:
        state.loading = False
        state.mulai_analisis = False


with SinglePageLayout(server, toolbar=True, footer=False) as layout:
    layout.title.set_text("GeoCatch 3D - Sistem Analisis Identifikasi Lokasi Potensial Embung dan DAS.")
    with layout.content:
        with vuetify.VContainer(fluid=True):
            with vuetify.VRow():
                with vuetify.VCol(cols=9, style="height: 100vh;"):
                    viewer = plotter_ui(plotter, height="100%", return_viewer=True, interactive=True,
                                        default_server_rendering=True, local_rendering=False)
                    with vuetify.VCard():
                        vuetify.VCardTitle("Informasi Kontrol")
                        html.Div("1. Klik kiri drag = rotasi bebas.")
                        html.Div("2. Klik kiri drag + ctrl = Spin / Roll Z-Axis")
                        html.Div("3. Klik kiri drag + shift = move (pan).")
                        html.Div("4. Scroll = zoom in / zoom out.")
                        html.Div("5. Klik kanan = pilih sel.")

                        vuetify.VCardTitle("Catatan Penting")
                        html.Div("1. Luas watershed / DAS valid bila tidak terpotong tepi area analisis.")
                        html.Div("2. Lokasi outlet valid bila tidak berada di tepi area analisis.")

                        vuetify.VCardTitle("Display Mode")
                        html.Div("Flow Accumulation (FA) = menampilkan akumulasi aliran.")
                        html.Div(
                            "FA threshold elevation = menampilkan akumulasi aliran yang berada diatas titik tengah (asumsi lahan target).")
                        html.Div("Watershed = menampilkan daerah aliran sungai (DAS).")
                        html.Div("FA + Watershed = menampilkan FA dikombinasi DAS.")
                        html.Div(
                            "FA + Watershed Interactive = menampilkan FA dikombinasi DAS interaktif klik kanan dahulu.")
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
                        html.Div("Vue v3")
                with vuetify.VCol(cols=3):
                    with vuetify.VCard(class_="mb-3"):
                        vuetify.VCardTitle("Input Parameter")

                        vuetify.VTextField(v_model="latitude_input", label="Latitude", outlined=True, dense=True,
                                           type="text",
                                           inputmode="decimal",
                                           # Tambahkan huruf r di luar tanda kutip
                                           keydown=r"if(!/^[0-9.\-]$/.test($event.key) && $event.key.length === 1) $event.preventDefault();",
                                           hide_details=True, class_="mb-3", style="margin-bottom: 10px;")
                        vuetify.VTextField(v_model="longitude_input", label="Longitude", outlined=True, dense=True,
                                           type="text",
                                           inputmode="decimal",
                                           # Tambahkan huruf r di luar tanda kutip
                                           keydown=r"if(!/^[0-9.\-]$/.test($event.key) && $event.key.length === 1) $event.preventDefault();",
                                           hide_details=True, class_="mb-3", style="margin-bottom: 10px;")
                        vuetify.VTextField(v_model="radius_input", label="Radius (interval approx 30m)", type="number", step=1,
                                           keydown="if($event.key === '.' || $event.key === ',') $event.preventDefault();",
                                           # Memblokir desimal

                                           outlined=True, dense=True, hide_details=True, class_="mb-3",
                                           style="margin-bottom: 10px;")

                        # PERBAIKAN 1: VSelect menggunakan list langsung dari modul, tanpa ctrl.
                        vuetify.VSelect(
                            v_model=("selected_option", None),
                            items=("list_koefisien", curahhujan.tabelkoefisien),
                            item_title="text",
                            item_value="value",
                            label="Pilih Koefisien C SNI 2415:2016",
                            outlined=True,
                            dense=True,
                        )

                        vuetify.VTextField(
                            v_model="user_defined_input",
                            label="Masukkan Koefisien C manual",
                            type="text",
                            inputmode="decimal",
                            # Tambahkan huruf r di luar tanda kutip
                            keydown=r"if(!/^[0-9.\-]$/.test($event.key) && $event.key.length === 1) $event.preventDefault();",
                            outlined=True,
                            dense=True,
                            v_show="selected_option === 'user_defined'",
                        )

                        # PERBAIKAN 2: VSelect menggunakan list langsung dari modul.
                        vuetify.VSelect(
                            v_model=("selected_option_rainfall", None),
                            items=("list_curahhujan", curahhujan.tabelcurahhujan),
                            item_title="text",
                            item_value="value",
                            label="Pilih Curah Hujan (mm/hari)",
                            outlined=True,
                            dense=True,
                        )

                        vuetify.VTextField(
                            v_model="user_defined_rainfall_input",
                            label="Masukkan curah hujan manual (mm/hari)",
                            outlined=True,
                            dense=True,
                            type="text",
                            inputmode="decimal",
                            # Tambahkan huruf r di luar tanda kutip
                            keydown=r"if(!/^[0-9.\-]$/.test($event.key) && $event.key.length === 1) $event.preventDefault();",
                            v_show="selected_option_rainfall === 'user_defined'",
                        )

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

                        # PERBAIKAN 3: Tombol analisis kembali pakai standar Trame (akan bekerja sinkron dengan yield)
                        vuetify.VBtn("Analysys", color="primary", click="loading = true; mulai_analisis = true,alert_message='Rendering in progress',alert_show = True ", disabled=("loading", False),
                                     loading=("loading", False))

                        vuetify.VProgressLinear(indeterminate=True, v_show="loading", color="deep-purple",
                                                class_="mt-3")

                        with vuetify.VAlert(type="info", v_model="alert_show", density="compact", class_="mt-3"):
                            html.Div("{{ alert_message }}", style="white-space: normal; word-break: break-word;")

                    with vuetify.VCard():
                        vuetify.VCardTitle("Informasi Titik")
                        html.Div("Informasi tampil pada rendering mode 'remote'")
                        html.Div("Elevasi Min: '{{ elevasimin }}' meter")
                        html.Div("Elevasi Titik Tengah: '{{ ketinggiantitiktengah }}' meter")
                        html.Div("Elevasi Max: '{{ elevasimax }}' meter")

                        html.Div("Panjang horizontal: '{{ panjanghorizontal }}' km")
                        html.Div("Panjang vertikal: '{{ panjangvertikal }}' km")
                        html.Div("Luas analisis: '{{ luasanalisis }}' km²")

                        html.Div("Jumlah lokasi potensial embung: '{{ jumlahoutlet }}'")
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

                        html.Div("TC Kirpich", classes="mt-2 font-weight-bold")
                        html.Div("Elevasi hilir (pointer): '{{ ketinggian }}' meter")
                        html.Div("Elevasi hulu: '{{ ketinggianhulu }}' meter")
                        html.Div("Delta elevasi hulu-(pointer): '{{ deltaelevasi }}' m")
                        html.Div("Kemiringan hulu - hilir: '{{ kemiringan }}'")
                        html.Div("Panjang aliran utama : '{{ jarakaAliranUtama_km }}' km")
                        html.Div("Time concentration: '{{ TC }}' jam")

                        html.Div("Intensitas hujan Monobe", classes="mt-2 font-weight-bold")
                        html.Div("Curah hujan: '{{ curahhujan }}' mm/hari")
                        html.Div("Intensitas hujan: '{{ I_mm_perjam }}' mm/jam")

                        html.Div("Metode Rasional", classes="mt-2 font-weight-bold")
                        html.Div("Koefisien: '{{ koefisien }}'")
                        html.Div("Estimasi debit puncak: '{{ Qp }}' m³/detik")

                        # PERBAIKAN 4: Penulisan Link (href) diperbaiki ke format asli Vue 3 yang lebih stabil di Trame
                        html.A("{{ maps_text }}", href=("maps_url", "#"), target="_blank",
                               style="color: blue; text-decoration: underline; display: block; margin-top: 10px;")
                        html.A("{{ estimasi_text }}", href=("estimasi_url", "#"), target="_blank",
                               style="color: blue; text-decoration: underline; display: block;")


def buka_browser(ip, port=80):
    if port == 80:
        url = f"http://{ip}"
    else:
        url = f"http://{ip}:{port}"

    webbrowser.open(url)


if __name__ == "__main__":
    try:
        print("Akses melalui web browser dari PC lain dengan link berikut:")


        def dapatkan_ip_lokal():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except Exception:
                IP = '127.0.0.1'
            finally:
                s.close()
            return IP


        ip_lokal = dapatkan_ip_lokal()
        daftar_ip = [ip_lokal]

        if daftar_ip and ip_lokal != '127.0.0.1':
            for ip in daftar_ip:
                if cfg.hostportv3 == 80:
                    print(f" -> http://{ip}")
                    threading.Timer(1.5, buka_browser, args=(ip,)).start()
                else:
                    print(f" -> http://{ip}:{cfg.hostportv3}")
                    threading.Timer(1.5, buka_browser, args=(ip, cfg.hostportv3)).start()
        elif ip_lokal == '127.0.0.1':
            print(" -> Perangkat tidak terhubung ke jaringan (Offline). Menggunakan localhost.")
            if cfg.hostportv3 == 80:
                print(f" -> http://127.0.0.1")
                threading.Timer(1.5, buka_browser, args=('127.0.0.1',)).start()
            else:
                print(f" -> http://127.0.0.1:{cfg.hostportv3}")
                threading.Timer(1.5, buka_browser, args=('127.0.0.1', cfg.hostportv3)).start()

        server.start(host="0.0.0.0", port=cfg.hostportv3, argv=[])

    except Exception as e:
        print(f"Terjadi error: {e}")
        raise ValueError(f"Terjadi error: {e}")
