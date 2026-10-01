# ⛏️ LinkedIn Loker Planner Tambang Scraper (Khusus Kontak HP & Email)

Aplikasi scraper cerdas yang dikhususkan untuk mencari dan mengekstrak info lowongan kerja posisi **Planner di Sektor Pertambangan & Alat Berat (Mining)** di wilayah **Indonesia**, yang secara spesifik **hanya mengambil Nomor WhatsApp/HP dan Alamat Email HRD** langsung dari postingan teks timeline LinkedIn.

---

## 🎯 Fokus Utama Sesuai Kebutuhan Anda

1. **🚫 Tanpa Tautan / Link Lamar yang Berbelit-belit**:
   - Kolom tautan eksternal ditiadakan agar spreadsheet bersih dan langsung tertuju pada kontak personal recruiter.
2. **📱 Fokus Hanya Nomor HP / WhatsApp & Email HRD**:
   - Postingan teks yang **TIDAK mencantumkan No HP atau Email otomatis dilewati (diabaikan)**.
   - Hanya postingan yang memuat kontak langsung untuk mengirim CV / chat WhatsApp yang diekstrak dan disimpan.
3. **⛏️ Kunci Ketat Sektor Pertambangan (Anti-Melenceng)**:
   - Dilengkapi filter ketat kata kunci pertambangan: *Mining, Tambang, Batubara, Nikel, Mineral, Emas, Site, Pit, Alat Berat, Heavy Equipment, Komatsu, Caterpillar, Hitachi, PAMA, BUMA, Adaro, Harita, Freeport, Thiess, Macmahon, dll*.
   - Posisi di luar tambang (seperti Media Planner periklanan, Financial Planner, FMCG) **100% otomatis ditolak**.

---

## 📋 Klasifikasi Posisi Planner Tambang yang Dideteksi

* **Maintenance Planner Alat Berat (Mining)**: Plant Planner, Fleet Planner, Heavy Equipment Planner.
* **Mine Planner (Short / Long Term)**: STP/LTP Engineer, Pit Planner, Desain Tambang.
* **Production / Pit Planner Tambang**: Perencanaan produksi batubara/nikel, Drill & Blast, Hauling & Crushing.
* **Supply Chain / Logistics Site Tambang**: Material Planner site tambang, Inventory spare part alat berat.
* **Project Planner Tambang**: Project Scheduler site tambang (Primavera / MS Project).

---

## 📊 Tampilan Kolom di File Excel (`kontak_loker_planner_tambang.xlsx`)

Data disusun sangat rapi dengan nomor kontak dan email di bagian depan:

| No | Posisi / Role Planner | Nomor HP / WhatsApp HRD | Email Kirim CV / Rekrutmen | Kategori Sektor Tambang | Perusahaan / Site / Poster | Lokasi Site | Waktu Post | Kutipan Lengkap Teks Postingan & Kualifikasi |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: | :---: | :--- |

---

## 🚀 Cara Menjalankan Scraper (Sangat Mudah)

1. Buka file [pengaturan.json](file:///c:/xampp/htdocs/linkedin-loker-scraper/pengaturan.json).
2. Isi email dan password akun LinkedIn Anda pada baris:
   ```json
   "linkedin_email": "email_anda@gmail.com",
   "linkedin_password": "password_anda",
   ```
   *(Catatan: Anda juga bisa mengosongkannya, scraper akan otomatis menanyakan email & password langsung di terminal).*
3. Klik dua kali file **[JALANKAN_SCRAPER.bat](file:///c:/xampp/htdocs/linkedin-loker-scraper/JALANKAN_SCRAPER.bat)** (atau jalankan `python main.py`).
4. Scraper akan otomatis melakukan login, menyimpan sesi ke `sesi_linkedin.json`, dan langsung mengekstrak kontak loker planner pertambangan.
5. Selesai! Buka file **[kontak_loker_planner_tambang.xlsx](file:///c:/xampp/htdocs/linkedin-loker-scraper/kontak_loker_planner_tambang.xlsx)** untuk melihat daftar nomor HP dan email HRD yang siap dihubungi.
