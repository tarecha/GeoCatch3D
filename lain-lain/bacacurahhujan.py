import pandas as pd
import numpy as np
from openpyxl import Workbook

# Path file input & output
file_path = r"D:\Agung\penelitian\data curah hujan dari website\compile semua data.xlsx"
output_path = r"D:\Agung\penelitian\data curah hujan dari website\rangkuman_curah_hujan2.xlsx"

# Baca semua sheet dari file excel
xls = pd.ExcelFile(file_path)
summary = {}

for sheet_name in xls.sheet_names:
    # Ambil 2 kolom pertama (Tanggal & RR)
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.iloc[:, :2]
    df.columns = ["Tanggal", "RR"]

    # Konversi tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce", dayfirst=True)

    # Deteksi nilai tidak valid
    invalid_mask = df["RR"].isin([8888, 9999, "-", " "]) | df["RR"].isna()

    # Bersihkan RR → ubah ke numeric
    df["RR"] = pd.to_numeric(df["RR"], errors="coerce")
    df.loc[df["RR"].isin([8888, 9999]), "RR"] = np.nan

    # Buat kolom bulan
    df["Bulan"] = df["Tanggal"].dt.to_period("M")

    # Hitung ringkasan
    def monthly_summary(g):
        if g["RR"].notna().any() and (g["RR"] > 0).any():
            maks_rr = g.loc[g["RR"] > 0, "RR"].max()
            tanggal_maks = g.loc[g["RR"] == maks_rr, "Tanggal"].iloc[0]
        else:
            maks_rr = np.nan
            tanggal_maks = pd.NaT

        return pd.Series({
            "Rata2_RR": g.loc[g["RR"] > 0, "RR"].mean(),
            "Hari_Hujan": (g["RR"] > 0).sum(),
            "Hari_Tidak_Hujan": (g["RR"] == 0).sum(),
            "Hari_Tidak_Valid": invalid_mask[g.index].sum(),
            "Maks_RR": maks_rr,
            "Tanggal_Maks_RR": tanggal_maks
        })

    grouped = df.groupby("Bulan", group_keys=False)[["Tanggal", "RR"]].apply(monthly_summary)

    summary[sheet_name] = grouped

# === Simpan ke Excel ===
wb = Workbook()
wb.remove(wb.active)  # hapus sheet default

for year, df_summary in summary.items():
    ws = wb.create_sheet(title=str(year))
    ws.append([
        "Bulan", "Rata2_RR", "Hari_Hujan", "Hari_Tidak_Hujan",
        "Hari_Tidak_Valid", "Maks_RR", "Tanggal_Maks_RR"
    ])

    for idx, row in df_summary.reset_index().iterrows():
        ws.append([
            str(row["Bulan"]),
            None if pd.isna(row["Rata2_RR"]) else round(row["Rata2_RR"], 2),
            int(row["Hari_Hujan"]),
            int(row["Hari_Tidak_Hujan"]),
            int(row["Hari_Tidak_Valid"]),
            None if pd.isna(row["Maks_RR"]) else row["Maks_RR"],
            "" if pd.isna(row["Tanggal_Maks_RR"]) else row["Tanggal_Maks_RR"].strftime("%d-%m-%Y")
        ])

wb.save(output_path)
print(f"Hasil ringkasan berhasil disimpan di: {output_path}")
