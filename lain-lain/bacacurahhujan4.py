import pandas as pd

# Ganti dengan path file Excel kamu
file_path = r"D:\Agung\penelitian\data curah hujan dari website\1 2022.xlsx"

# Baca file Excel
df = pd.read_excel(file_path)

# Pastikan kolom "Tanggal" ada
if "Tanggal" not in df.columns:
    raise ValueError("Kolom 'Tanggal' tidak ditemukan di file Excel!")

# Ubah kolom Tanggal ke datetime
df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

# Cek apakah ada tanggal yang gagal diparse
if df["Tanggal"].isna().any():
    print("⚠️ Ada tanggal yang tidak bisa diparse:")
    print(df[df["Tanggal"].isna()])

# Cek duplikat sebelum set_index
dupes = df[df.duplicated("Tanggal", keep=False)]
if not dupes.empty:
    print("⚠️ Ada duplikat tanggal:")
    print(dupes)

# Kalau tidak ada masalah, lanjut proses
if dupes.empty and not df["Tanggal"].isna().any():
    start, end = df["Tanggal"].min(), df["Tanggal"].max()
    date_range = pd.date_range(start=start, end=end, freq="D")

    df = df.set_index("Tanggal").reindex(date_range).reset_index()
    df = df.rename(columns={"index": "Tanggal"})

    print("✅ Data setelah reindex:")
    print(df.head(20))
