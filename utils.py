import re
from datetime import datetime, date

# Vietnamese headers usually exported by Airbnb
VN_HEADERS = {
    "confirmation_code": "Mã xác nhận",
    "listing": "Nhà/phòng cho thuê",
    "status": "Trạng thái đặt phòng",
    "guest_name": "Tên khách",
    "guest_contact": "Email, Số điện thoại",  # adjust nếu CSV bạn khác tên
    "start_date": "Ngày bắt đầu",
    "end_date": "Ngày kết thúc",
    "booking_date": "Đã đặt",
    "num_nights": "# đêm",
    "num_adults": "# người lớn",
    "num_children": "# trẻ em",
    "num_infants": "# trẻ sơ sinh",
    "income": "Thu nhập",
}

def parse_date_mixed(val):
    if val is None:
        return None
    if isinstance(val, date):
        return val
    s = str(val).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    try:
        return datetime.fromisoformat(s[:19]).date()
    except Exception:
        return None

def parse_vnd(val):
    if val is None:
        return None
    s = str(val).strip()
    s = s.replace("₫","").replace(",","").replace(".","").replace(" ","")
    if s in {"", "-"}:
        return None
    try:
        return int(s)
    except Exception:
        return None

# Mapping ngoại lệ (vd: Avalon D.3 -> AVA-403)
UNIT_MAPPING = {
    "D.3": "403",
    "E.3": "503",
    "D.1": "401",
}

def parse_building_and_unit(listing: str):
    if not listing:
        return (None, None)
    # Bắt "Avalon 2.2 ..." hoặc "Avalon D.3- ..."
    m = re.match(r"\s*([A-Za-zÀ-ỹ0-9]+)\s+([A-Za-z0-9]+(?:\.[A-Za-z0-9]+)?)", listing)
    if m:
        return (m.group(1), m.group(2))
    return (None, None)

def building_code_from_name(name: str):
    if not name: return None
    letters = "".join([c for c in name if c.isalpha()]).upper()
    return letters[:3] if letters else None

def unit_short_from_unit_number_auto(unit_number: str):
    if not unit_number:
        return None
    if unit_number in UNIT_MAPPING:
        return UNIT_MAPPING[unit_number]
    if "." in unit_number:
        a, b = unit_number.split(".", 1)
        if a.isdigit() and b.isdigit():
            return f"{int(a)}{int(b):02d}"
    return unit_number.replace(".", "")

    # Alias các tên cột có thể gặp trong file CSV (tiếng Việt/Anh)
HEADER_ALIASES = {
    "confirmation_code": ["Mã xác nhận", "Confirmation Code", "Confirmation code"],
    "listing": ["Nhà/phòng cho thuê", "Listing"],
    "status": ["Trạng thái đặt phòng", "Trạng thái", "Status"],
    "guest_name": ["Tên khách", "Tên của khách", "Guest Name", "Guest name"],
    "guest_contact": [
        "Liên hệ",  # <--- THÊM VÀO ĐÂY
        "Email, Số điện thoại", "Số điện thoại", "Điện thoại", "Phone", "Phone number",
        "Email", "E-mail", "Email address", "Contact",
        "Guest phone number", "Guest Phone"
    ],
    "start_date": ["Ngày bắt đầu", "Check-in", "Start Date", "Start date"],
    "end_date": ["Ngày kết thúc", "Check-out", "End Date", "End date"],
    "booking_date": ["Đã đặt", "Booking Date", "Booking date", "Created at"],
    "num_nights": ["# đêm", "Số đêm", "Nights"],
    "num_adults": ["# người lớn", "Adults"],
    "num_children": ["# trẻ em", "Children"],
    "num_infants": ["# trẻ sơ sinh", "Infants", "Babies"],
    "income": ["Thu nhập", "Tổng thu", "Total Payout (VND)", "Total payout (VND)", "Payout (VND)"]
}

def pick(df, logical_key: str):
    """Trả về tên cột thực tế trong df theo logical_key, ưu tiên alias xuất hiện đầu tiên."""
    names = HEADER_ALIASES.get(logical_key, [])
    for n in names:
        if n in df.columns:
            return n
    # fallback: dùng VN_HEADERS nếu tồn tại
    n = VN_HEADERS.get(logical_key)
    return n if n in df.columns else None

