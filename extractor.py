import re
from typing import Dict, List, Optional

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_WA_REGEX = re.compile(r'(?:\+62|62|08)[0-9\s\-]{8,15}')

# Keyword khusus sektor pertambangan dan alat berat tambang
MINING_KEYWORDS = [
    r'\btambang\b', r'\bpertambangan\b', r'\bmining\b', r'\bmine\b',
    r'\bcoal\b', r'\bbatubara\b', r'\bbatu\s+bara\b', r'\bnikel\b', r'\bnickel\b',
    r'\bmineral\b', r'\bgold\b', r'\bemas\b', r'\bbauxite\b', r'\bbauksit\b',
    r'\balat\s+berat\b', r'\bheavy\s+equipment\b', r'\bexcavator\b', r'\bdump\s+truck\b',
    r'\bdozer\b', r'\bgrader\b', r'\bpama\b', r'\bbuma\b', r'\badaro\b',
    r'\bkideco\b', r'\bthiess\b', r'\bmacmahon\b', r'\bberau\s+coal\b',
    r'\bbukit\s+asam\b', r'\bptba\b', r'\bfreeport\b', r'\bvale\b',
    r'\bharita\b', r'\bantam\b', r'\bdarma\s+henwa\b', r'\bsaptaindra\b',
    r'\bsims\b', r'\bsis\b', r'\bbib\b', r'\bjobsite\b', r'\bmine\s+site\b',
    r'\bsite\s+(?:tambang|nikel|batubara|mining|pit)\b', r'\bpit\b',
    r'\bhauling\b', r'\bcrusher\b', r'\bjetty\b', r'\bsmelter\b',
    r'\bmorowali\b', r'\bkaltim\b', r'\bkalsel\b', r'\bkalbar\b',
    r'\bkalteng\b', r'\bhalmahera\b', r'\bwedabay\b', r'\bsorowako\b',
    r'\bkolaka\b', r'\boverburden\b', r'\bstp\b', r'\bltp\b',
    r'\bkomatsu\b', r'\bcaterpillar\b', r'\bhitachi\b', r'\bscania\b', r'\bvolvo\b'
]

PLANNER_TYPES = {
    "Maintenance Planner Alat Berat (Mining)": [
        r'\bmaintenance\s+planner\b', r'\bplant\s+planner\b', r'\balat\s+berat\b',
        r'\bheavy\s+equipment\b', r'\bperawatan\b', r'\bfleet\s+planner\b'
    ],
    "Mine Planner (Short/Long Term)": [
        r'\bmine\s+planner\b', r'\bmining\s+planner\b', r'\bshort\s+term\s+planner\b',
        r'\blong\s+term\s+planner\b', r'\bstp\b', r'\bltp\b', r'\bpit\s+planner\b'
    ],
    "Production / Pit Planner Tambang": [
        r'\bproduction\s+planner\b', r'\bdrill.*blast\b', r'\bhauling\s+planner\b',
        r'\bcoal\s+processing\s+planner\b'
    ],
    "Supply Chain / Logistics Site Tambang": [
        r'\bmaterial\s+planner\b', r'\binventory\s+planner\b', r'\blogistics?\s+planner\b',
        r'\bsupply\s+chain\s+planner\b'
    ],
    "Project Planner Tambang": [
        r'\bproject\s+planner\b', r'\bproject\s+scheduler\b', r'\bprimavera\b'
    ]
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_emails(text: str) -> List[str]:
    if not text:
        return []
    matches = EMAIL_REGEX.findall(text)
    cleaned = []
    for m in matches:
        m_lower = m.lower()
        if not any(m_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]):
            if m_lower not in cleaned:
                cleaned.append(m)
    return cleaned

def extract_phones(text: str) -> List[str]:
    if not text:
        return []
    matches = PHONE_WA_REGEX.findall(text)
    cleaned = []
    for m in matches:
        raw_digits = re.sub(r'[\s\-]', '', m)
        if 9 <= len(raw_digits) <= 14:
            if m.strip() not in cleaned:
                cleaned.append(m.strip())
    return cleaned

def extract_apply_links(text: str) -> List[str]:
    if not text:
        return []
    urls = re.findall(r'https?://[^\s<>"]+', text)
    cleaned = []
    for u in urls:
        u_clean = u.rstrip('.,;)"\'')
        u_lower = u_clean.lower()
        if any(dom in u_lower for dom in ['lnkd.in', 'forms.gle', 'google.com/forms', 'bit.ly', 's.id', 'wa.me', 'career', 'recruitment', 'job', 'apply']):
            if u_clean not in cleaned:
                cleaned.append(u_clean)
    return cleaned

def is_mining_sector(text: str) -> bool:
    """
    Memverifikasi secara ketat bahwa postingan / loker berasal dari sektor pertambangan,
    alat berat tambang, site eksplorasi, mineral, nikel, batubara, dll.
    """
    text_lower = text.lower()
    for kw_pattern in MINING_KEYWORDS:
        if re.search(kw_pattern, text_lower):
            return True
    return False

def detect_planner_category(text: str) -> str:
    text_lower = text.lower()
    detected = []
    for category, patterns in PLANNER_TYPES.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                detected.append(category)
                break
    if detected:
        return ", ".join(detected)
    if "planner" in text_lower:
        return "Planner Tambang (General)"
    return "Pertambangan Lainnya"

def is_job_posting(text: str, filter_keywords: List[str]) -> bool:
    text_lower = text.lower()
    for kw in filter_keywords:
        if kw.lower() in text_lower:
            return True
    return False

def parse_post_data(
    raw_data: dict,
    filter_keywords: List[str],
    check_filter: bool = True,
    wajib_sektor_tambang: bool = True,
    wajib_ada_kontak: bool = True
) -> Optional[dict]:
    text = clean_text(raw_data.get("teks", ""))
    if not text:
        return None

    # 1. Verifikasi Sektor Pertambangan
    if wajib_sektor_tambang and not is_mining_sector(text + " " + raw_data.get("headline_poster", "")):
        return None

    # 2. Verifikasi Kata Kunci Hiring/Loker
    if check_filter and not is_job_posting(text, filter_keywords):
        return None

    emails = extract_emails(text)
    phones = extract_phones(text)
    apply_links = extract_apply_links(text)

    # 3. Verifikasi Keberadaan Kontak (Email, Nomor HP/WA, ATAU Link Lamaran/Form)
    if wajib_ada_kontak and not emails and not phones and not apply_links:
        return None

    category = detect_planner_category(text)

    # Pastikan post_url adalah link langsung ke postingan feed LinkedIn
    post_url = raw_data.get("post_url", "").strip()
    if not post_url and apply_links:
        post_url = apply_links[0]

    return {
        "post_urn": raw_data.get("urn", ""),
        "post_url": post_url,
        "tanggal_post": raw_data.get("tanggal", "-"),
        "nama_poster": raw_data.get("nama_poster", "Tidak diketahui"),
        "headline_poster": raw_data.get("headline_poster", "-"),
        "link_profil_poster": raw_data.get("link_profil_poster", ""),
        "kategori_planner": category,
        "kontak_email": ", ".join(emails) if emails else ("Link Form: " + apply_links[0] if apply_links and not phones else "-"),
        "kontak_wa": ", ".join(phones) if phones else "-",
        "isi_teks_lengkap": text
    }
