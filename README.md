# ⛏️ LinkedIn Loker Planner Tambang Scraper (Dual Engine)

Aplikasi scraper cerdas berbasis Python untuk mengekstrak lowongan kerja spesifik posisi **Planner di Sektor Pertambangan & Alat Berat (Mining)** di Indonesia. Dilengkapi sistem filter ketat untuk mengekstrak **Nomor HP / WhatsApp dan Alamat Email HRD/Recruiter** secara otomatis ke format Excel (`.xlsx`) dan SQLite (`.sqlite`).

---

## 🌟 Fitur Utama

- **🚀 Dual Engine Architecture**:
  - **Mode 1 (Feed / Status Recruiter)**: Mengambil postingan teks langsung dari timeline recruiter LinkedIn menggunakan sesi browser Camoufox yang anti-deteksi.
  - **Mode 2 (Official Jobs / Lowongan Resmi)**: 100% **Tanpa Login** (Bebas password & OTP checkpoint), mengekstrak deskripsi lengkap dan kontak rekrutmen.
  - **Mode 3 (Hybrid Dual Mode)**: Menjalankan Mode 2 lalu dilanjutkan Mode 1 untuk cakupan data maksimal.
- **📱 Deteksi Kontak Otomatis**:
  - Algoritma Regex cerdas untuk mendeteksi nomor WhatsApp/telepon Indonesia (`+62`, `08xx`, spasi, strip, tanda kurung).
  - Ekstraksi alamat email HRD dan penyeleksian kontak personal.
- **⛏️ Strict Mining Sector Filter**:
  - Filter otomatis menolak posisi non-tambang (seperti FMCG, Media/Ad Planner, Financial Planner).
  - Mendeteksi kata kunci pertambangan: *Mining, Tambang, Batubara, Nikel, Mineral, Emas, Site, Pit, Alat Berat, Heavy Equipment, Komatsu, Caterpillar, Hitachi, PAMA, BUMA, Adaro, Harita, Freeport, Thiess, Macmahon, dll*.
- **📊 Ekspor Otomatis**:
  - Spreadsheet Excel rapi dengan styling header, auto-fit lebar kolom, dan nomor kontak di kolom depan.
  - Database SQLite lokal untuk integritas data dan riwayat pencarian.

---

## 📂 Struktur Proyek

```text
linkedin-loker-scraper/
├── main.py                  # Entry point CLI (menu pilihan Mode 1 / 2 / 3)
├── public_jobs_scraper.py   # Engine scraper lowongan resmi (100% tanpa login)
├── feed_text_scraper.py     # Engine scraper feed timeline recruiter (Camoufox)
├── extractor.py             # Parser regex kontak (HP/WA/Email) & filter tambang
├── storage.py               # Penyimpanan data ke Excel (.xlsx) & SQLite (.sqlite)
├── config_manager.py        # Pengelola konfigurasi & parameter pencarian
├── pengaturan.json          # File konfigurasi utama (kata kunci, filter, export)
├── .env.example             # Template konfigurasi environment (opsional)
├── CARA_AMBIL_COOKIE.md     # Panduan mengambil cookie sesi li_at dari browser
├── PANDUAN_PENGGUNAAN.md    # Panduan penggunaan lengkap
├── JALANKAN_SCRAPER.bat     # Shortcut 1-Click launcher di Windows
└── requirements.txt         # Daftar dependensi Python
```

---

## 🛠️ Instalasi & Persiapan

### 1. Prasyarat
- Python 3.10 atau versi lebih baru.
- Google Chrome atau browser modern untuk mengambil cookie sesi (hanya jika menggunakan Mode 1).

### 2. Instalasi Dependensi
Jalankan perintah berikut di terminal:
```bash
pip install -r requirements.txt
camoufox fetch
```

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan Script Launcher (Windows)
Cukup klik dua kali file **`JALANKAN_SCRAPER.bat`**.

### Cara 2: Menjalankan via Terminal
```bash
python main.py
```
Pilih mode yang diinginkan:
- Ketik `1` untuk Mode Feed Recruiter (Butuh Sesi / Cookie `li_at`).
- Ketik `2` untuk Mode Lowongan Resmi (**100% Bebas Login**).
- Ketik `3` untuk Mode Hybrid (Jalankan keduanya).

---

## ⚙️ Konfigurasi (`pengaturan.json`)

Anda dapat menyesuaikan kata kunci pencarian, filter, dan output langsung di `pengaturan.json`:

```json
{
  "pencarian": {
    "target_minimal_data": 30,
    "daftar_kata_kunci_pertambangan": [
      "loker mine planner",
      "loker planner tambang",
      "hiring mine planner",
      "maintenance planner tambang"
    ],
    "kata_kunci_utama": "planner",
    "lokasi": "Indonesia",
    "wajib_sektor_tambang": true,
    "hanya_yang_ada_kontak_email_atau_hp": true
  },
  "ekspor": {
    "simpan_ke_excel": true,
    "simpan_ke_sqlite": true,
    "nama_file_excel": "kontak_loker_planner_tambang.xlsx",
    "nama_file_database": "database_loker_tambang.sqlite"
  }
}
```

---

## 🔒 Keamanan & Privasi

- **Jangan pernah melakukan commit file `sesi_linkedin.json` atau file `.env`** yang memuat cookie sesi Anda ke repositori publik.
- File sesi dan data output telah terdaftar di `.gitignore` untuk mencegah kebocoran data sensitif.

---

## 📄 Lisensi
MIT License
