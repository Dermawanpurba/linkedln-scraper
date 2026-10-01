import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from config_manager import get_config
from public_jobs_scraper import run_public_jobs
from feed_text_scraper import run_feed_scraper

def main():
    print("=" * 70)
    print("       LINKEDIN PLANNER SCRAPER (INDONESIA) - DUAL ENGINE")
    print("=" * 70)
    print("1. [Mode 1] Scrape Postingan Feed / Status Recruiter")
    print("            -> Butuh Sesi Login (Pakai sesi_linkedin.json / Cookie li_at)")
    print("2. [Mode 2] Scrape Lowongan Resmi & Teks Lengkap Terbaru")
    print("            -> 100% TANPA LOGIN (Bebas OTP/Password, Tarik Teks & Kontak)")
    print("3. [Mode 3] Scrape Keduanya (Lowongan Resmi + Feed Recruiter)")
    print("=" * 70)

    config = get_config()
    default_mode = config.get("pencarian", {}).get("mode", "2")

    pilihan = input(f"Pilih mode (1/2/3) [Default: {default_mode}]: ").strip()
    if not pilihan:
        pilihan = default_mode

    if pilihan == "1":
        print("\n[*] Menjalankan Mode 1: Postingan Teks Recruiter...")
        run_feed_scraper()
    elif pilihan == "2":
        print("\n[*] Menjalankan Mode 2: Lowongan Resmi LinkedIn Indonesia...")
        run_public_jobs()
    elif pilihan == "3":
        print("\n[*] Menjalankan Mode 3: Scrape Keduanya...")
        print("\n--- TAHAP 1: Lowongan Resmi LinkedIn Indonesia ---")
        run_public_jobs()
        print("\n--- TAHAP 2: Postingan Teks Recruiter (Feed) ---")
        run_feed_scraper()
    else:
        print("[!] Pilihan tidak valid. Menjalankan Mode 2 (Lowongan Resmi)...")
        run_public_jobs()

if __name__ == "__main__":
    main()
