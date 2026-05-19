import pandas as pd
import os

# === 1. Path folder & file input ===
folder = r"D:\Agung\penelitian\data aws\AWS STAKLIM JAWA TIMUR\Data Perjam\Perjam 2022\hasil"   # ganti sesuai lokasi file Anda
files = {
    "2022": os.path.join(folder, "curah_hujan_maksimal_harian_2022.csv"),
    "2023": os.path.join(folder, "curah_hujan_maksimal_harian_2023.csv"),
    "2024": os.path.join(folder, "curah_hujan_maksimal_harian_2024.csv"),
    "2025": os.path.join(folder, "curah_hujan_maksimal_harian_2025.csv"),
}

# === 2. Baca & rapikan setiap file ===
dfs = []
for year, path in files.items():
    df = pd.read_csv(path, delimiter=";")  # otomatis baca pakai ; sebagai pemisah
    # pastikan kolom datetime benar
    print("Daftar kolom di CSV:", df.columns.tolist())

    df["Tanggal_Harian"] = pd.to_datetime(df["Tanggal_Harian"], errors="coerce")
    df = df.dropna(subset=["Tanggal_Harian"])
    # ambil bulan-hari (MM-DD) saja agar bisa dibandingkan antar tahun
    df["Tanggal"] = df["Tanggal_Harian"].dt.strftime("%m-%d")
    # ambil kolom penting & rename jadi sesuai tahun
    df = df[["Tanggal", "Curah_Hujan_Maks_mm_per_jam"]].rename(
        columns={"Curah_Hujan_Maks_mm_per_jam": year}
    )
    dfs.append(df)

# === 3. Gabungkan berdasarkan Tanggal (MM-DD) ===
df_final = dfs[0]
for d in dfs[1:]:
    df_final = pd.merge(df_final, d, on="Tanggal", how="outer")

# === 4. Urutkan berdasarkan bulan-hari ===
df_final["Tanggal_dt"] = pd.to_datetime("2000-" + df_final["Tanggal"], format="%Y-%m-%d")
df_final = df_final.sort_values("Tanggal_dt").drop(columns=["Tanggal_dt"])

# === 5. Simpan ke Excel ===
output_path = os.path.join(folder, "curah_hujan_maksimal_transpose.xlsx")
df_final.to_excel(output_path, index=False)

print("File hasil disimpan di:", output_path)
