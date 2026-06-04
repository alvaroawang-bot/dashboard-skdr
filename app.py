import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard SKDR",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard SKDR")

file = st.file_uploader(
    "Upload File Excel",
    type=["xlsx"]
)

if file is not None:

    data = pd.read_excel(file)

    kolom_penyakit = data.columns[1:]

    data = data[
        data[kolom_penyakit].sum(axis=1) > 0
    ]

    data = data.dropna(subset=["MINGGU"])
    data = data.fillna(0)
    
    data = data[data["MINGGU"].notna()]

    st.dataframe(data.head(52), use_container_width=True)
    st.subheader("🏆 Top 5 Penyakit")

    total_penyakit = data.iloc[:, 1:].sum()

    st.write(total_penyakit.sort_values(ascending=False))

    top5 = total_penyakit.sort_values(
    ascending=False
    ).head(5)

    top5_df = top5.reset_index()
    top5_df.columns = ["Penyakit", "Jumlah Kasus"]

    st.bar_chart(
    top5_df.set_index("Penyakit")
    )
    penyakit = st.selectbox(
    "Pilih Penyakit",
    data.columns[1:]
    )

    total = data[penyakit].sum()
    rata = round(data[penyakit].mean(), 2)
    maks = data[penyakit].max()
    minggu_puncak = data.loc[
        data[penyakit].idxmax(),
        "MINGGU"
    ]
    mini = data[penyakit].min()

    ambang = rata * 1.5

    penduduk = st.number_input(
        "Jumlah Penduduk",
        min_value=1,
        value=116500
    )

    ir = round((total / penduduk) * 100000, 2)

    
    data_valid = data[data[penyakit].notna()]

    
    data_kasus = data[data[penyakit] > 0]

    minggu_ini = data_kasus[penyakit].iloc[-1]
    minggu_lalu = data_kasus[penyakit].iloc[-2]

    minggu_terakhir = data_kasus["MINGGU"].iloc[-1]
    minggu_sebelumnya = data_kasus["MINGGU"].iloc[-2]
    
    if minggu_lalu != 0:
        persen = round(
            ((minggu_ini - minggu_lalu) / minggu_lalu) * 100,
            2
        )
    else:
        persen = 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total", total)
    col2.metric("Rata-rata", rata)
    col3.metric("Tertinggi", maks)
    col4.metric("Terendah", mini)
    col5.metric("Perubahan", f"{persen}%")
    col6.metric("IR", ir)

    st.subheader(f"📈 Grafik Tren {penyakit}")

    fig = px.line(
    data,
    x="MINGGU",
    y=penyakit,
    markers=True,
    title=f"Tren Kasus {penyakit}"
    )

    st.plotly_chart(fig, use_container_width=True)

    if minggu_ini > minggu_lalu:
        st.warning("⚠️ Kasus meningkat dibanding minggu sebelumnya")
    elif minggu_ini < minggu_lalu:
        st.success("✅ Kasus menurun dibanding minggu sebelumnya")
    else:
        st.info("ℹ️ Kasus stabil dibanding minggu sebelumnya")

    # Early Warning System (EWS)
    if minggu_ini > ambang:
        st.error(
            f"🚨 ALERT SKDR: Kasus {penyakit} minggu ini ({minggu_ini}) "
            f"melebihi ambang kewaspadaan ({round(ambang,2)})"
        )
    st.subheader("📝 Narasi Otomatis")

    narasi = f"""
    Jumlah kasus {penyakit} selama periode pengamatan sebanyak {total} kasus.
    Rata-rata kasus per minggu sebesar {rata} kasus.
    Kasus tertinggi terjadi pada {minggu_puncak} sebanyak {maks} kasus.
    Pada minggu terakhir tercatat {minggu_ini} kasus, dibanding minggu sebelumnya sebanyak {minggu_lalu} kasus.
    """

    st.success(narasi)
    st.download_button(
    "📥 Download Narasi",
    narasi,
    "Narasi_SKDR.txt"
    )
