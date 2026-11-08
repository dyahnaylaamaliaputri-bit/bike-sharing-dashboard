import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

BASE = os.path.dirname(os.path.abspath(__file__))
BLUE, GREY, ORANGE = "#1F77B4", "#B0B7C3", "#E8743B"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
SEASONS = ["Spring", "Summer", "Fall", "Winter"]
WEATHERS = ["Cerah", "Berkabut/Mendung", "Hujan/Salju Ringan"]


@st.cache_data
def load_data():
    hour = pd.read_csv(os.path.join(BASE, "main_data.csv"), parse_dates=["dteday"])
    day = pd.read_csv(os.path.join(BASE, "day_data.csv"), parse_dates=["dteday"])
    return hour, day


hour_df, day_df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title("🚲 Filter Data")
min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", (min_d, max_d), min_value=min_d, max_value=max_d)
if len(date_range) != 2:
    st.sidebar.info("Pilih tanggal awal dan akhir.")
    st.stop()
start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

sel_weather = st.sidebar.multiselect("Kondisi cuaca (data harian)", WEATHERS, default=WEATHERS)
sel_season = st.sidebar.multiselect("Musim", SEASONS, default=SEASONS)

d = day_df[day_df["dteday"].between(start, end) & day_df["weather"].isin(sel_weather) & day_df["season"].isin(sel_season)]
h = hour_df[hour_df["dteday"].isin(d["dteday"])]

st.sidebar.caption("Sumber: Capital Bikeshare, Washington D.C. (2011-2012)")

if d.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ---------------- Header & KPI ----------------
st.title("🚲 Bike Sharing Dashboard")
st.caption("Ringkasan pola penyewaan sepeda: kapan, pada kondisi apa, dan seberapa cepat tumbuh.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total penyewaan", f"{d['cnt'].sum():,.0f}")
k2.metric("Rata-rata per hari", f"{d['cnt'].mean():,.0f}")
k3.metric("Pengguna registered", f"{d['registered'].sum() / d['cnt'].sum():.0%}")
k4.metric("Jumlah hari dianalisis", f"{len(d):,}")

tab1, tab2, tab3, tab4 = st.tabs(["⏰ Pola Jam", "🌦️ Cuaca & Musim", "📈 Pertumbuhan", "🧩 Segmentasi"])

# ---------------- Tab 1 ----------------
with tab1:
    st.subheader("Pada jam berapa penyewaan memuncak: hari kerja vs akhir pekan/libur?")
    hp = h.groupby(["hr", "day_type"], as_index=False)["cnt"].mean()
    fig = px.line(hp, x="hr", y="cnt", color="day_type", markers=True,
                  color_discrete_map={"Hari Kerja": BLUE, "Akhir Pekan/Libur": ORANGE},
                  labels={"hr": "Jam dalam sehari", "cnt": "Rata-rata penyewaan per jam", "day_type": ""})
    fig.update_layout(yaxis_rangemode="tozero", xaxis=dict(dtick=2), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, width="stretch")

    piv = hp.pivot(index="hr", columns="day_type", values="cnt")
    c1, c2 = st.columns(2)
    if "Hari Kerja" in piv:
        c1.metric("Puncak hari kerja", f"{piv['Hari Kerja'].idxmax():02d}:00", f"{piv['Hari Kerja'].max():.0f} sewa/jam")
    if "Akhir Pekan/Libur" in piv:
        c2.metric("Puncak akhir pekan/libur", f"{piv['Akhir Pekan/Libur'].idxmax():02d}:00", f"{piv['Akhir Pekan/Libur'].max():.0f} sewa/jam")
    st.info("**Insight:** hari kerja punya dua puncak komuter (08:00 dan 17:00), akhir pekan satu puncak landai di siang hari. "
            "**Aksi:** isi stok stasiun sebelum 07:00 dan 16:00 pada hari kerja, dan jadwalkan perawatan pukul 00:00-04:00.")

# ---------------- Tab 2 ----------------
with tab2:
    st.subheader("Seberapa besar cuaca dan musim memengaruhi penyewaan harian?")
    col_a, col_b = st.columns(2)

    w = d.groupby("weather", as_index=False)["cnt"].mean()
    w["weather"] = pd.Categorical(w["weather"], WEATHERS, ordered=True)
    w = w.sort_values("weather")
    base = w.loc[w["weather"] == "Cerah", "cnt"]
    w["label"] = [f"{v:,.0f}" if (wt == "Cerah" or base.empty) else f"{v:,.0f} ({v / base.iloc[0] - 1:+.0%})" for wt, v in zip(w["weather"], w["cnt"])]
    f1 = px.bar(w, x="weather", y="cnt", text="label", color="weather",
                color_discrete_map={"Cerah": BLUE, "Berkabut/Mendung": GREY, "Hujan/Salju Ringan": GREY},
                labels={"weather": "", "cnt": "Rata-rata penyewaan harian"})
    f1.update_layout(showlegend=False, title="Cuaca buruk menekan penyewaan")
    col_a.plotly_chart(f1, width="stretch")

    s = d.groupby("season", as_index=False)["cnt"].mean()
    s["season"] = pd.Categorical(s["season"], SEASONS, ordered=True)
    s = s.sort_values("season")
    s["color"] = [BLUE if v == s["cnt"].max() else (ORANGE if v == s["cnt"].min() else GREY) for v in s["cnt"]]
    f2 = px.bar(s, x="season", y="cnt", text=s["cnt"].round(0).map("{:,.0f}".format),
                labels={"season": "", "cnt": "Rata-rata penyewaan harian"})
    f2.update_traces(marker_color=s["color"])
    f2.update_layout(title="Rata-rata penyewaan per musim")
    col_b.plotly_chart(f2, width="stretch")

    st.info("**Insight:** pada seluruh data, cuaca berkabut menurunkan penyewaan ~17% dan hujan/salju ringan ~63% dibanding cuaca cerah. "
            "Fall tertinggi, Spring terendah. **Aksi:** kurangi armada aktif saat prakiraan hujan dan siapkan kapasitas maksimum saat cerah-hangat.")

# ---------------- Tab 3 ----------------
with tab3:
    st.subheader("Seberapa cepat penyewaan tumbuh dari 2011 ke 2012?")
    m = d.groupby(["year", "mnth"], as_index=False)["cnt"].sum()
    m["Bulan"] = m["mnth"].map(lambda i: MONTHS[i - 1])
    m["year"] = m["year"].astype(str)
    f3 = px.line(m, x="Bulan", y="cnt", color="year", markers=True,
                 color_discrete_map={"2011": GREY, "2012": BLUE},
                 category_orders={"Bulan": MONTHS},
                 labels={"cnt": "Total penyewaan per bulan", "year": "Tahun"})
    f3.update_layout(yaxis_rangemode="tozero")
    st.plotly_chart(f3, width="stretch")

    yy = d.groupby("year")[["casual", "registered", "cnt"]].sum()
    if {2011, 2012}.issubset(yy.index):
        g = (yy.loc[2012] / yy.loc[2011] - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("Pertumbuhan total (YoY)", f"{g['cnt']:+.1f}%")
        c2.metric("Registered", f"{g['registered']:+.1f}%")
        c3.metric("Casual", f"{g['casual']:+.1f}%")
    else:
        st.caption("Pilih rentang tanggal yang mencakup 2011 dan 2012 untuk melihat pertumbuhan YoY.")

# ---------------- Tab 4 ----------------
with tab4:
    st.subheader("Analisis lanjutan: Manual Grouping & Binning")
    col_c, col_d = st.columns(2)

    seg = h.groupby(["time_segment", "day_type"], as_index=False)["cnt"].mean()
    f4 = px.bar(seg, y="time_segment", x="cnt", color="day_type", barmode="group", orientation="h",
                color_discrete_map={"Hari Kerja": BLUE, "Akhir Pekan/Libur": ORANGE},
                labels={"time_segment": "", "cnt": "Rata-rata penyewaan per jam", "day_type": ""})
    f4.update_layout(yaxis=dict(autorange="reversed"), title="Segmen waktu dalam sehari", legend=dict(orientation="h", y=-0.25))
    col_c.plotly_chart(f4, width="stretch")

    order_t = ["Dingin (<10C)", "Sejuk (10-20C)", "Hangat (20-30C)", "Panas (>30C)"]
    t = d.groupby("temp_bin", as_index=False, observed=True)["cnt"].mean()
    t["temp_bin"] = pd.Categorical(t["temp_bin"], order_t, ordered=True)
    t = t.sort_values("temp_bin")
    f5 = px.bar(t, x="temp_bin", y="cnt", text=t["cnt"].round(0).map("{:,.0f}".format),
                labels={"temp_bin": "", "cnt": "Rata-rata penyewaan harian"})
    f5.update_traces(marker_color=[BLUE if v == t["cnt"].max() else GREY for v in t["cnt"]])
    f5.update_layout(title="Penyewaan menurut kategori suhu")
    col_d.plotly_chart(f5, width="stretch")

    st.info("**Insight:** Puncak Sore hari kerja adalah segmen tertinggi, dini hari terendah (cocok untuk perawatan). "
            "Suhu hangat 20-30 C menghasilkan penyewaan harian tertinggi.")

st.caption("Dibuat dengan Streamlit | Dataset: Fanaee-T & Gama (2013), Capital Bikeshare.")
