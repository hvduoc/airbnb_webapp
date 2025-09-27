import re
from datetime import datetime, date, timedelta
from sqlmodel import Session, select
from models import Booking, Property
import requests

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

# Global room mapping dictionary - can be updated from UI
ROOM_MAPPING = {}

def update_room_mapping(mapping_dict):
    """Cập nhật room mapping từ UI"""
    global ROOM_MAPPING
    ROOM_MAPPING.clear()
    ROOM_MAPPING.update(mapping_dict)

def apply_room_mapping(listing_raw, room_mapping_data=None):
    """Áp dụng room mapping nếu có"""
    if not listing_raw:
        return listing_raw
        
    # Use provided mapping data or global ROOM_MAPPING
    mappings = {}
    if room_mapping_data and 'mappings' in room_mapping_data:
        mappings = room_mapping_data['mappings']
    else:
        mappings = ROOM_MAPPING
        
    if not mappings:
        return listing_raw
        
    # Tìm exact match trước
    if listing_raw in mappings:
        return mappings[listing_raw]
    
    # Tìm partial match (case-insensitive)
    listing_lower = listing_raw.lower()
    for airbnb_name, internal_code in mappings.items():
        if airbnb_name.lower() in listing_lower or listing_lower in airbnb_name.lower():
            return internal_code
            
    return listing_raw

def get_room_mapping_preview(df, room_mapping_data=None):
    """Preview kết quả room mapping trước khi import CSV DataFrame"""
    preview = []
    
    # Get listing column
    lst_col = pick(df, "listing")
    if not lst_col:
        return preview
    
    # Get mappings from room_mapping_data
    mappings = {}
    if room_mapping_data and 'mappings' in room_mapping_data:
        mappings = room_mapping_data['mappings']
    
    # Preview up to 10 rows
    for index, row in df.head(10).iterrows():
        original = str(row.get(lst_col, "")).strip()
        if not original:
            continue
            
        # Apply mapping if exists
        mapped_name = mappings.get(original, original)
        is_mapped = original != mapped_name
        
        preview.append({
            'original': original,
            'mapped_name': mapped_name,
            'mapped': is_mapped
        })
    
    return preview

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

def get_properties_stats(month: str, building_id: int | None = None):
    # Parse month to get start and end dates
    start_date = datetime.strptime(month, "%Y-%m").date()
    end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    with Session() as session:
        # Query bookings within the month
        bookings = session.exec(
            select(Booking).where(
                Booking.start_date <= end_date,
                Booking.end_date >= start_date
            )
        ).all()

        # Query properties
        properties = session.exec(
            select(Property).where(
                Property.building_id == building_id if building_id else True
            )
        ).all()

        # Calculate stats
        stats = []
        for prop in properties:
            prop_bookings = [b for b in bookings if b.property_id == prop.id]
            sold_nights = sum((min(b.end_date, end_date) - max(b.start_date, start_date)).days for b in prop_bookings)
            available_nights = (end_date - start_date).days + 1  # Total nights in the month

            stats.append({
                "property_id": prop.id,
                "available_nights": available_nights,
                "sold_nights": sold_nights
            })

        return stats

def fetch_buildings():
    """Fetch building data from the API."""
    try:
        response = requests.get("http://127.0.0.1:8000/buildings")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching buildings: {e}")
        return []

def fetch_properties():
    """Fetch property data from the API."""
    try:
        response = requests.get("http://127.0.0.1:8000/properties")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching properties: {e}")
        return []
