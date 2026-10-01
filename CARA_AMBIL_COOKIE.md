# 🍪 Panduan Praktis Mengambil Cookie `li_at` LinkedIn

Untuk menggunakan scraper ini, Anda **TIDAK PERLU** memasukkan username ataupun password LinkedIn. Cukup ambil cookie sesi yang bernama **`li_at`** dari browser Anda yang sudah login.

---

### Cara Mengambil Cookie `li_at` (Hanya Butuh 30 Detik):

#### 1. Buka Browser (Google Chrome, Microsoft Edge, atau Brave)
- Buka situs [linkedin.com](https://www.linkedin.com) dan pastikan akun Anda sudah dalam keadaan **Login**.

#### 2. Buka Menu Developer Tools
- Tekan tombol **F12** pada keyboard Anda.
- *(Atau klik kanan di sembarang tempat pada halaman LinkedIn, lalu pilih **Inspect / Periksa**).*

#### 3. Masuk ke Tab Application / Storage
- Di jendela samping/bawah yang baru muncul, cari tab di bagian atas bernama **Application** (pada Google Chrome & Edge) atau **Storage** (pada Firefox).
- *Tips: Jika tab Application tidak terlihat, klik icon panah `>>` di sebelah menu Console/Sources/Network.*

#### 4. Buka Menu Cookies
- Di panel sebelah kiri, cari kelompok **Storage** -> klik tanda panah pada **Cookies**.
- Klik URL `https://www.linkedin.com`.

#### 5. Cari dan Salin Cookie `li_at`
- Di tabel daftar cookie yang muncul di tengah, cari baris yang namanya **`li_at`**.
- Klik dua kali (double click) pada kolom **Value** dari `li_at`.
- Tekan **Ctrl + C** untuk menyalin seluruh nilai token tersebut.
  *(Nilai token biasanya berupa teks acak yang panjang, contohnya diawali dengan `AQEDAR...`)*.

---

### Cara Memasukkan ke Scraper:
1. Buka file **`pengaturan.json`** yang ada di folder ini.
2. Temukan baris:
   ```json
   "linkedin_li_at": "PASTE_COOKIE_LI_AT_DISINI",
   ```
3. Ganti tulisan `"PASTE_COOKIE_LI_AT_DISINI"` dengan cookie yang tadi Anda copy, contoh:
   ```json
   "linkedin_li_at": "AQEDARzXXXXXX...",
   ```
4. Simpan file (**Ctrl + S**).
5. Selesai! Sekarang Anda tinggal menjalankan **`JALANKAN_SCRAPER.bat`**.

---

### ⚠️ PENTING: JANGAN KLIK 'LOG OUT / KELUAR' DI BROWSER
Setelah menyalin cookie:
- **Biarkan tab LinkedIn Anda tetap terbuka/login**.
- **JANGAN menekan tombol "Sign out / Keluar"**, karena sistem LinkedIn akan secara otomatis mematikan (*invalidate*) token cookie tersebut dari server.

---

### Tips Tambahan (Opsional): Menyalin `JSESSIONID`
Tepat di sebelah/dekat baris `li_at`, ada baris cookie bernama **`JSESSIONID`** (contoh value: `ajax:1234567890`).
Jika Anda ingin perlindungan sesi ekstra:
1. Salin juga nilai `JSESSIONID` tersebut.
2. Tempelkan ke baris `"linkedin_jsessionid": ""` di file `pengaturan.json`.

---

> [!NOTE]
> Cookie `li_at` ini berlaku selama sesi login Anda aktif di browser. Jika sewaktu-waktu sesi login di browser Anda habis, cukup ulangi langkah di atas untuk mengambil nilai `li_at` yang baru.
