import sys
import time
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

from config_manager import get_config, BASE_DIR
from extractor import detect_planner_category, clean_text, extract_emails, extract_phones, is_mining_sector
from storage import StorageManager

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

DEFAULT_MINING_QUERIES = [
    "mine planner",
    "planner tambang",
    "maintenance planner mining",
    "planner alat berat",
    "plant planner mining",
    "short term planner",
    "planner nikel",
    "planner batubara"
]

import html

def fetch_job_detail_text(job_id: str) -> str:
    """
    Mengambil seluruh isi teks deskripsi lowongan kerja lengkap (Guest API tanpa login).
    Mendapatkan detail persyaratan, kualifikasi, dan info pengiriman lamaran.
    """
    if not job_id:
        return ""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""

    match = re.search(r'<div class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL)
    if not match:
        match = re.search(r'<div class="description__text[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL)

    if match:
        raw_desc = match.group(1)
        raw_desc = re.sub(r'<(?:br\s*/?|/p|/li|/div)>', '\n', raw_desc, flags=re.IGNORECASE)
        clean = re.sub(r'<[^>]+>', ' ', raw_desc)
        clean = html.unescape(clean)
        lines = [line.strip() for line in clean.split('\n') if line.strip()]
        return '\n'.join(lines)
    return ""

def fetch_guest_jobs_for_query(
    keyword: str,
    location: str = "Indonesia",
    max_per_query: int = 30,
    seen_urns: set = None,
    sort_by_date: bool = True,
    wajib_tambang: bool = True
) -> List[Dict]:
    """
    Mengambil lowongan kerja terbaru beserta teks deskripsi lengkap secara publik (100% TANPA LOGIN).
    """
    if seen_urns is None:
        seen_urns = set()

    results = []
    start = 0
    sort_param = "&sortBy=DD" if sort_by_date else ""

    while len(results) < max_per_query:
        query_url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={urllib.parse.quote(keyword)}&location={urllib.parse.quote(location)}&start={start}{sort_param}"
        )
        try:
            req = urllib.request.Request(query_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                html_resp = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"        [!] Peringatan request ({keyword} start={start}): {e}")
            break

        items = re.findall(r'<div class="base-card[^"]*"(.*?)</li>', html_resp, re.DOTALL)
        if not items:
            break

        batch_count = 0
        for it in items:
            urn_match = re.search(r'data-entity-urn="(urn:li:jobPosting:(\d+))"', it)
            title_match = re.search(r'<h3 class="base-search-card__title">\s*(.*?)\s*</h3>', it)
            comp_match = re.search(r'<h4 class="base-search-card__subtitle">\s*(?:<a[^>]*>)?\s*(.*?)\s*(?:</a>)?\s*</h4>', it)
            loc_match = re.search(r'<span class="job-search-card__location">\s*(.*?)\s*</span>', it)
            link_match = re.search(r'<a class="base-card__full-link[^"]*"\s+href="([^"?]+)', it)
            time_match = re.search(r'<time[^>]*>\s*(.*?)\s*</time>', it)

            urn = urn_match.group(1) if urn_match else ""
            job_id = urn_match.group(2) if urn_match else ""
            title = title_match.group(1).strip() if title_match else "Planner"
            company = comp_match.group(1).strip() if comp_match else "-"
            loc = loc_match.group(1).strip() if loc_match else location
            job_link = link_match.group(1).strip() if link_match else ""
            posted = time_match.group(1).strip() if time_match else "-"

            if not urn:
                urn = job_link

            if urn in seen_urns:
                continue

            # Ambil seluruh teks deskripsi lengkap dari endpoint detail guest
            desc_detail = fetch_job_detail_text(job_id) if job_id else ""
            full_context = f"{title} di {company} - {loc}\n\n{desc_detail}" if desc_detail else f"{title} di {company} - {loc}"

            # Verifikasi sektor tambang jika opsi aktif
            if wajib_tambang and not is_mining_sector(full_context):
                continue

            seen_urns.add(urn)

            category = detect_planner_category(full_context)
            emails = extract_emails(full_context)
            phones = extract_phones(full_context)

            desc = desc_detail if desc_detail else f"Lowongan resmi posisi '{title}' di {company}. Penempatan: {loc}. Diposting: {posted}."

            results.append({
                "post_urn": urn,
                "tipe_sumber": "Lowongan Resmi LinkedIn (Tanpa Login)",
                "posisi_pekerjaan": title,
                "nama_poster_atau_perusahaan": company,
                "lokasi": loc,
                "tanggal_post": posted,
                "kategori_planner": category,
                "kontak_email": ", ".join(emails) if emails else "-",
                "kontak_wa": ", ".join(phones) if phones else "-",
                "post_url": job_link,
                "link_profil": "",
                "isi_teks_lengkap": desc
            })
            batch_count += 1
            print(f"      [+] Teks terserap: {title} | {company} ({posted}) - Teks: {len(desc)} kar.")

            if len(results) >= max_per_query:
                break

            time.sleep(0.6)

        if batch_count == 0:
            break

        start += 25
        time.sleep(1.2)

    return results

def run_public_jobs(target_min: int = None):
    print("=" * 68)
    print(" [LINKEDIN MINING PLANNER SCRAPER] - Multi-Query Engine")
    print("=" * 68)

    config = get_config()
    search_cfg = config.get("pencarian", {})
    export_cfg = config.get("ekspor", {})

    location = search_cfg.get("lokasi", "Indonesia")
    db_path = BASE_DIR / export_cfg.get("nama_file_database", "database_loker_tambang.sqlite")
    excel_path = BASE_DIR / export_cfg.get("nama_file_excel", "kontak_loker_planner_tambang.xlsx")
    storage = StorageManager(db_path=db_path, excel_path=excel_path)

    all_jobs = []
    seen_urns = set()

    queries = search_cfg.get("daftar_kata_kunci_pertambangan", DEFAULT_MINING_QUERIES)
    wajib_tambang = search_cfg.get("wajib_sektor_tambang", True)
    urutkan = search_cfg.get("urutkan_berdasarkan", "date_posted")
    sort_by_date = (str(urutkan).lower() in ["date_posted", "terbaru", "recent", "dd"])

    if target_min is None:
        target_min = search_cfg.get("target_minimal_data", 30)

    print(f"\n[*] Target Minimum Scrap : {target_min} lowongan")
    print(f"[*] Wilayah Target       : {location}")
    print(f"[*] Urutan Lowongan      : {'Paling Baru (Date Posted)' if sort_by_date else 'Paling Relevan'}")
    print(f"[*] Filter Wajib Tambang : {'Aktif' if wajib_tambang else 'Nonaktif (Semua Bidang)'}")
    print(f"[*] Mode Pengambilan     : 100% TANPA LOGIN (Menyerap teks deskripsi lengkap & kontak)")
    print(f"[*] Rangkaian Keyword    : {len(queries)} variasi kata kunci\n")

    for idx, q in enumerate(queries, 1):
        if len(all_jobs) >= target_min:
            break

        print(f"[{idx}/{len(queries)}] Mencari lowongan terbaru dengan kata kunci: '{q}'...")
        jobs = fetch_guest_jobs_for_query(
            keyword=q,
            location=location,
            max_per_query=20,
            seen_urns=seen_urns,
            sort_by_date=sort_by_date,
            wajib_tambang=wajib_tambang
        )
        print(f"    -> Ditemukan: {len(jobs)} lowongan valid pada keyword ini.")
        all_jobs.extend(jobs)
        print(f"    -> Akumulasi terkumpul: {len(all_jobs)} lowongan.")
        time.sleep(1.2)

    print(f"\n[✓] Selesai! Total lowongan planner pertambangan terkumpul: {len(all_jobs)}")

    if all_jobs:
        baru, duplikat = storage.save_to_sqlite(all_jobs)
        print(f"[*] SQLite: {baru} baru ditambahkan | {duplikat} data lama/duplikat.")
        excel_file = storage.export_all_to_excel()
        print(f"[✓] File Excel sukses diperbarui: {excel_file.name}")
        print(f"    Lokasi: {excel_file.resolve()}\n")

    return all_jobs

if __name__ == "__main__":
    run_public_jobs()
