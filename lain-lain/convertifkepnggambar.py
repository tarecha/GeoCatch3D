import os
from PIL import Image


def konversi_tif_ke_png(folder_path):
    # Pastikan folder yang dimasukkan benar-benar ada
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' tidak ditemukan.")
        return

    # Menghitung jumlah file yang berhasil dikonversi
    berhasil = 0

    # Mengambil semua file di dalam folder
    for filename in os.listdir(folder_path):
        # Mengecek apakah file berekstensi .tif atau .tiff (mengabaikan huruf besar/kecil)
        if filename.lower().endswith(('.tif', '.tiff')):
            # Path lengkap file asli (.tif)
            tif_path = os.path.join(folder_path, filename)

            # Membuat nama file baru dengan ekstensi .png
            nama_tanpa_ekstensi = os.path.splitext(filename)[0]
            png_filename = f"{nama_tanpa_ekstensi}.png"
            png_path = os.path.join(folder_path, png_filename)

            try:
                # Membuka gambar dan menyimpannya sebagai PNG
                with Image.open(tif_path) as img:
                    img.save(png_path, 'PNG')

                print(f"Sukses: {filename} -> {png_filename}")
                berhasil += 1
            except Exception as e:
                print(f"Gagal mengonversi {filename}. Error: {e}")

    print("-" * 30)
    print(f"Selesai! Total file berhasil dikonversi: {berhasil}")


# --- Cara Penggunaan ---
# Ganti string di bawah ini dengan path folder Anda.
# Contoh Windows: r"C:\Users\NamaKamu\Documents\Gambar"
# Contoh Mac/Linux: "/Users/NamaKamu/Documents/Gambar"

folder_path = r"D:\maps\temp\dataran rendah"

konversi_tif_ke_png(folder_path)