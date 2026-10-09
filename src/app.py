from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Dashboard Kinerja Lelang", layout="wide")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Dummy_Kinerja_Lelang.xlsx"
SHEET_NAME = "RAW Kinerja Lelang"
DATE_COLS = ["tgl_penetapan", "tgl_penayangan", "tgl_lelang", "tanggal_pelunasan"]
BEA_COLS = ["bea_permohonan", "bea_batal", "bea_lelang_pembeli", "bea_lelang_penjual"]
STAKEHOLDER_JENIS_LELANG = {
    "Pasal 6 Undang-Undang Hak Tanggungan": "perbankan, lembaga pembiayaan, dan kreditur pemegang hak tanggungan",
    "Harta Pailit": "kurator dan Pengadilan Niaga",
    "Benda Sitaan Pajak": "Direktorat Jenderal Pajak dan instansi pemungut pajak",
    "Benda Sitaan Pengadilan": "pengadilan dan aparat penegak hukum",
    "Barang Rampasan": "Kejaksaan dan aparat penegak hukum",
    "Barang Gratifikasi": "Komisi Pemberantasan Korupsi dan instansi terkait",
    "Barang Milik Negara/Daerah": "kementerian, lembaga, dan pemerintah daerah",
    "Barang Milik Perorangan / Badan Usaha Swasta": "pemilik aset, perusahaan swasta, dan asosiasi usaha",
    "BUMN/BUMD berbentuk Persero": "BUMN/BUMD berbentuk Persero dan pembina perusahaan",
    "BUMN/D NON PERSERO": "BUMN/BUMD non-Persero dan instansi pembinanya",
}


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


def format_rupiah_ringkas(value):
    def format_angka(angka):
        return f"{angka:,.1f}".replace(",", "_").replace(".", ",").replace("_", ".")

    if value >= 1_000_000_000:
        return f"Rp{format_angka(value / 1_000_000_000)} miliar"
    return f"Rp{format_angka(value / 1_000_000)} juta"


def tambah_tombol_urut_kategori(
    fig, axis, urutan_ascending, urutan_descending, default="descending"
):
    axis_key = f"{axis}axis"
    urutan_awal = urutan_descending if default == "descending" else urutan_ascending
    urutan_lawan = urutan_ascending if default == "descending" else urutan_descending

    if axis == "y":
        fig.update_yaxes(categoryorder="array", categoryarray=urutan_awal)
    else:
        fig.update_xaxes(categoryorder="array", categoryarray=urutan_awal)

    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 1,
                "xanchor": "right",
                "y": 1.10,
                "yanchor": "bottom",
                "showactive": True,
                "active": 0,
                "buttons": [
                    {
                        "label": "↕",
                        "method": "relayout",
                        "args": [
                            {
                                f"{axis_key}.categoryorder": "array",
                                f"{axis_key}.categoryarray": urutan_awal,
                            }
                        ],
                        "args2": [
                            {
                                f"{axis_key}.categoryorder": "array",
                                f"{axis_key}.categoryarray": urutan_lawan,
                            }
                        ],
                    },
                ],
            }
        ],
        margin={"t": 90},
    )


def tambah_tombol_urut_numerik(fig, axis="x", default="ascending"):
    axis_key = f"{axis}axis"
    autorange_awal = True if default == "ascending" else "reversed"
    autorange_lawan = "reversed" if default == "ascending" else True

    if axis == "x":
        fig.update_xaxes(autorange=autorange_awal)
    else:
        fig.update_yaxes(autorange=autorange_awal)

    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 1,
                "xanchor": "right",
                "y": 1.10,
                "yanchor": "bottom",
                "showactive": True,
                "active": 0,
                "buttons": [
                    {
                        "label": "↕",
                        "method": "relayout",
                        "args": [{f"{axis_key}.autorange": autorange_awal}],
                        "args2": [{f"{axis_key}.autorange": autorange_lawan}],
                    },
                ],
            }
        ],
        margin={"t": 90},
    )


def tambah_tombol_ganti_data_kategori(
    fig, fig_alternatif, axis, urutan_awal, urutan_alternatif
):
    axis_key = f"{axis}axis"
    data_awal = {
        "x": [trace.x for trace in fig.data],
        "y": [trace.y for trace in fig.data],
    }
    data_alternatif = {
        "x": [trace.x for trace in fig_alternatif.data],
        "y": [trace.y for trace in fig_alternatif.data],
    }

    if axis == "y":
        fig.update_yaxes(categoryorder="array", categoryarray=urutan_awal)
    else:
        fig.update_xaxes(categoryorder="array", categoryarray=urutan_awal)

    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 1,
                "xanchor": "right",
                "y": 1.10,
                "yanchor": "bottom",
                "showactive": True,
                "active": 0,
                "buttons": [
                    {
                        "label": "↕",
                        "method": "update",
                        "args": [
                            data_awal,
                            {
                                f"{axis_key}.categoryorder": "array",
                                f"{axis_key}.categoryarray": urutan_awal,
                            },
                        ],
                        "args2": [
                            data_alternatif,
                            {
                                f"{axis_key}.categoryorder": "array",
                                f"{axis_key}.categoryarray": urutan_alternatif,
                            },
                        ],
                    }
                ],
            }
        ],
        margin={"t": 90},
    )


@st.cache_data
def load_data():
    data = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)
    for col in DATE_COLS:
        data[col] = pd.to_datetime(data[col], errors="coerce")

    data["hari_penetapan_tayang"] = (
        data["tgl_penayangan"] - data["tgl_penetapan"]
    ).dt.total_seconds() / 86400
    data["hari_tayang_lelang"] = (
        data["tgl_lelang"] - data["tgl_penayangan"]
    ).dt.total_seconds() / 86400
    data["hari_penetapan_lelang"] = (
        data["tgl_lelang"] - data["tgl_penetapan"]
    ).dt.total_seconds() / 86400

    data["kategori_aset"] = data["nama_lot"].apply(kategori_aset)
    data["status_plot"] = data["status_lelang"].fillna("Belum Ada Status")
    data["bulan_lelang"] = data["tgl_lelang"].dt.to_period("M").astype(str)
    return data


df = load_data()

st.title("Dashboard Kinerja Lelang")

st.sidebar.header("Filter")
selected_kanwil = st.sidebar.multiselect(
    "Kanwil", sorted(df["kanwil"].dropna().unique())
)

kpknl_options = df
if selected_kanwil:
    kpknl_options = kpknl_options[kpknl_options["kanwil"].isin(selected_kanwil)]
selected_kpknl = st.sidebar.multiselect(
    "KPKNL", sorted(kpknl_options["kpknl"].dropna().unique())
)

selected_jenis = st.sidebar.multiselect(
    "Jenis lelang", sorted(df["jenis_lelang"].dropna().unique())
)

min_date = df["tgl_lelang"].min().date()
max_date = df["tgl_lelang"].max().date()
selected_dates = st.sidebar.date_input(
    "Tanggal lelang", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

filtered = df.copy()
if selected_kanwil:
    filtered = filtered[filtered["kanwil"].isin(selected_kanwil)]
if selected_kpknl:
    filtered = filtered[filtered["kpknl"].isin(selected_kpknl)]
if selected_jenis:
    filtered = filtered[filtered["jenis_lelang"].isin(selected_jenis)]
if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered = filtered[
        filtered["tgl_lelang"].dt.date.between(start_date, end_date)
    ]

if filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini.")
    st.stop()

total_lot = len(filtered)
total_limit = filtered["nilai_limit"].sum()
lot_laku = (filtered["status_lelang"] == "LAKU").sum()
proporsi_laku = lot_laku / total_lot
total_bea = filtered[BEA_COLS].fillna(0).sum().sum()

st.subheader("1. Ringkasan KPI")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Lot", f"{total_lot:,}")
col2.metric("Total Nilai Limit", format_rupiah_ringkas(total_limit))
col3.metric("Lot berstatus LAKU", f"{lot_laku:,} ({proporsi_laku:.1%})")
col4.metric("Total Bea", format_rupiah_ringkas(total_bea))

overview_tab, wilayah_tab, proses_tab, detail_tab = st.tabs(
    ["Overview", "Konfirmasi Status", "Waktu & Nilai", "Detail"]
)

with overview_tab:
    kpknl_total_semua = (
        filtered.groupby("kpknl")
        .size()
        .reset_index(name="jumlah_lot")
    )
    kpknl_total_terbesar = kpknl_total_semua.nlargest(10, "jumlah_lot")
    kpknl_total_terkecil = kpknl_total_semua.nsmallest(10, "jumlah_lot")
    top_10_kpknl = kpknl_total_terbesar["kpknl"].tolist()
    bottom_10_kpknl = kpknl_total_terkecil["kpknl"].tolist()

    kpknl_order_terbesar = (
        kpknl_total_terbesar
        .sort_values(["jumlah_lot", "kpknl"], ascending=[True, False])["kpknl"]
        .tolist()
    )
    kpknl_order_terkecil = (
        kpknl_total_terkecil
        .sort_values(["jumlah_lot", "kpknl"], ascending=[False, False])["kpknl"]
        .tolist()
    )

    def buat_data_kpknl_laku(daftar_kpknl):
        return (
            filtered[filtered["kpknl"].isin(daftar_kpknl)]
            .groupby("kpknl")
            .agg(
                seluruh_lot=("kode_lot", "size"),
                status_laku=("status_lelang", lambda x: (x == "LAKU").sum()),
            )
            .reset_index()
            .melt(
                id_vars="kpknl",
                value_vars=["seluruh_lot", "status_laku"],
                var_name="kelompok",
                value_name="jumlah_lot",
            )
        )

    def buat_data_kpknl_status(daftar_kpknl):
        status_list = sorted(filtered["status_plot"].dropna().unique())
        index_lengkap = pd.MultiIndex.from_product(
            [daftar_kpknl, status_list], names=["kpknl", "status_plot"]
        )
        return (
            filtered[filtered["kpknl"].isin(daftar_kpknl)]
            .groupby(["kpknl", "status_plot"])
            .size()
            .reindex(index_lengkap, fill_value=0)
            .reset_index(name="jumlah_lot")
        )

    kpknl_laku = buat_data_kpknl_laku(top_10_kpknl)
    kpknl_laku_terkecil = buat_data_kpknl_laku(bottom_10_kpknl)
    for data_laku in [kpknl_laku, kpknl_laku_terkecil]:
        data_laku["kelompok"] = data_laku["kelompok"].map(
            {"seluruh_lot": "Seluruh lot", "status_laku": "Status LAKU"}
        )

    kpknl_status = buat_data_kpknl_status(top_10_kpknl)
    kpknl_status_terkecil = buat_data_kpknl_status(bottom_10_kpknl)
    fig_kpknl_laku = px.bar(
        kpknl_laku,
        x="jumlah_lot",
        y="kpknl",
        color="kelompok",
        orientation="h",
        barmode="group",
        title="Komposisi LAKU menurut KPKNL",
        labels={
            "jumlah_lot": "Jumlah Lot",
            "kpknl": "KPKNL",
            "kelompok": "Keterangan",
        },
        color_discrete_map={"Seluruh lot": "#1976D2", "Status LAKU": "#168C78"},
        height=520,
    )
    fig_kpknl_laku_terkecil = px.bar(
        kpknl_laku_terkecil,
        x="jumlah_lot",
        y="kpknl",
        color="kelompok",
        orientation="h",
        barmode="group",
        color_discrete_map={"Seluruh lot": "#1976D2", "Status LAKU": "#168C78"},
    )
    tambah_tombol_ganti_data_kategori(
        fig_kpknl_laku,
        fig_kpknl_laku_terkecil,
        "y",
        urutan_awal=kpknl_order_terbesar,
        urutan_alternatif=kpknl_order_terkecil,
    )

    fig_kpknl_status = px.bar(
        kpknl_status,
        x="jumlah_lot",
        y="kpknl",
        color="status_plot",
        orientation="h",
        title="Komposisi Status menurut KPKNL",
        labels={
            "jumlah_lot": "Jumlah Lot",
            "kpknl": "KPKNL",
            "status_plot": "Status",
        },
        height=520,
    )
    fig_kpknl_status_terkecil = px.bar(
        kpknl_status_terkecil,
        x="jumlah_lot",
        y="kpknl",
        color="status_plot",
        orientation="h",
    )
    tambah_tombol_ganti_data_kategori(
        fig_kpknl_status,
        fig_kpknl_status_terkecil,
        "y",
        urutan_awal=kpknl_order_terbesar,
        urutan_alternatif=kpknl_order_terkecil,
    )

    kpknl_laku_col, kpknl_status_col = st.columns(2)
    kpknl_laku_col.plotly_chart(fig_kpknl_laku, width="stretch")
    kpknl_status_col.plotly_chart(fig_kpknl_status, width="stretch")

    left, right = st.columns(2)

    status = (
        filtered["status_plot"]
        .value_counts()
        .rename_axis("status")
        .reset_index(name="jumlah_lot")
        .sort_values("jumlah_lot")
    )
    fig_status = px.bar(
        status,
        x="jumlah_lot",
        y="status",
        orientation="h",
        title="Komposisi Status Lelang",
        labels={"jumlah_lot": "Jumlah Lot", "status": "Status"},
    )
    status_order = status["status"].tolist()
    tambah_tombol_urut_kategori(
        fig_status,
        "y",
        urutan_ascending=list(reversed(status_order)),
        urutan_descending=status_order,
    )
    left.plotly_chart(fig_status, width="stretch")

    laku_kpknl_semua = (
        filtered.groupby("kpknl")["status_lelang"]
        .apply(lambda x: (x == "LAKU").sum())
        .reset_index(name="jumlah_laku")
    )
    laku_kpknl_terbesar = laku_kpknl_semua.nlargest(10, "jumlah_laku").sort_values(
        ["jumlah_laku", "kpknl"], ascending=[True, False]
    )
    laku_kpknl_terkecil = laku_kpknl_semua.nsmallest(10, "jumlah_laku").sort_values(
        ["jumlah_laku", "kpknl"], ascending=[False, False]
    )
    laku_kpknl_order_terbesar = laku_kpknl_terbesar["kpknl"].tolist()
    laku_kpknl_order_terkecil = laku_kpknl_terkecil["kpknl"].tolist()
    fig_jumlah_laku = px.bar(
        laku_kpknl_terbesar,
        x="jumlah_laku",
        y="kpknl",
        orientation="h",
        title="Jumlah LAKU menurut KPKNL",
        labels={"jumlah_laku": "Jumlah LAKU", "kpknl": "KPKNL"},
        color_discrete_sequence=["#168C78"],
    )
    fig_jumlah_laku_terkecil = px.bar(
        laku_kpknl_terkecil,
        x="jumlah_laku",
        y="kpknl",
        orientation="h",
        color_discrete_sequence=["#168C78"],
    )
    tambah_tombol_ganti_data_kategori(
        fig_jumlah_laku,
        fig_jumlah_laku_terkecil,
        "y",
        urutan_awal=laku_kpknl_order_terbesar,
        urutan_alternatif=laku_kpknl_order_terkecil,
    )
    right.plotly_chart(fig_jumlah_laku, width="stretch")

    jenis_status = (
        filtered.groupby(["jenis_lelang", "status_plot"])
        .size()
        .reset_index(name="jumlah_lot")
    )
    jenis_order = (
        filtered.groupby("jenis_lelang")
        .size()
        .reset_index(name="jumlah_lot")
        .sort_values(["jumlah_lot", "jenis_lelang"], ascending=[True, False])["jenis_lelang"]
        .tolist()
    )
    fig_jenis = px.bar(
        jenis_status,
        x="jumlah_lot",
        y="jenis_lelang",
        color="status_plot",
        orientation="h",
        title="Komposisi Status menurut Jenis Lelang",
        labels={
            "jumlah_lot": "Jumlah Lot",
            "jenis_lelang": "Jenis Lelang",
            "status_plot": "Status",
        },
    )
    tambah_tombol_urut_kategori(
        fig_jenis,
        "y",
        urutan_ascending=list(reversed(jenis_order)),
        urutan_descending=jenis_order,
    )
    st.plotly_chart(fig_jenis, width="stretch")

with wilayah_tab:
    wilayah = (
        filtered.groupby(["kanwil", "kpknl"])
        .agg(
            jumlah_lot=("kode_lot", "size"),
            lot_laku=("status_lelang", lambda x: (x == "LAKU").sum()),
            tap=("status_lelang", lambda x: (x == "TAP").sum()),
            batal=("status_lelang", lambda x: (x == "BATAL").sum()),
            wanprestasi=("status_lelang", lambda x: (x == "WANPRESTASI").sum()),
            status_kosong=("status_lelang", lambda x: x.isna().sum()),
            nilai_limit=("nilai_limit", "sum"),
        )
        .reset_index()
    )
    wilayah["perlu_follow_up"] = wilayah["status_kosong"]
    wilayah["proporsi_follow_up"] = wilayah["perlu_follow_up"] / wilayah["jumlah_lot"]

    top_wilayah = wilayah.nlargest(15, "perlu_follow_up").sort_values(
        ["perlu_follow_up", "kpknl"], ascending=[True, False]
    )
    fig_wilayah = px.bar(
        top_wilayah,
        x="perlu_follow_up",
        y="kpknl",
        color="kanwil",
        orientation="h",
        title="15 KPKNL dengan Status Kosong Terbanyak",
        labels={"perlu_follow_up": "Status Kosong", "kpknl": "KPKNL", "kanwil": "Kanwil"},
    )
    wilayah_order = top_wilayah["kpknl"].tolist()
    tambah_tombol_urut_kategori(
        fig_wilayah,
        "y",
        urutan_ascending=list(reversed(wilayah_order)),
        urutan_descending=wilayah_order,
    )
    st.plotly_chart(fig_wilayah, width="stretch")

    st.dataframe(
        wilayah.sort_values("perlu_follow_up", ascending=False)[
            [
                "kanwil",
                "kpknl",
                "jumlah_lot",
                "lot_laku",
                "tap",
                "batal",
                "wanprestasi",
                "status_kosong",
                "proporsi_follow_up",
                "nilai_limit",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "kanwil": "Kanwil",
            "kpknl": "KPKNL",
            "jumlah_lot": "Jumlah Lot",
            "lot_laku": "LAKU",
            "tap": "TAP",
            "batal": "BATAL",
            "wanprestasi": "WANPRESTASI",
            "status_kosong": "Perlu Follow-up (Status Kosong)",
            "nilai_limit": st.column_config.NumberColumn("Nilai Limit", format="Rp %.0f"),
            "proporsi_follow_up": st.column_config.NumberColumn("Proporsi Follow-up", format="%.1%%"),
        },
    )

with proses_tab:
    trend = (
        filtered.groupby("bulan_lelang")
        .size()
        .reset_index(name="jumlah_lot")
        .sort_values("bulan_lelang")
    )
    fig_trend = px.line(
        trend,
        x="bulan_lelang",
        y="jumlah_lot",
        markers=True,
        title="Volume Lelang per Bulan",
        labels={"bulan_lelang": "Bulan Lelang", "jumlah_lot": "Jumlah Lot"},
    )
    bulan_order = trend["bulan_lelang"].tolist()
    tambah_tombol_urut_kategori(
        fig_trend,
        "x",
        urutan_ascending=bulan_order,
        urutan_descending=list(reversed(bulan_order)),
        default="ascending",
    )
    st.plotly_chart(fig_trend, width="stretch")

    left, right = st.columns(2)
    fig_nilai = px.histogram(
        filtered,
        x="nilai_limit",
        nbins=30,
        title="Sebaran Nilai Limit",
        labels={"nilai_limit": "Nilai Limit", "count": "Jumlah Lot"},
    )
    tambah_tombol_urut_numerik(fig_nilai, axis="x", default="ascending")
    left.plotly_chart(fig_nilai, width="stretch")

    fig_durasi = px.box(
        filtered,
        x="kategori_aset",
        y="hari_penetapan_lelang",
        title="Durasi Penetapan sampai Lelang menurut Kategori Aset",
        labels={
            "kategori_aset": "Kategori Aset",
            "hari_penetapan_lelang": "Durasi (hari)",
        },
    )
    kategori_order = (
        filtered.groupby("kategori_aset")["hari_penetapan_lelang"]
        .median()
        .sort_values(ascending=True)
        .index.tolist()
    )
    tambah_tombol_urut_kategori(
        fig_durasi,
        "x",
        urutan_ascending=kategori_order,
        urutan_descending=list(reversed(kategori_order)),
        default="ascending",
    )
    right.plotly_chart(fig_durasi, width="stretch")

with detail_tab:
    show_cols = [
        "kanwil",
        "kpknl",
        "kode_lot",
        "nama_lot",
        "jenis_lelang",
        "kategori_aset",
        "nilai_limit",
        "status_plot",
        "tgl_lelang",
        "hari_penetapan_lelang",
    ]
    st.dataframe(
        filtered[show_cols].sort_values("tgl_lelang"),
        width="stretch",
        hide_index=True,
    )

st.subheader("2. Insight dan Rekomendasi")

ringkasan_kpknl = (
    filtered.groupby(["kanwil", "kpknl"])
    .agg(
        jumlah_lot=("kode_lot", "size"),
        laku=("status_lelang", lambda x: (x == "LAKU").sum()),
    )
    .reset_index()
)
ringkasan_kpknl["proporsi_laku"] = (
    ringkasan_kpknl["laku"] / ringkasan_kpknl["jumlah_lot"]
)
laku_terendah = ringkasan_kpknl.sort_values(
    ["proporsi_laku", "jumlah_lot", "kpknl"],
    ascending=[True, False, True],
).iloc[0]
volume_terendah = ringkasan_kpknl.sort_values(
    ["jumlah_lot", "kpknl"], ascending=[True, True]
).iloc[0]
jenis_terbanyak = filtered["jenis_lelang"].value_counts().index[0]
jumlah_jenis_terbanyak = int((filtered["jenis_lelang"] == jenis_terbanyak).sum())
proporsi_jenis_terbanyak = jumlah_jenis_terbanyak / total_lot
stakeholder_jenis = STAKEHOLDER_JENIS_LELANG.get(
    jenis_terbanyak, "pemohon dan instansi yang terkait dengan jenis lelang tersebut"
)

st.markdown("### Tiga prioritas pembahasan")
priority_1, priority_2, priority_3 = st.columns(3)

with priority_1.container(border=True):
    st.markdown("#### Prioritas 1 - Tingkatkan LAKU")
    st.markdown("**TEMUAN**")
    st.write(
        f"{laku_terendah['kpknl']} memiliki proporsi observasi LAKU terendah, "
        f"yaitu {laku_terendah['proporsi_laku']:.1%} "
        f"({int(laku_terendah['laku']):,} dari {int(laku_terendah['jumlah_lot']):,} lot)."
    )
    st.markdown("**MAKNA**")
    st.write(
        "LAKU merupakan hasil yang ingin ditingkatkan. Proporsi yang rendah menunjukkan "
        "perlunya evaluasi daya tarik lot dan jangkauan calon pembeli."
    )
    st.markdown("**REKOMENDASI**")
    st.write(
        "Perkuat promosi lelang, perluas kanal publikasi, dan evaluasi informasi aset "
        "serta nilai limit agar lebih menarik bagi calon peserta."
    )

with priority_2.container(border=True):
    st.markdown("#### Prioritas 2 - Gali Potensi")
    st.markdown("**TEMUAN**")
    st.write(
        f"{volume_terendah['kpknl']} memiliki volume lelang paling sedikit dalam hasil "
        f"filter, yaitu {int(volume_terendah['jumlah_lot']):,} lot."
    )
    st.markdown("**MAKNA**")
    st.write(
        "Volume yang rendah dapat menunjukkan potensi objek atau pemohon lelang yang "
        "belum tergali secara optimal."
    )
    st.markdown("**REKOMENDASI**")
    st.write(
        "Lakukan penggalian potensi lelang melalui pemetaan calon pemohon, koordinasi "
        "dengan pemangku kepentingan, dan sosialisasi layanan lelang."
    )

with priority_3.container(border=True):
    st.markdown("#### Prioritas 3 - Perkuat Stakeholder")
    st.markdown("**TEMUAN**")
    st.write(
        f"Jenis lelang yang paling banyak dilakukan adalah {jenis_terbanyak}, yaitu "
        f"{jumlah_jenis_terbanyak:,} lot ({proporsi_jenis_terbanyak:.1%} dari hasil filter)."
    )
    st.markdown("**MAKNA**")
    st.write(
        "Volume yang tinggi menunjukkan jenis lelang tersebut paling banyak diajukan "
        "dan memiliki basis pemohon yang perlu dijaga serta dikembangkan."
    )
    st.markdown("**REKOMENDASI**")
    st.write(
        f"Perkuat hubungan, koordinasi, dan sosialisasi layanan dengan {stakeholder_jenis} "
        f"untuk menjaga dan meningkatkan potensi lelang {jenis_terbanyak}."
    )
