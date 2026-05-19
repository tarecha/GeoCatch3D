import pandas as pd
import numpy as np
import glob
import os

# Folder tempat file Excel curah hujan disimpan
folder_path = r"D:\Agung\penelitian\data curah hujan dari website"   # ganti dengan path folder Anda

# Cari semua file Excel di folder
files = glob.glob(os.path.join(folder_path, "*.xlsx"))

all_data = []

for file_path in files:
    # --- baca & bersihkan data ---
    df_raw = pd.read_excel(file_path, sheet_name="Worksheet")

    # cari header "TANGGAL"
    start_idx = df_raw[df_raw.iloc[:, 0] == "TANGGAL"].index[0]
    df = pd.read_excel(file_path, sheet_name="Worksheet", skiprows=start_idx)

    df = df.iloc[:, :2]
    df.columns = ["Tanggal", "Curah_Hujan"]

    df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d-%m-%Y", errors="coerce")
    df["Curah_Hujan"] = pd.to_numeric(df["Curah_Hujan"], errors="coerce")
    df["Curah_Hujan"].replace([8888, 9999], np.nan, inplace=True)

    # Buat kalender lengkap
    if df["Tanggal"].notna().any():
        date_range = pd.date_range(start=df["Tanggal"].min(), end=df["Tanggal"].max(), freq="D")
        df = df.set_index("Tanggal").reindex(date_range).reset_index()
        df.columns = ["Tanggal", "Curah_Hujan"]

    # Tambahkan kolom nama file (biar tahu data dari stasiun mana)
    df["File"] = os.path.basename(file_path)

    all_data.append(df)

# Gabungkan semua data
data_all = pd.concat(all_data, ignore_index=True)

# Buat kolom Bulan
data_all["Bulan"] = data_all["Tanggal"].dt.to_period("M")

# --- Hitung statistik per file & per bulan ---
rata2_per_bulan = (
    data_all[(data_all["Curah_Hujan"].notna()) & (data_all["Curah_Hujan"] != 0)]
    .groupby(["File", "Bulan"])["Curah_Hujan"]
    .mean()
)

hari_tidak_hujan = (
    data_all[data_all["Curah_Hujan"] == 0]
    .groupby(["File", "Bulan"])["Curah_Hujan"]
    .count()
)

hari_hujan = (
    data_all[data_all["Curah_Hujan"] > 0]
    .groupby(["File", "Bulan"])["Curah_Hujan"]
    .count()
)

total_per_bulan = (
    data_all.groupby(["File", "Bulan"])["Curah_Hujan"]
    .sum(min_count=1)   # min_count=1 supaya kalau semua NaN → hasil tetap NaN
)

# Gabungkan ringkasan
ringkasan = pd.DataFrame({
    "Rata2_Curah_Hujan": rata2_per_bulan,
    "Hari_Tidak_Hujan": hari_tidak_hujan,
    "Hari_Hujan": hari_hujan,
    "Total_Curah_Hujan": total_per_bulan
}).reset_index()

print(ringkasan)
