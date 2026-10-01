import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PENGATURAN_FILE = BASE_DIR / "pengaturan.json"
ENV_FILE = BASE_DIR / ".env"
SESSION_FILE = BASE_DIR / "sesi_linkedin.json"

def load_env_file(filepath: Path) -> dict:
    env_vars = {}
    if not filepath.exists():
        return env_vars
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    env_vars[key.strip()] = val.strip().strip("'\"")
    except Exception as e:
        print(f"[!] Gagal membaca .env: {e}")
    return env_vars

def get_config() -> dict:
    config = {
        "linkedin_email": "",
        "linkedin_password": "",
        "linkedin_li_at": "",
        "linkedin_jsessionid": "",
        "pencarian": {
            "kata_kunci_utama": "planner",
            "lokasi": "Indonesia",
            "kata_kunci_tambahan_query": "",
            "urutkan_berdasarkan": "date_posted",
            "hanya_yang_mengandung_kata_loker": True,
            "filter_kata_loker": [
                "hiring", "lowongan", "loker", "recruitment", "rekrutmen",
                "dibutuhkan", "join our team", "we are hiring", "open position",
                "apply", "kirim cv", "send your cv", "kualifikasi", "requirements", "job vacancy"
            ]
        },
        "pengaturan_browser": {
            "tampilkan_browser": False,
            "maksimal_scroll": 10,
            "jeda_detik_per_scroll": 2.5,
            "timeout_halaman_detik": 45
        },
        "ekspor": {
            "simpan_ke_excel": True,
            "simpan_ke_sqlite": True,
            "nama_file_excel": "loker_planner_indonesia.xlsx",
            "nama_file_database": "database_loker.sqlite"
        }
    }

    # 1. Baca dari pengaturan.json jika ada
    if PENGATURAN_FILE.exists():
        try:
            with open(PENGATURAN_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                # Merge shallow & deep
                for k, v in json_data.items():
                    if isinstance(v, dict) and k in config:
                        config[k].update(v)
                    else:
                        config[k] = v
        except Exception as e:
            print(f"[!] Gagal membaca pengaturan.json: {e}")

    # 2. Overwrite dari .env jika diisi
    env_vars = load_env_file(ENV_FILE)
    if env_vars.get("LINKEDIN_EMAIL"):
        config["linkedin_email"] = env_vars["LINKEDIN_EMAIL"]
    if env_vars.get("LINKEDIN_PASSWORD"):
        config["linkedin_password"] = env_vars["LINKEDIN_PASSWORD"]
    if env_vars.get("LINKEDIN_LI_AT") and env_vars["LINKEDIN_LI_AT"] != "PASTE_COOKIE_LI_AT_DISINI":
        config["linkedin_li_at"] = env_vars["LINKEDIN_LI_AT"]
    if env_vars.get("KATA_KUNCI"):
        config["pencarian"]["kata_kunci_utama"] = env_vars["KATA_KUNCI"]
    if env_vars.get("LOKASI"):
        config["pencarian"]["lokasi"] = env_vars["LOKASI"]
    if env_vars.get("MAX_SCROLL"):
        try:
            config["pengaturan_browser"]["maksimal_scroll"] = int(env_vars["MAX_SCROLL"])
        except ValueError:
            pass
    if env_vars.get("TAMPILKAN_BROWSER"):
        config["pengaturan_browser"]["tampilkan_browser"] = env_vars["TAMPILKAN_BROWSER"].lower() in ["true", "1", "yes"]

    # Trim token & kredensial
    config["linkedin_email"] = config.get("linkedin_email", "").strip()
    config["linkedin_password"] = config.get("linkedin_password", "").strip()
    config["linkedin_li_at"] = config.get("linkedin_li_at", "").strip().strip('"').strip("'")
    return config

def validate_cookie(config: dict) -> bool:
    cookie = config.get("linkedin_li_at", "")
    if not cookie or cookie == "PASTE_COOKIE_LI_AT_DISINI" or len(cookie) < 20:
        return False
    return True

def load_session_cookies() -> list:
    """Membaca snapshot cookies sesi login yang tersimpan sebelumnya."""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            return []
    return []

def save_session_cookies(cookies: list):
    """Menyimpan snapshot cookies sesi login agar tidak perlu login ulang."""
    if not cookies:
        return
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
    except Exception as e:
        print(f"[!] Gagal menyimpan file sesi cookies: {e}")

def update_config_cookie(li_at: str, jsessionid: str = ""):
    """Memperbarui cookie li_at terbaru secara otomatis ke pengaturan.json."""
    if not PENGATURAN_FILE.exists() or not li_at:
        return
    try:
        with open(PENGATURAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["linkedin_li_at"] = li_at
        if jsessionid:
            data["linkedin_jsessionid"] = jsessionid
        with open(PENGATURAN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
