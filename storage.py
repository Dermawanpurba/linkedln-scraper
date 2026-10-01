import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class StorageManager:
    def __init__(self, db_path: Path, excel_path: Path):
        self.db_path = db_path
        self.excel_path = excel_path
        self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS postingan_loker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_urn TEXT UNIQUE,
                    tipe_sumber TEXT,
                    posisi_pekerjaan TEXT,
                    nama_poster_atau_perusahaan TEXT,
                    lokasi TEXT,
                    tanggal_post TEXT,
                    waktu_disimpan TEXT,
                    kategori_planner TEXT,
                    kontak_email TEXT,
                    kontak_wa TEXT,
                    post_url TEXT,
                    link_profil TEXT,
                    isi_teks_lengkap TEXT
                )
            """)
            conn.commit()

            cursor.execute("PRAGMA table_info(postingan_loker)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            new_cols = {
                "tipe_sumber": "TEXT",
                "posisi_pekerjaan": "TEXT",
                "nama_poster_atau_perusahaan": "TEXT",
                "lokasi": "TEXT",
                "link_profil": "TEXT"
            }
            for col, col_type in new_cols.items():
                if col not in existing_cols:
                    try:
                        cursor.execute(f"ALTER TABLE postingan_loker ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass
            conn.commit()
        finally:
            conn.close()

    def save_to_sqlite(self, posts: List[Dict]) -> tuple[int, int]:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        baru = 0
        duplikat = 0

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            for p in posts:
                try:
                    cursor.execute("""
                        INSERT INTO postingan_loker (
                            post_urn, tipe_sumber, posisi_pekerjaan,
                            nama_poster_atau_perusahaan, lokasi, tanggal_post,
                            waktu_disimpan, kategori_planner, kontak_email,
                            kontak_wa, post_url, link_profil, isi_teks_lengkap
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        p.get("post_urn"),
                        p.get("tipe_sumber", "Postingan Teks Tambang"),
                        p.get("posisi_pekerjaan", "Planner Tambang"),
                        p.get("nama_poster", p.get("nama_poster_atau_perusahaan", "-")),
                        p.get("lokasi", "Site Pertambangan Indonesia"),
                        p.get("tanggal_post", "-"),
                        now_str,
                        p.get("kategori_planner", "Mining Planner"),
                        p.get("kontak_email", "-"),
                        p.get("kontak_wa", "-"),
                        p.get("post_url", ""),
                        p.get("link_profil_poster", p.get("link_profil", "")),
                        p.get("isi_teks_lengkap", "-")
                    ))
                    baru += 1
                except sqlite3.IntegrityError:
                    duplikat += 1
            conn.commit()
        finally:
            conn.close()

        return baru, duplikat

    def export_all_to_excel(self) -> Path:
        """
        Mengekspor kontak nomor HP/WA dan Email loker Planner Tambang ke Excel.
        Kolom link dihilangkan agar fokus 100% pada nomor kontak dan email HRD.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, posisi_pekerjaan, kontak_wa, kontak_email, post_url,
                    link_profil, kategori_planner, nama_poster_atau_perusahaan, lokasi,
                    tanggal_post, waktu_disimpan, isi_teks_lengkap
                FROM postingan_loker
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()
        finally:
            conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Kontak Loker Planner Tambang"
        ws.views.sheetView[0].showGridLines = True

        # Header Definition (Lengkap dengan Link Postingan Feed dan Link Profil HRD)
        headers = [
            "No",
            "Posisi / Role Planner",
            "Nomor HP / WhatsApp HRD",
            "Email Kirim CV / Rekrutmen",
            "Link Postingan Feed Loker",
            "Link Profil LinkedIn HRD",
            "Kategori Sektor Tambang",
            "Perusahaan / Site / Poster",
            "Lokasi / Wilayah Site",
            "Waktu Post",
            "Waktu Scrape",
            "Kutipan Lengkap Teks Postingan & Kualifikasi"
        ]
        ws.append(headers)

        # Header Styling: Tema Pertambangan (Dark Slate / Charcoal Navy)
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border
        ws.row_dimensions[1].height = 32

        # Cell Styles
        fill_even = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        font_regular = Font(name="Segoe UI", size=10, color="1E293B")
        font_contact = Font(name="Segoe UI", size=10, bold=True, color="047857") # Emerald Green untuk kontak
        font_link = Font(name="Segoe UI", size=10, color="2563EB", underline="single")

        row_idx = 2
        for r in rows:
            current_fill = fill_even if row_idx % 2 == 0 else fill_odd
            row_data = [
                r["id"],
                r["posisi_pekerjaan"],
                r["kontak_wa"] if r["kontak_wa"] != "-" else "-",
                r["kontak_email"] if r["kontak_email"] != "-" else "-",
                "Buka Postingan Loker" if r["post_url"] else "-",
                "Buka Profil HRD" if r["link_profil"] else "-",
                r["kategori_planner"],
                r["nama_poster_atau_perusahaan"],
                r["lokasi"],
                r["tanggal_post"],
                r["waktu_disimpan"],
                r["isi_teks_lengkap"]
            ]
            ws.append(row_data)

            for col_num in range(1, len(headers) + 1):
                cell = ws.cell(row=row_idx, column=col_num)
                cell.fill = current_fill
                cell.border = thin_border
                cell.font = font_regular
                cell.alignment = Alignment(vertical="top")

                # Format khusus kolom No HP (Kolom 3) & Email (Kolom 4)
                if col_num in [3, 4] and cell.value and cell.value != "-":
                    cell.font = font_contact
                    cell.alignment = Alignment(horizontal="left", vertical="top")

                # Format Link Postingan Feed Loker (Kolom 5)
                if col_num == 5 and r["post_url"]:
                    cell.hyperlink = r["post_url"]
                    cell.font = font_link
                    cell.alignment = Alignment(horizontal="center", vertical="top")

                # Format Link Profil LinkedIn HRD (Kolom 6)
                if col_num == 6 and r["link_profil"]:
                    cell.hyperlink = r["link_profil"]
                    cell.font = font_link
                    cell.alignment = Alignment(horizontal="center", vertical="top")

                # Center align No, Kategori, Waktu
                if col_num in [1, 7, 9, 10, 11]:
                    cell.alignment = Alignment(horizontal="center", vertical="top")

                # Wrap text for deskripsi postingan
                if col_num == 12:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)

            ws.row_dimensions[row_idx].height = 48
            row_idx += 1

        # Lebar Kolom yang Nyaman
        column_widths = {
            1: 6,   # No
            2: 26,  # Posisi
            3: 24,  # Nomor HP / WhatsApp
            4: 30,  # Email
            5: 24,  # Link Postingan Feed Loker
            6: 22,  # Link Profil LinkedIn HRD
            7: 25,  # Kategori Sektor Tambang
            8: 25,  # Perusahaan / Poster
            9: 20,  # Lokasi Site
            10: 14, # Waktu Post
            11: 18, # Waktu Scrape
            12: 75  # Isi Lengkap Postingan
        }
        for col_num, width in column_widths.items():
            ws.column_dimensions[get_column_letter(col_num)].width = width

        try:
            wb.save(self.excel_path)
            return self.excel_path
        except PermissionError:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_name = self.excel_path.stem + f"_{timestamp}.xlsx"
            fallback_path = self.excel_path.parent / fallback_name
            wb.save(fallback_path)
            print(f"\n[!] Catatan: File '{self.excel_path.name}' sedang terbuka di Microsoft Excel.")
            print(f"[OK] Data berhasil disimpan ke file baru: {fallback_name}")
            return fallback_path
