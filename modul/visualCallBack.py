import webbrowser

def make_callback(plotter, latitude, longitude, radiusBaris, radiusKolom, barisMatriks, kolomMatriks,matrikFAaslicallback):
    lastTextActor = [None]  # supaya bisa diubah di dalam fungsi nested
    open_map_flag = [False]  # flag untuk menandai apakah tombol 'm' ditekan

    def on_key_press(key):
        if key.lower() == 'm':
            open_map_flag[0] = True
            print("Tombol 'm' ditekan: Siap membuka Google Maps pada klik berikutnya.")

    plotter.add_key_event('m', lambda: on_key_press('m'))

    def callback(point, idx):
        kolomKlik = point[0] - radiusKolom
        barisKlik = point[1] - radiusBaris
        ketinggianKlik = point[2]

        print(f"point: {point}")

        if lastTextActor[0] is not None:
            plotter.remove_actor(lastTextActor[0])
        barisKonversi = barisMatriks - barisKlik
        kolomKonversi = kolomMatriks + kolomKlik

        FAKlik = matrikFAaslicallback[int(round(point[1])), int(round(point[0]))]
        print("pyvista==================================")
        from modul import mapping
        latitudePoint, longitudePoint = mapping.MappingBarisKolomMatrikKeLatLong(
            barisKonversi, kolomKonversi, latitude, longitude)
        print("pyvista end ==================================")
        lastTextActor[0] = plotter.add_text(
            f"barisKlik : {round(point[1] )}, kolomKlik : {round(point[0]) }, latitude: {latitudePoint}, longitude: {longitudePoint}, altitude : {round(ketinggianKlik)} meter(s), FA : {round(FAKlik)}",
            font_size=12, position="upper_left", color="red"
        )

        if open_map_flag[0]:
            google_maps_url = f"https://www.google.com/maps?q={latitudePoint},{longitudePoint}"
            webbrowser.open(google_maps_url)
            open_map_flag[0] = False  # reset setelah membuka link
            print(google_maps_url)
    return callback
