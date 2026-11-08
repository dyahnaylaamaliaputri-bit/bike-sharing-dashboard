# Proyek Analisis Data: Bike Sharing Dashboard 🚲

Analisis penyewaan sepeda Capital Bikeshare (Washington D.C., 2011-2012): pola per jam, pengaruh cuaca & musim, dan pertumbuhan tahunan, disajikan dalam dashboard Streamlit interaktif.

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv     # data per jam yang sudah dibersihkan
| ├───day_data.csv      # data harian yang sudah dibersihkan
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment - Anaconda
```
conda create --name bike-ds python=3.11
conda activate bike-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Dashboard
```
cd dashboard
streamlit run dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Menjalankan Notebook
Jalankan `jupyter notebook` lalu buka `notebook.ipynb` dari folder utama (path data relatif: `data/` dan `dashboard/`).

## Pertanyaan Bisnis
1. Pada jam berapa penyewaan memuncak pada hari kerja vs akhir pekan/libur, dan berapa selisihnya (2011-2012)?
2. Seberapa besar penurunan penyewaan harian pada cuaca buruk vs cerah, dan musim mana tertinggi/terendah (2011-2012)?
3. Berapa pertumbuhan 2012 vs 2011 dan siapa pendorongnya (registered/casual)?

## Teknik Analisis Lanjutan
Manual Grouping (segmen waktu dalam sehari) dan Binning (kategori suhu, level demand). RFM dan geospatial tidak digunakan karena dataset tidak memuat identitas pelanggan maupun koordinat lokasi.
