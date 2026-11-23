"""SPK Seleksi Beasiswa Bidikmisi UNTAN: AHP (bobot) + TOPSIS (ranking), SAW sebagai pembanding.
Data: Tabel 3 jurnal Sari & Alliandaw (2022), SISFOKOM 11(2). Jalankan: streamlit run app.py
"""
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- data awal
KODE = ["K1", "K2", "K3", "K4", "K5"]
NAMA = ["Rata-rata nilai rapor", "Usia", "Pendapatan orang tua",
        "Status kepemilikan rumah", "Jumlah tanggungan"]
TIPE = ["Benefit", "Cost", "Cost", "Benefit", "Benefit"]
ALT = [[4, 3, 1, 3, 3], [3, 5, 2, 3, 2], [2, 1, 1, 5, 2], [4, 1, 1, 1, 4], [2, 4, 3, 4, 4],
       [2, 5, 2, 4, 3], [5, 3, 1, 1, 2], [2, 1, 4, 1, 5], [1, 3, 1, 3, 5], [4, 2, 3, 1, 4],
       [2, 4, 2, 3, 1], [2, 3, 1, 3, 3], [4, 2, 2, 1, 1], [4, 5, 4, 5, 2], [3, 4, 1, 3, 2],
       [2, 3, 1, 5, 2], [4, 2, 4, 2, 2], [1, 4, 4, 4, 2], [3, 4, 3, 5, 1], [3, 1, 2, 3, 2],
       [5, 5, 3, 1, 4], [2, 4, 1, 5, 4], [4, 5, 3, 4, 5], [5, 4, 5, 4, 5], [5, 1, 3, 1, 5],
       [1, 5, 3, 4, 2], [5, 3, 3, 3, 2], [4, 3, 5, 2, 2], [3, 4, 3, 2, 2], [2, 4, 2, 3, 5]]
SKALA = {
    "K1 Rata-rata nilai rapor": ["< 50", "50 – 60", "> 60 – 70", "> 70 – 80", "> 80"],
    "K2 Usia": ["< 19 tahun", "19 tahun", "20 tahun", "21 tahun", "> 21 tahun"],
    "K3 Pendapatan orang tua": ["< Rp 300.000", "Rp 300.000 – 800.000", "> Rp 800.000 – 1.500.000",
                                "> Rp 1.500.000 – 3.000.000", "> Rp 3.000.000"],
    "K4 Status kepemilikan rumah": ["Pribadi", "Warisan", "Sewa tahunan", "Sewa bulanan", "Menumpang"],
    "K5 Jumlah tanggungan": ["1 orang", "2 orang", "3 orang", "4 – 5 orang", "> 5 orang"],
}
RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
SAATY = ["1/9", "1/8", "1/7", "1/6", "1/5", "1/4", "1/3", "1/2", "1",
         "2", "3", "4", "5", "6", "7", "8", "9"]
AHP_DEF = {(0, 1): "1/3", (0, 2): "1/2", (0, 3): "1", (0, 4): "1/2", (1, 2): "2",
           (1, 3): "3", (1, 4): "2", (2, 3): "2", (2, 4): "1", (3, 4): "1/2"}


# ---------------------------------------------------------------- perhitungan
def saaty_val(s):
    if "/" in s:
        a, b = s.split("/")
        return int(a) / int(b)
    return float(s)


def ahp(M):
    n = len(M)
    S = M.sum(axis=0)
    N = M / S
    w = N.mean(axis=1)
    lam = (M @ w) / w
    lmax = lam.mean()
    ci = (lmax - n) / (n - 1)
    cr = ci / RI[n] if RI[n] > 0 else 0.0
    return S, N, w, lam, lmax, ci, cr


def topsis(X, w, types):
    ben = np.array([t == "Benefit" for t in types])
    R = X / np.sqrt((X ** 2).sum(axis=0))
    Y = R * w
    Ap = np.where(ben, Y.max(0), Y.min(0))
    Am = np.where(ben, Y.min(0), Y.max(0))
    Dp = np.sqrt(((Y - Ap) ** 2).sum(1))
    Dm = np.sqrt(((Y - Am) ** 2).sum(1))
    return R, Y, Ap, Am, Dp, Dm, Dm / (Dm + Dp)


def saw(X, w, types):
    ben = np.array([t == "Benefit" for t in types])
    R = np.where(ben, X / X.max(0), X.min(0) / X)
    return R, R * w, (R * w).sum(1)


def rank_min(v):
    return pd.Series(np.round(v, 12)).rank(ascending=False, method="min").astype(int).values


def rank_uniq(v):
    return pd.Series(np.round(v, 12)).rank(ascending=False, method="first").astype(int).values


def sens_weights(w, k, p):
    """Bobot kriteria k diubah relatif p; bobot lain disesuaikan proporsional, total tetap 1."""
    new = w * (1 - w[k] * (1 + p)) / (1 - w[k])
    new[k] = w[k] * (1 + p)
    return new


def to_excel(sheets):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as xw:
        for name, d in sheets.items():
            d.to_excel(xw, sheet_name=name, index=False)
    return bio.getvalue()


# ---------------------------------------------------------------- UI
st.set_page_config(page_title="SPK Bidikmisi UNTAN", layout="wide")
st.title("SPK Seleksi Beasiswa Bidikmisi UNTAN")
st.caption("AHP untuk bobot kriteria → TOPSIS untuk pemeringkatan (SAW sebagai pembanding). "
           "Data: Tabel 3 jurnal Sari & Alliandaw (2022), SISFOKOM 11(2).")
kuota = st.sidebar.number_input("Kuota penerima", min_value=1, value=5, step=1)
st.sidebar.markdown("Semua tahap dihitung otomatis dan ditampilkan di tiap tab.")

tabs = st.tabs(["1 Data", "2 AHP", "3 TOPSIS", "4 SAW", "5 Hasil", "6 Sensitivitas", "7 Kontribusi"])

# ---- 1. Data
with tabs[0]:
    st.subheader("Kriteria")
    kri = st.data_editor(
        pd.DataFrame({"Kode": KODE, "Kriteria": NAMA, "Tipe": TIPE}), hide_index=True,
        disabled=["Kode"], key="kri",
        column_config={"Tipe": st.column_config.SelectboxColumn(options=["Benefit", "Cost"], required=True)})
    st.caption("Benefit: makin besar makin baik. Cost: makin kecil makin baik. "
               "K4: skor tinggi = kondisi rumah makin kurang mampu.")
    with st.expander("Skala penilaian (skor 1–5)"):
        st.dataframe(pd.DataFrame(SKALA, index=[1, 2, 3, 4, 5]))
    st.subheader("Alternatif (skor 1–5)")
    df0 = pd.DataFrame(ALT, columns=KODE)
    df0.insert(0, "Alternatif", [f"A{i + 1}" for i in range(len(ALT))])
    alt = st.data_editor(
        df0, num_rows="dynamic", hide_index=True, key="alt",
        column_config={k: st.column_config.NumberColumn(min_value=1, max_value=5, step=1) for k in KODE})

alt = alt.dropna()
if len(alt) < 2:
    st.error("Minimal 2 alternatif.")
    st.stop()
if not alt[KODE].apply(lambda c: c.between(1, 5)).all().all():
    st.error("Skor harus 1–5.")
    st.stop()
if len(alt) < 30:
    tabs[0].warning(f"Alternatif saat ini {len(alt)}; ketentuan tugas minimal 30.")
names = alt["Alternatif"].astype(str).tolist()
X = alt[KODE].astype(float).values
types = kri["Tipe"].tolist()
ben = np.array([t == "Benefit" for t in types])

# ---- 2. AHP
with tabs[1]:
    st.subheader("Perbandingan berpasangan (skala Saaty)")
    st.caption("Isi segitiga atas: 'baris lebih penting dari kolom'. Segitiga bawah otomatis kebalikannya.")
    n = len(KODE)
    M = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            c1, c2 = st.columns([3, 1])
            v = c2.selectbox(f"{KODE[i]} vs {KODE[j]}", SAATY, index=SAATY.index(AHP_DEF[(i, j)]),
                             key=f"p{i}{j}")
            c1.markdown(f"**{KODE[i]}** {NAMA[i]} &nbsp;vs&nbsp; **{KODE[j]}** {NAMA[j]}")
            M[i, j] = saaty_val(v)
            M[j, i] = 1 / M[i, j]
    S, N_, w, lam, lmax, ci, cr = ahp(M)
    st.markdown("**1. Matriks perbandingan** (baris Σ = jumlah tiap kolom)")
    dfM = pd.DataFrame(M, index=KODE, columns=KODE)
    dfM.loc["Σ kolom"] = S
    st.dataframe(dfM.round(4))
    st.markdown("**2. Normalisasi (a/Σ kolom) dan bobot w = rata-rata baris**")
    dfN = pd.DataFrame(N_, index=KODE, columns=KODE)
    dfN["Bobot (w)"] = w
    st.dataframe(dfN.round(5))
    st.markdown("**3. Uji konsistensi**")
    dfL = pd.DataFrame({"v = Σ a·w": M @ w, "w": w, "λ = v/w": lam}, index=KODE)
    st.dataframe(dfL.round(5))
    c = st.columns(5)
    c[0].metric("λ maks", f"{lmax:.5f}")
    c[1].metric("CI", f"{ci:.5f}")
    c[2].metric("RI (n=5)", f"{RI[n]:.2f}")
    c[3].metric("CR", f"{cr:.5f}")
    c[4].metric("Status", "Konsisten" if cr <= 0.10 else "TIDAK konsisten")
    st.latex(r"CI=\frac{\lambda_{maks}-n}{n-1},\quad CR=\frac{CI}{RI}\le 0{,}10")
    if cr <= 0.10:
        st.success("CR ≤ 0,10: penilaian konsisten, bobot dipakai pada TOPSIS dan SAW.")
    else:
        st.error("CR > 0,10: revisi perbandingan berpasangan sebelum hasil dipakai.")

# ---- hitung semua
R, Y, Ap, Am, Dp, Dm, V = topsis(X, w, types)
Rs, Ys, Vs = saw(X, w, types)
rk, rku = rank_min(V), rank_uniq(V)
rks = rank_min(Vs)
if cr > 0.10:
    st.warning("CR > 0,10: hasil di bawah belum valid secara AHP.")

# ---- 3. TOPSIS
with tabs[2]:
    st.subheader("Tahapan TOPSIS")
    st.dataframe(pd.DataFrame({"Kriteria": NAMA, "Tipe": types, "Bobot (AHP)": w}, index=KODE).round(5))
    st.markdown("**1. Matriks keputusan (X)**")
    st.dataframe(pd.DataFrame(X, index=names, columns=KODE))
    st.markdown("**2. Normalisasi**")
    st.latex(r"r_{ij}=\frac{x_{ij}}{\sqrt{\sum_i x_{ij}^2}}")
    st.dataframe(pd.DataFrame(R, index=names, columns=KODE).round(5))
    st.markdown("**3. Normalisasi terbobot**")
    st.latex(r"y_{ij}=w_j\,r_{ij}")
    st.dataframe(pd.DataFrame(Y, index=names, columns=KODE).round(5))
    st.markdown("**4. Solusi ideal** (benefit: A⁺ = maks, A⁻ = min; cost sebaliknya)")
    st.dataframe(pd.DataFrame([Ap, Am], index=["A⁺", "A⁻"], columns=KODE).round(5))
    st.markdown("**5. Jarak dan nilai preferensi**")
    st.latex(r"D^+_i=\sqrt{\sum_j (y_{ij}-A^+_j)^2},\;D^-_i=\sqrt{\sum_j (y_{ij}-A^-_j)^2},\;V_i=\frac{D^-_i}{D^-_i+D^+_i}")
    st.dataframe(pd.DataFrame({"D+": Dp, "D−": Dm, "V": V, "Peringkat": rk}, index=names).round(5))

# ---- 4. SAW
with tabs[3]:
    st.subheader("Tahapan SAW (pembanding, bobot AHP yang sama)")
    st.latex(r"r_{ij}=\frac{x_{ij}}{\max_i x_{ij}}\ (\text{benefit}),\quad r_{ij}=\frac{\min_i x_{ij}}{x_{ij}}\ (\text{cost}),\quad V_i=\sum_j w_j r_{ij}")
    st.markdown("**Normalisasi**")
    st.dataframe(pd.DataFrame(Rs, index=names, columns=KODE).round(5))
    st.markdown("**Nilai preferensi**")
    st.dataframe(pd.DataFrame({"V SAW": Vs, "Peringkat": rks}, index=names).round(5))

# ---- 5. Hasil
with tabs[4]:
    st.subheader("Hasil pemeringkatan")
    hasil = pd.DataFrame({"Alternatif": names, "V TOPSIS": V, "Peringkat TOPSIS": rk,
                          "V SAW": Vs, "Peringkat SAW": rks, "_u": rku})
    hasil["Selisih (TOPSIS − SAW)"] = hasil["Peringkat TOPSIS"] - hasil["Peringkat SAW"]
    hasil["Keputusan"] = np.where(hasil["_u"] <= kuota, "Direkomendasikan", "Tidak direkomendasikan")
    hasil = hasil.sort_values("_u").drop(columns="_u").reset_index(drop=True)
    rec = hasil[hasil["Keputusan"] == "Direkomendasikan"]["Alternatif"].tolist()
    saw_top = hasil.sort_values("Peringkat SAW").head(kuota)["Alternatif"].tolist()
    st.success(f"Direkomendasikan (kuota {kuota}): {', '.join(rec)}")
    st.caption(f"Irisan dengan {kuota} teratas SAW: {len(set(rec) & set(saw_top))} dari {kuota}. "
               f"Peringkat sama pada {(hasil['Selisih (TOPSIS − SAW)'] == 0).sum()} alternatif.")
    st.dataframe(
        hasil.style.apply(lambda r: ["background-color:#d4edda;color:#000" if r["Keputusan"] == "Direkomendasikan" else ""] * len(r), axis=1)
        .format({"V TOPSIS": "{:.5f}", "V SAW": "{:.5f}"}),
        hide_index=True)
    st.bar_chart(hasil.set_index("Alternatif")["V TOPSIS"])
    st.markdown("**Profil alternatif tertinggi dan terendah** (skor asli per kriteria)")
    i_hi, i_lo = int(np.argmin(rku)), int(np.argmax(rku))
    prof = pd.DataFrame(X[[i_hi, i_lo]], index=[f"{names[i_hi]} (peringkat tertinggi)",
                                                 f"{names[i_lo]} (peringkat terendah)"], columns=KODE)
    st.dataframe(prof)
    st.download_button("Unduh hasil (Excel)", to_excel({
        "Bobot AHP": pd.DataFrame({"Kode": KODE, "Kriteria": NAMA, "Tipe": types, "Bobot": w}),
        "Hasil": hasil}), file_name="hasil_spk_ahp_topsis.xlsx")

# ---- 6. Sensitivitas
with tabs[5]:
    st.subheader("Analisis sensitivitas bobot")
    st.caption("Bobot satu kriteria diubah relatif sebesar p; bobot lain disesuaikan proporsional sehingga total tetap 1.")
    c1, c2 = st.columns(2)
    kk = c1.selectbox("Kriteria yang diubah", range(n), format_func=lambda i: f"{KODE[i]} {NAMA[i]}")
    p = c2.slider("Perubahan relatif bobot (%)", -90, 100, 20) / 100
    wn = sens_weights(w, kk, p)
    Vn = topsis(X, wn, types)[-1]
    rn, rnu = rank_min(Vn), rank_uniq(Vn)
    st.dataframe(pd.DataFrame({"Bobot dasar": w, "Bobot baru": wn}, index=KODE).T.round(4)
                 .assign(**{"Σ": [w.sum(), wn.sum()]}))
    cmp_ = pd.DataFrame({"Alternatif": names, "Peringkat dasar": rk, "Peringkat baru": rn,
                         "Pergeseran": rk - rn, "V baru": Vn}).sort_values("Peringkat baru")
    m = st.columns(3)
    m[0].metric("Alternatif berubah peringkat", int((rk != rn).sum()))
    m[1].metric("Pergeseran terbesar", int(np.abs(rk - rn).max()))
    m[2].metric("Penerima kuota berubah", "Ya" if set(np.array(names)[rku <= kuota]) != set(np.array(names)[rnu <= kuota]) else "Tidak")
    st.dataframe(cmp_.style.format({"V baru": "{:.5f}"}), hide_index=True)

    st.markdown("**Ringkasan semua skenario (±p)**")
    base_rec = set(np.array(names)[rku <= kuota])
    rows = [{"Skenario": "Dasar", "Berubah": 0, "Geser maks": 0, "Peringkat 1": names[int(np.argmin(rku))],
             "Penerima kuota berubah": "Tidak"}]
    for i in range(n):
        for sgn, lab in ((1, "+p"), (-1, "−p")):
            Vx = topsis(X, sens_weights(w, i, sgn * abs(p)), types)[-1]
            rx = rank_min(Vx)
            rows.append({"Skenario": f"{KODE[i]} {lab}", "Berubah": int((rk != rx).sum()),
                         "Geser maks": int(np.abs(rk - rx).max()),
                         "Peringkat 1": names[int(np.argmin(rank_uniq(Vx)))],
                         "Penerima kuota berubah": "Ya" if set(np.array(names)[rank_uniq(Vx) <= kuota]) != base_rec else "Tidak"})
    st.dataframe(pd.DataFrame(rows), hide_index=True)

# ---- 7. Kontribusi
with tabs[6]:
    st.subheader("Kontribusi kriteria terhadap hasil")
    st.caption("Membandingkan rata-rata nilai terbobot (y) kelompok N teratas vs N terbawah. "
               "Selisih dibalik untuk kriteria cost agar searah keuntungan.")
    Nn = st.slider("N kelompok atas/bawah", 1, max(1, len(names) // 2), 3)
    order = np.argsort(rku)
    mt, mb = Y[order[:Nn]].mean(0), Y[order[-Nn:]].mean(0)
    sel = np.where(ben, mt - mb, mb - mt)
    kont = pd.DataFrame({"Kriteria": NAMA, "Tipe": types, "Bobot AHP": w, "Rata-rata y atas": mt,
                         "Rata-rata y bawah": mb, "Selisih (searah)": sel, "Kontribusi": sel / sel.sum()}, index=KODE)
    st.dataframe(kont.style.format({"Bobot AHP": "{:.4f}", "Rata-rata y atas": "{:.5f}",
                                    "Rata-rata y bawah": "{:.5f}", "Selisih (searah)": "{:.5f}",
                                    "Kontribusi": "{:.1%}"}))
    st.caption("Kontribusi besar = kriteria itu paling membedakan kelompok atas dari bawah. "
               "Negatif = kriteria itu justru lebih menguntungkan kelompok bawah.")
    st.bar_chart(kont["Kontribusi"])
