# SPK Seleksi Beasiswa Bidikmisi UNTAN (AHP + TOPSIS)

Aplikasi Sistem Pendukung Keputusan (SPK) untuk menyeleksi penerima beasiswa Bidikmisi
Universitas Tanjungpura dengan metode **Multi-Attribute Decision Making (MADM)**:

- **AHP** (Analytical Hierarchy Process) untuk menentukan bobot kriteria, lengkap dengan uji konsistensi (CR ≤ 0,10).
- **TOPSIS** untuk pemeringkatan alternatif memakai bobot hasil AHP.
- **SAW** sebagai metode pembanding (bobot AHP yang sama).

Final Project mata kuliah Sistem Pendukung Keputusan (SPK), 2026.

## Studi kasus

Kasus diambil dari jurnal:

> Sari, R. P., & Alliandaw, A. M. (2022). Penerapan Metode MOORA Pada Sistem Penentuan
> Penerimaan Bidikmisi UNTAN. *Jurnal SISFOKOM (Sistem Informasi dan Komputer)*, 11(2), 242–250.
> DOI: 10.32736/sisfokom.v11i2.1420

Jurnal tersebut memakai MOORA dengan bobot langsung. Pada proyek ini bobot dihitung ulang dengan AHP
dan pemeringkatan memakai TOPSIS. Data alternatif (30 calon penerima) diambil dari Tabel 3 jurnal.
Kuota penerima: 5 dari 30 alternatif.

### Kriteria

| Kode | Kriteria | Tipe | Keterangan skala (skor 1–5) |
|---|---|---|---|
| K1 | Rata-rata nilai rapor | Benefit | < 50, 50–60, >60–70, >70–80, >80 |
| K2 | Usia | Cost | < 19, 19, 20, 21, > 21 tahun |
| K3 | Pendapatan orang tua | Cost | < 300 rb, 300–800 rb, >800 rb–1,5 jt, >1,5–3 jt, > 3 jt |
| K4 | Status kepemilikan rumah | Benefit | Pribadi, warisan, sewa tahunan, sewa bulanan, menumpang |
| K5 | Jumlah tanggungan | Benefit | 1, 2, 3, 4–5, > 5 orang |

## Fitur aplikasi

Aplikasi punya 7 tab:

1. **Data:** kriteria (tipe benefit/cost) dan alternatif, bisa diedit.
2. **AHP:** perbandingan berpasangan (skala Saaty), bobot, λ maks, CI, CR, dan status konsistensi.
3. **TOPSIS:** seluruh tahap ditampilkan (matriks keputusan, normalisasi, terbobot, solusi ideal, jarak, nilai preferensi, peringkat).
4. **SAW:** tahapan metode pembanding.
5. **Hasil:** peringkat akhir, penerima sesuai kuota, grafik, profil alternatif tertinggi dan terendah, unduh Excel.
6. **Sensitivitas:** ubah bobot satu kriteria, bobot lain disesuaikan proporsional sehingga total tetap 1.
7. **Kontribusi:** kontribusi tiap kriteria terhadap perbedaan kelompok teratas dan terbawah.

## Hasil

- Bobot AHP: K1 0,109 · K2 0,368 · K3 0,206 · K4 0,109 · K5 0,206
- CR = 0,003 (konsisten, CR ≤ 0,10)
- Penerima menurut TOPSIS (kuota 5): **A4, A25, A3, A20, A8**

Hasil aplikasi sudah dicocokkan dengan perhitungan di Excel.

## Menjalankan di komputer sendiri

Butuh Python 3 (diuji di Python 3.14).

```bash
pip install -r requirements.txt
streamlit run app.py
```

Di Windows dengan Python install manager, gunakan:

```bash
py -3.14 -m pip install -r requirements.txt
py -3.14 -m streamlit run app.py
```

Aplikasi terbuka di `http://localhost:8501`.

## Deploy online (Streamlit Community Cloud)

1. Upload `app.py` dan `requirements.txt` ke repository GitHub.
2. Buka [share.streamlit.io](https://share.streamlit.io) dan login dengan GitHub.
3. Pilih **Create app**, pilih repository ini, branch `main`, file `app.py`, lalu **Deploy**.

## Struktur file

```
.
├── app.py             # aplikasi Streamlit (perhitungan AHP, TOPSIS, SAW, sensitivitas, UI)
├── requirements.txt   # streamlit, pandas, numpy, openpyxl
└── README.md
```

| Nama | NPM |
|---|---|
| (isi) | (isi) |
