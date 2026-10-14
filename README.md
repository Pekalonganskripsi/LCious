# LCious

**Local Culinary & Delicious** — Sistem Rekomendasi Kuliner Lokal berbasis Web dengan algoritma Hybrid *Fuzzy Logic + Collaborative Filtering*.

- **Aplikasi**: https://lcious.mygarden.my.id/
- **Manual Book**: lihat `manualbook.docx`

## Tentang

LCious membantu pengguna menemukan kuliner lokal UMKM sesuai selera pribadi (pedas, manis, gurih), budget harga, jarak lokasi, dan popularitas — sekaligus memberi UMKM kanal digital untuk memasarkan menu.

Rekomendasi dihitung dengan Hybrid Recommendation System:

```
Hscore(u,i) = (α × Sf(u,i)) + ((1-α) × Pcf(u,i)/Rmax)
```

- **Fuzzy Logic** — kecocokan preferensi pribadi (harga, jarak, rasa, jenis masakan, popularitas)
- **Collaborative Filtering** — prediksi rating dari pola komunitas (KNN, Pearson correlation, K=10)
- **Adaptive Alpha** — bobot α menyesuaikan jumlah rating merchant (mengatasi cold start)

## Teknologi

| Bagian | Teknologi |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend | React 18, Vite, Tailwind CSS, Zustand |
| Algoritma | Fuzzy Logic (Triangular MF), User-Based CF (KNN + Pearson), Hybrid Weighted, Haversine |
| Evaluasi | MAE, RMSE, Hit Rate, 5-Fold Cross-Validation, Paired t-test |

## Struktur Proyek

```
LCicious/
├── backend/     # REST API FastAPI (port 8001)
│   └── app/
│       ├── algorithms/   # fuzzy.py, collaborative_filtering.py, hybrid.py, evaluation.py
│       ├── api/v1/       # endpoint auth, menus, merchants, recommendations, admin
│       ├── models/       # model SQLAlchemy
│       └── core/         # security, config
├── frontend/    # SPA React + Vite (port 8091)
│   └── src/
│       ├── pages/        # halaman aplikasi (customer, merchant, admin)
│       ├── components/   # komponen UI
│       └── store/        # state management Zustand
├── algoritma.md   # dokumentasi algoritma sistem rekomendasi
└── penjelasan.md  # dokumentasi teknis lengkap
```

## Pengembang

| Nama | Peran |
|---|---|
| **Fenilinas Adi Art.** | Programmer — perancang & pengembang aplikasi (backend, frontend, algoritma rekomendasi) |
| **Imam Rosyadi** | Mitra UMKM — survei pendataan merchant dan perhitungan kebutuhan merchant |

## Role Pengguna

1. **Customer** — menjelajah menu, menerima rekomendasi personal, memberi rating & review, mengatur preferensi rasa
2. **Merchant (UMKM)** — mendaftarkan warung, mengelola menu, memantau rating & performa
3. **Superadmin** — mengelola pengguna & merchant, mengatur parameter algoritma, menjalankan evaluasi sistem
