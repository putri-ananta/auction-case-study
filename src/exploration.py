import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Dummy_Kinerja_Lelang.xlsx"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "kinerja_lelang_analisis_ready.csv"
SHEET_NAME = "RAW Kinerja Lelang"


def kategori_aset(text):
    text = str(text).lower()
    if "tanah" in text:
        return "Tanah/Bangunan"
    if "kendaraan roda empat" in text:
        return "Kendaraan Roda 4"
    if "kendaraan roda dua" in text:
        return "Kendaraan Roda 2"
    if "barang inventaris" in text:
        return "Barang Inventaris"
    return "Lainnya"


df = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)

date_cols = ["tgl_penetapan", "tgl_penayangan", "tgl_lelang", "tanggal_pelunasan"]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")

df["hari_penetapan_tayang"] = (
    df["tgl_penayangan"] - df["tgl_penetapan"]
).dt.total_seconds() / 86400
df["hari_tayang_lelang"] = (
    df["tgl_lelang"] - df["tgl_penayangan"]
).dt.total_seconds() / 86400
df["hari_penetapan_lelang"] = (
    df["tgl_lelang"] - df["tgl_penetapan"]
).dt.total_seconds() / 86400

df["kategori_aset"] = df["nama_lot"].apply(kategori_aset)
df["status_plot"] = df["status_lelang"].fillna("Belum Ada Status")
df["bulan_lelang"] = df["tgl_lelang"].dt.to_period("M").astype(str)

df.to_csv(OUTPUT_PATH, index=False)

print(f"Jumlah data: {len(df):,} baris")
print(f"Jumlah kolom hasil olahan: {len(df.columns)}")
print(f"Data hasil olahan tersimpan di: {OUTPUT_PATH}")
print("\nDistribusi status:")
print(df["status_plot"].value_counts())

