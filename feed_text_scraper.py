import sys
import time
import random
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

from camoufox.sync_api import Camoufox
from config_manager import (
    get_config, validate_cookie, load_session_cookies,
    save_session_cookies, update_config_cookie, BASE_DIR, PENGATURAN_FILE
)
from extractor import parse_post_data
from storage import StorageManager

def ensure_linkedin_login(page, context, config: dict, browser_cfg: dict) -> bool:
    """
    Memastikan browser berada dalam status login di LinkedIn.
    Alur:
    1. Cek sesi aktif dari file sesi_linkedin.json jika ada.
    2. Jika belum login atau sesi lama habis, bersihkan semua cookie (clear_cookies).
    3. Buka halaman login LinkedIn dengan context bersih.
    4. Masukkan email & password secara otomatis.
    5. Tangani tantangan 2FA/PIN OTP jika diminta.
    6. Simpan snapshot sesi cookies otomatis ke sesi_linkedin.json.
    """
    email = config.get("linkedin_email", "").strip()
    password = config.get("linkedin_password", "").strip()
    timeout_ms = browser_cfg.get("timeout_halaman_detik", 45) * 1000

    # 1. Cek apakah ada file sesi login yang tersimpan sebelumnya
    saved_cookies = load_session_cookies()
    if saved_cookies:
        print("[*] Memeriksa status sesi login yang tersimpan...")
        try:
            context.add_cookies(saved_cookies)
            page.goto("https://www.linkedin.com/feed/", timeout=min(timeout_ms, 20000), wait_until="domcontentloaded")
            time.sleep(3)
            curr_url = page.url
            if "feed" in curr_url and not any(k in curr_url for k in ["login", "uas", "checkpoint", "authwall"]):
                print(f"[*] Halaman aktif: {curr_url}")
                print("[✓] Sesi login LinkedIn aktif! Berhasil masuk tanpa perlu login ulang.\n")
                save_session_cookies(context.cookies())
                return True
        except Exception:
            pass

    # 2. Cek apakah ada cookie 'li_at' yang diisi di pengaturan.json / .env
    li_at_cookie = config.get("linkedin_li_at", "").strip()
    if li_at_cookie and li_at_cookie != "PASTE_COOKIE_LI_AT_DISINI" and len(li_at_cookie) > 20:
        print("[*] Mencoba login menggunakan cookie 'li_at' dari konfigurasi...")
        try:
            cookies_to_add = [
                {
                    "name": "li_at",
                    "value": li_at_cookie,
                    "domain": ".www.linkedin.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": True
                }
            ]
            jsessionid = config.get("linkedin_jsessionid", "").strip()
            if jsessionid:
                cookies_to_add.append({
                    "name": "JSESSIONID",
                    "value": jsessionid,
                    "domain": ".www.linkedin.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False
                })
            context.add_cookies(cookies_to_add)
            page.goto("https://www.linkedin.com/feed/", timeout=min(timeout_ms, 20000), wait_until="domcontentloaded")
            time.sleep(3)
            curr_url = page.url
            if "feed" in curr_url and not any(k in curr_url for k in ["login", "uas", "checkpoint", "authwall"]):
                print(f"[*] Halaman aktif: {curr_url}")
                print("[✓] Login dengan cookie 'li_at' berhasil! Sesi login disimpan.\n")
                save_session_cookies(context.cookies())
                return True
            else:
                print("[!] Cookie 'li_at' sudah kedaluwarsa atau tidak valid, melanjutkan ke metode login akun...")
        except Exception as e:
            print(f"[!] Gagal menerapkan cookie 'li_at': {e}")

    # 3. Bersihkan seluruh cookie di browser context jika kedua metode di atas tidak berhasil
    try:
        context.clear_cookies()
    except Exception:
        pass

    # 3. Kredensial email dan password
    if not email or not password:
        print("\n[!] Kredensial email dan password LinkedIn belum diisi di 'pengaturan.json'")
        print("[+] Silakan masukkan Akun LinkedIn Anda untuk login otomatis:")
        try:
            email = input("    -> Email / Nomor HP LinkedIn : ").strip()
            password = input("    -> Password LinkedIn         : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Login dibatalkan.")
            return False

        if not email or not password:
            print("[!] Email atau password tidak boleh kosong.")
            return False

        simpan = input("    -> Simpan ke 'pengaturan.json' agar otomatis selanjutnya? (y/n) [y]: ").strip().lower()
        if simpan in ["", "y", "ya", "yes"]:
            if PENGATURAN_FILE.exists():
                try:
                    import json
                    with open(PENGATURAN_FILE, "r", encoding="utf-8") as f:
                        p_data = json.load(f)
                    p_data["linkedin_email"] = email
                    p_data["linkedin_password"] = password
                    with open(PENGATURAN_FILE, "w", encoding="utf-8") as f:
                        json.dump(p_data, f, indent=2)
                    print("    [✓] Kredensial berhasil disimpan ke 'pengaturan.json'!\n")
                except Exception as e:
                    print(f"    [!] Gagal menyimpan ke pengaturan.json: {e}\n")

    print(f"\n[*] Melakukan login otomatis dengan Akun LinkedIn: {email}...")
    try:
        page.goto("https://www.linkedin.com/login", timeout=timeout_ms, wait_until="domcontentloaded")
        time.sleep(2.5)

        # Cari input email dan password yang visible
        email_input = page.locator('input[type="email"]').locator("visible=true").first
        pass_input = page.locator('input[type="password"]').locator("visible=true").first

        if not email_input.is_visible() or not pass_input.is_visible():
            print("[!] Elemen formulir login tidak ditemukan pada halaman.")
            return False

        email_input.fill(email)
        time.sleep(0.5)
        pass_input.fill(password)
        time.sleep(0.5)

        print("[*] Mengirim formulir login...")
        sign_in_btn = page.locator('button:has-text("Sign in"):not(:has-text("Apple")):not(:has-text("Microsoft")), button:has-text("Masuk"):not(:has-text("Apple")), button[type="submit"]').locator("visible=true").first
        if sign_in_btn.is_visible():
            sign_in_btn.click()
        else:
            pass_input.press("Enter")

        # Tunggu sampai navigasi berpindah dari halaman login ke feed / checkpoint
        for _ in range(25):
            time.sleep(1)
            curr = page.url
            if "feed" in curr or "mynetwork" in curr or "checkpoint" in curr or "challenge" in curr:
                break

        # Cek apakah ada prompt verifikasi PIN OTP / Suspicious Login di halaman secara aman
        body_text_lower = ""
        for _ in range(3):
            try:
                body_text_lower = page.locator("body").inner_text(timeout=3000).lower()
                break
            except Exception:
                time.sleep(1.5)

        is_verification_page = (
            page.locator('#input__email_verification_pin, input[name="pin"]').count() > 0 or
            "verification" in body_text_lower or
            "verifikasi" in body_text_lower or
            "checkpoint" in page.url or
            "challenge" in page.url
        )

        if is_verification_page:
            print("\n" + "=" * 65)
            print(" [🔐 VERIFIKASI KEAMANAN LINKEDIN]")
            print(f" -> LinkedIn meminta kode verifikasi 6 digit yang dikirim ke:")
            print(f"    {email}")
            print("=" * 65)
            try:
                kode_otp = input("\n[?] Masukkan 6 digit kode verifikasi dari email Anda: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n[!] Dibatalkan oleh pengguna.")
                return False

            if kode_otp:
                pin_input = page.locator('#input__email_verification_pin, input[name="pin"]').locator("visible=true").first
                if pin_input.is_visible():
                    pin_input.fill(kode_otp)
                    time.sleep(0.5)
                    pin_input.press("Enter")
                else:
                    btn_pin = page.locator('button:has-text("Submit"), button:has-text("Kirim"), button[type="submit"]').locator("visible=true").first
                    if btn_pin.is_visible():
                        btn_pin.click()
                print("[*] Memverifikasi kode PIN...")
                time.sleep(6)

        # Tunggu sampai berpindah ke feed
        for _ in range(5):
            curr_url = page.url
            if "feed" in curr_url or "mynetwork" in curr_url:
                break
            time.sleep(1)

        curr_url = page.url
        # Verifikasi akhir status login
        if "feed" in curr_url or "mynetwork" in curr_url or ("login" not in curr_url and "uas" not in curr_url and "checkpoint" not in curr_url):
            print(f"[✓] Login LinkedIn Berhasil! (Halaman aktif: {curr_url})\n")
            all_cookies = context.cookies()
            save_session_cookies(all_cookies)
            return True
        else:
            err_msg_el = page.locator('.alert-content, #error-for-username, #error-for-password, div[error-for]').first
            err_text = err_msg_el.inner_text().strip() if err_msg_el.is_visible() else "Gagal verifikasi login. Cek kembali email, password, atau kode verifikasi."
            print(f"\n[!] Gagal login LinkedIn: {err_text}")
            return False

    except Exception as e:
        print(f"[!] Terjadi kesalahan saat login: {e}")
        return False

def run_feed_scraper():
    print("=" * 65)
    print(" [LINKEDIN POSTINGAN TEKS SCRAPER] - Recruiter Feed Timeline")
    print("=" * 65)

    config = get_config()

    search_cfg = config["pencarian"]
    browser_cfg = config["pengaturan_browser"]
    export_cfg = config["ekspor"]

    kata_kunci = search_cfg.get("kata_kunci_utama", "planner")
    lokasi = search_cfg.get("lokasi", "Indonesia")
    query_tambahan = search_cfg.get("kata_kunci_tambahan_query", "").strip()

    search_query = f"{kata_kunci} {lokasi} {query_tambahan}".strip()
    sort_by = search_cfg.get("urutkan_berdasarkan", "date_posted")
    max_scroll = browser_cfg.get("maksimal_scroll", 10)
    headless = not browser_cfg.get("tampilkan_browser", False)
    scroll_delay = browser_cfg.get("jeda_detik_per_scroll", 2.5)

    db_path = BASE_DIR / export_cfg.get("nama_file_database", "database_loker_tambang.sqlite")
    excel_path = BASE_DIR / export_cfg.get("nama_file_excel", "kontak_loker_planner_tambang.xlsx")
    storage = StorageManager(db_path=db_path, excel_path=excel_path)

    default_queries = [
        "planner tambang",
        "mine planner",
        "maintenance planner tambang",
        "planner batubara",
        "planner nikel"
    ]
    queries = search_cfg.get("daftar_kata_kunci_pertambangan", default_queries)
    target_min = search_cfg.get("target_minimal_data", 20)

    print(f"\n[+] Wilayah Target       : {lokasi}")
    print(f"[+] Target Minimum Scrap : {target_min} postingan")
    print(f"[+] Daftar Keyword       : {len(queries)} variasi kata kunci tambang")
    print(f"[+] Maksimal Scroll      : {max_scroll} kali per keyword")
    print(f"[+] Mode Tampilan        : {'Headless (Latar Belakang)' if headless else 'Jendela Browser Aktif'}\n")

    print("[*] Meluncurkan browser anti-detect Camoufox...")

    with Camoufox(headless=headless) as browser:
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="id-ID"
        )

        page = context.new_page()

        # Pastikan login berhasil (otomatis via email & password)
        if not ensure_linkedin_login(page, context, config, browser_cfg):
            return False

        collected_posts = {}
        filter_keywords = search_cfg.get("filter_kata_loker", [])
        check_filter = search_cfg.get("hanya_yang_mengandung_kata_loker", True)
        wajib_sektor_tambang = search_cfg.get("wajib_sektor_tambang", True)
        wajib_ada_kontak = search_cfg.get("hanya_yang_ada_kontak_email_atau_hp", True)

        js_script = r"""
        () => {
            // Fungsi decoding ID aktivitas LinkedIn dari binary protobuf
            function decodeLinkedInActivity(encodedStr) {
                try {
                    let b64 = encodedStr.replace(/-/g, '+').replace(/_/g, '/');
                    while (b64.length % 4 !== 0) b64 += '=';
                    const bin = atob(b64);
                    const bytes = [];
                    for (let i = 0; i < bin.length; i++) bytes.push(bin.charCodeAt(i));
                    
                    let i = 0;
                    while (i < bytes.length) {
                        const tag = bytes[i++];
                        const wire = tag & 7;
                        if (wire === 2) {
                            if (i >= bytes.length) break;
                            const len = bytes[i++];
                            if (bytes[i] === 8) {
                                let val = 0n;
                                let shift = 0n;
                                let j = i + 1;
                                while (j < i + len) {
                                    const b = BigInt(bytes[j++]);
                                    val |= (b & 0x7fn) << shift;
                                    shift += 7n;
                                    if (!(b & 0x80n)) break;
                                }
                                if (val > 0n) {
                                    const actId = val >> 1n;
                                    if (actId > 1000000000000000000n) {
                                        return actId.toString();
                                    }
                                }
                            }
                            i += len;
                        } else if (wire === 0) {
                            while (i < bytes.length && (bytes[i] & 0x80)) i++;
                            i++;
                        } else {
                            break;
                        }
                    }
                } catch(e) {}
                return '';
            }

            // Perluas semua teks 'see more' / 'lihat selengkapnya' / '... more'
            const buttons = document.querySelectorAll('button, span[role="button"]');
            buttons.forEach(btn => {
                const txt = (btn.innerText || btn.getAttribute('aria-label') || '').toLowerCase();
                if (txt.includes('see more') || txt.includes('lihat lainnya') || txt.includes('lihat selengkapnya') || txt.includes('more') || txt.includes('… more')) {
                    try { btn.click(); } catch(e){}
                }
            });

            // Seleksi card postingan modern (div[role="listitem"] atau reusable result container)
            const listItems = Array.from(document.querySelectorAll('div[role="listitem"], li.reusable-search__result-container, div.feed-shared-update-v2'));
            // Ambil hanya card terbawah yang memiliki isi teks memadai (>50 char)
            const validCards = listItems.filter(c => c.innerText && c.innerText.length > 50 && c.querySelectorAll('div[role="listitem"]').length === 0);

            const items = [];

            validCards.forEach((c, i) => {
                const fullText = c.innerText || '';
                const allAnchors = Array.from(c.querySelectorAll('a'));
                const links = allAnchors.map(a => a.href);

                const profileLink = links.find(h => (h.includes('/in/') || h.includes('/company/'))) || '';
                let postLink = links.find(h => h.includes('/feed/update/') || h.includes('/posts/') || h.includes('/pulse/')) || '';

                // Ekstraksi langsung link postingan feed melalui decoding protobuf key pada replaceableCommentTools
                if (!postLink) {
                    const match = c.outerHTML.match(/([A-Za-z0-9_+\-/=]{10,40})-replaceableCommentTools/);
                    if (match) {
                        const actId = decodeLinkedInActivity(match[1]);
                        if (actId) {
                            postLink = `https://www.linkedin.com/feed/update/urn:li:activity:${actId}/`;
                        }
                    }
                }

                const lines = fullText.split('\n').map(l => l.trim()).filter(Boolean);
                let author = lines.length > 0 ? lines[0] : 'Recruiter / User';
                if (author.toLowerCase().includes('feed post') && lines.length > 1) {
                    author = lines[1];
                }

                let headline = lines.length > 2 ? lines[2] : '-';
                if (headline.includes('•') && lines.length > 3) {
                    headline = lines[3];
                }

                const timeMatch = fullText.match(/\b(\d+[mhdwy]|edited|diedit|\d+\s+(?:menit|jam|hari|minggu|bulan)\s+lalu)\b/i);
                const tanggal = timeMatch ? timeMatch[0] : '-';

                const compKey = c.getAttribute('componentkey') || '';
                const urn = compKey || (postLink || `${author}_${i}`);

                items.push({
                    urn: urn,
                    post_url: postLink,
                    tanggal: tanggal,
                    nama_poster: author,
                    headline_poster: headline,
                    link_profil_poster: profileLink,
                    teks: fullText
                });
            });

            return items;
        }
        """

        for q_idx, q_text in enumerate(queries, 1):
            if len(collected_posts) >= target_min:
                print(f"[✓] Target minimum ({target_min}) tercapai!")
                break

            # Bangun query pencarian cerdas agar hasil postingan maksimal
            clean_q = q_text.strip()
            # Jika query sudah mengandung terminologi Indonesia/tambang, tidak perlu memaksa tambahan string
            if any(w in clean_q.lower() for w in ["tambang", "nikel", "batubara", "loker", "lowongan"]):
                search_query_str = clean_q
            else:
                search_query_str = f"{clean_q} {lokasi}".strip()

            target_url = f'https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(search_query_str)}'
            if sort_by and sort_by != "relevance":
                target_url += f'&sortBy=%22{sort_by}%22'

            print(f"\n[{q_idx}/{len(queries)}] Mencari: '{clean_q}'...")

            try:
                page.goto(target_url, timeout=browser_cfg.get("timeout_halaman_detik", 45) * 1000, wait_until="domcontentloaded")
                time.sleep(3.5)
            except Exception as e:
                print(f"    [!] Gagal memuat keyword '{q_text}': {e}")
                continue

            current_url = page.url
            if "login" in current_url or "uas" in current_url or "checkpoint" in current_url:
                print("\n[!] Sesi LinkedIn terputus atau memerlukan verifikasi ulang.")
                print("-------------------------------------------------------------------")
                print("Tips Solusi:")
                print("1. Pastikan email dan password di 'pengaturan.json' sudah benar.")
                print("2. Hapus file 'sesi_linkedin.json' jika ingin login ulang dari awal.")
                print("-------------------------------------------------------------------\n")
                return False

            for scroll_i in range(1, max_scroll + 1):
                try:
                    raw_items = page.evaluate(js_script)
                    for it in raw_items:
                        urn_key = it.get("urn")
                        if urn_key and urn_key not in collected_posts:
                            parsed = parse_post_data(
                                it,
                                filter_keywords=filter_keywords,
                                check_filter=check_filter,
                                wajib_sektor_tambang=wajib_sektor_tambang,
                                wajib_ada_kontak=wajib_ada_kontak
                            )
                            if parsed:
                                parsed["tipe_sumber"] = "Postingan Teks Tambang"
                                parsed["posisi_pekerjaan"] = parsed.get("kategori_planner", "Planner Tambang")
                                parsed["lokasi"] = lokasi
                                collected_posts[urn_key] = parsed
                                print(f"    [+] KONTAK DITEMUKAN: [{parsed['kategori_planner']}] oleh '{parsed['nama_poster']}'")
                                if parsed['kontak_wa'] != "-":
                                    print(f"        -> No HP/WA : {parsed['kontak_wa']}")
                                if parsed['kontak_email'] != "-":
                                    print(f"        -> Email    : {parsed['kontak_email']}")
                                if parsed['post_url']:
                                    print(f"        -> Link     : {parsed['post_url']}")
                except Exception as e:
                    pass

                # Scroll container utama workspace LinkedIn serta window untuk trigger loading data baru
                try:
                    page.evaluate(r"""() => {
                        const scroller = document.querySelector('main#workspace') || document.querySelector('main') || document.documentElement;
                        scroller.scrollTop += scroller.clientHeight * 1.5;
                        scroller.dispatchEvent(new Event('scroll'));
                        window.scrollBy(0, window.innerHeight);
                    }""")
                except Exception:
                    time.sleep(1)
                time.sleep(scroll_delay + random.uniform(0.3, 1.0))

        print(f"\n[✓] Selesai scraping feed teks! Total {len(collected_posts)} kontak loker planner tambang terkumpul.")

        if collected_posts:
            posts_list = list(collected_posts.values())
            baru, duplikat = storage.save_to_sqlite(posts_list)
            print(f"[*] SQLite: {baru} baru disimpan | {duplikat} data lama/duplikat.")
            excel_file = storage.export_all_to_excel()
            print(f"[✓] File Excel berhasil diperbarui: {excel_file.name}")
            print(f"    Lokasi: {excel_file.resolve()}\n")
            return True
        else:
            print("[!] Tidak ada postingan teks yang memenuhi kriteria filter loker.")
            return False

if __name__ == "__main__":
    run_feed_scraper()
