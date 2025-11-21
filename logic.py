import os
import streamlit as st
from datetime import datetime
from pytz import timezone
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from lunardate import LunarDate

# --- 1. CONSTANTS & DATA ---
THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

DS_TIET_KHI = [
    "Xuân phân", "Thanh minh", "Cốc vũ", "Lập hạ", "Tiểu mãn", "Mang chủng",
    "Hạ chí", "Tiểu thử", "Đại thử", "Lập thu", "Xử thử", "Bạch lộ",
    "Thu phân", "Hàn lộ", "Sương giáng", "Lập đông", "Tiểu tuyết", "Đại tuyết",
    "Đông chí", "Tiểu hàn", "Đại hàn", "Lập xuân", "Vũ thủy", "Kinh trập"
]

DATA_TRUC = [
    {"ten": "Kiến", "tot": "Xuất hành, giá thú, mưu sự, may mặc, làm nhà, khai trương.", "xau": "Động thổ, đào ao, khai hoang."},
    {"ten": "Trừ",  "tot": "Cúng tế, giải oan, chữa bệnh, thẩm mỹ, dọn dẹp nhà cửa.", "xau": "Cưới hỏi, đi xa, ký kết, động thổ."},
    {"ten": "Mãn",  "tot": "Cúng tế, cầu tài, khai trương, xuất hành, may mặc.", "xau": "Kiện tụng, tranh chấp, nhậm chức, cưới hỏi."},
    {"ten": "Bình", "tot": "Sửa nhà, nhập trạch, cưới hỏi, đi xa, làm đường.", "xau": "Đào mương, thưa kiện, tranh chấp pháp lý."},
    {"ten": "Định", "tot": "Nhập học, mua bán, động thổ, an táng, cầu tài.", "xau": "Tố tụng, xuất quân, chuyển chỗ ở."},
    {"ten": "Chấp", "tot": "Lập khế ước, sửa nhà, trồng trọt, tế lễ, cầu phúc.", "xau": "Xuất vốn, chuyển nhà, đi xa, mở kho."},
    {"ten": "Phá",  "tot": "Phá dỡ nhà cũ, chữa bệnh, săn bắt.", "xau": "Cưới hỏi, khai trương, động thổ, mua bán nhà."},
    {"ten": "Nguy", "tot": "Cúng tế, san đường, sửa nhà (nhẹ), an táng.", "xau": "Đi thuyền, leo núi, cưới hỏi, khởi công."},
    {"ten": "Thành", "tot": "Khai trương, nhập học, giá thú, dọn nhà, giao dịch.", "xau": "Kiện tụng, tranh chấp, đánh bạc."},
    {"ten": "Thu",  "tot": "Thu nợ, mua súc vật, cấy gặt, xây kho, nhập học.", "xau": "Mai táng, xuất vốn, khám chữa bệnh, động thổ."},
    {"ten": "Khai", "tot": "Cưới hỏi, khai trương, động thổ, nhập trạch, xuất hành.", "xau": "Chôn cất, tranh chấp, kiện tụng."},
    {"ten": "Bế",   "tot": "Đắp đập, xây tường, an táng, lấp hang lỗ.", "xau": "Đi xa, chữa mắt, cưới hỏi, khai trương."}
]

DATA_GIO_HOANG_DAO = {
    0: [0, 1, 3, 5, 7, 9], 1: [2, 4, 5, 7, 9, 10], 2: [0, 1, 4, 7, 9, 10],
    3: [0, 2, 4, 6, 8, 10], 4: [2, 4, 5, 7, 9, 10], 5: [1, 4, 6, 8, 10, 0],
    6: [0, 1, 3, 5, 7, 9], 7: [2, 4, 5, 7, 9, 10], 8: [0, 1, 4, 7, 9, 10],
    9: [0, 2, 4, 6, 8, 10], 10: [2, 4, 5, 7, 9, 10], 11: [1, 4, 6, 8, 10, 0]
}

LUC_XUNG = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
SAT_CHU = {1: 5, 2: 0, 3: 7, 4: 3, 5: 8, 6: 10, 7: 11, 8: 1, 9: 6, 10: 9, 11: 2, 12: 4}

# --- DỮ LIỆU SAO CHIẾU MỆNH (Nâng cấp mới) ---
# Tính chất: 1=Tốt, -1=Xấu, 0=Trung tính
SAO_PROPERTIES = {
    "Thái Dương": {"loai": 1, "desc": "Rồng lên mây, tài lộc thăng tiến, vạn sự may mắn (Tốt nhất cho Nam)."},
    "Thái Âm": {"loai": 1, "desc": "Hạnh phúc trọn vẹn, tiền tài danh vọng, tốt cho việc bất động sản (Tốt nhất cho Nữ)."},
    "Mộc Đức": {"loai": 1, "desc": "Vinh hoa phú quý, công việc thuận lợi, có tin vui về hôn nhân, con cái."},
    "Thủy Diệu": {"loai": 0, "desc": "Phước lộc tinh, đi xa làm ăn tốt, nhưng kỵ tháng 4, 8 âm lịch (Cẩn thận sông nước)."},
    "Thổ Tú": {"loai": 0, "desc": "Ách Tinh, cẩn thận tiểu nhân, xuất hành không thuận, kỵ tháng 4, 8 âm lịch."},
    "Vân Hớn": {"loai": 0, "desc": "Hung tinh nhẹ, phòng thương tật, kiện tụng, nóng nảy mồm miệng. Kỵ tháng 2, 8."},
    "Thái Bạch": {"loai": -1, "desc": "Hao tài tốn của, đề phòng đau ốm, kỵ màu trắng. (Xấu nhất trong các sao)."},
    "La Hầu": {"loai": -1, "desc": "Khẩu thiệt tinh, thị phi, kiện tụng, bệnh về mắt, máu huyết (Rất xấu cho Nam)."},
    "Kế Đô": {"loai": -1, "desc": "Hung tinh, dễ gặp tai nạn, bệnh tật, thị phi, buồn rầu (Rất xấu cho Nữ)."}
}

# Bảng tra cứu sao theo số dư tuổi âm lịch chia cho 9
# Key: (Tuổi âm % 9) -> Value: [Sao Nam, Sao Nữ]
SAO_LOOKUP = {
    1: ["La Hầu", "Kế Đô"],    # 10, 19, 28...
    2: ["Thổ Tú", "Vân Hớn"],  # 11, 20, 29...
    3: ["Thủy Diệu", "Mộc Đức"],# 12, 21, 30...
    4: ["Thái Bạch", "Thái Âm"],# 13, 22, 31...
    5: ["Thái Dương", "Thổ Tú"],# 14, 23, 32...
    6: ["Vân Hớn", "La Hầu"],  # 15, 24, 33...
    7: ["Kế Đô", "Thái Dương"],# 16, 25, 34...
    8: ["Thái Âm", "Thái Bạch"],# 17, 26, 35...
    0: ["Mộc Đức", "Thủy Diệu"] # 9, 18, 27, 36...
}


# --- 2. HÀM XỬ LÝ ---
@st.cache_resource
def load_astronomy_data():
    if not os.path.exists('de421.bsp'):
        load('de421.bsp')
    return load.timescale(), load('de421.bsp')

def get_tiet_khi(date_obj):
    ts, eph = load_astronomy_data()
    if date_obj.tzinfo is None:
        tz = timezone('Asia/Ho_Chi_Minh')
        date_obj = tz.localize(date_obj)
    t = ts.from_datetime(date_obj)
    earth, sun = eph['earth'], eph['sun']
    astrometric = earth.at(t).observe(sun).apparent()
    _, lon, _ = astrometric.frame_latlon(ecliptic_frame)
    index = int(lon.degrees // 15)
    return DS_TIET_KHI[index], lon.degrees

def get_can_chi(can, chi):
    return f"{THIEN_CAN[can]} {DIA_CHI[chi]}"

def tinh_can_chi_ngay_julian(d, m, y):
    a = (14 - m) // 12
    y_j = y + 4800 - a
    m_j = m + 12 * a - 3
    jdn = d + (153 * m_j + 2) // 5 + 365 * y_j + y_j // 4 - y_j // 100 + y_j // 400 - 32045
    return (jdn + 9) % 10, (jdn + 1) % 12

def check_ngay_hoang_dao(thang_am, chi_ngay_idx):
    khoi_thanh_long = ((thang_am - 1) % 6) * 2
    return ((chi_ngay_idx - khoi_thanh_long + 12) % 12) in [0, 1, 4, 5, 7, 10]

def lay_gio_hoang_dao(chi_ngay_idx):
    ds_indices = DATA_GIO_HOANG_DAO.get(chi_ngay_idx, [])
    ket_qua = []
    for chi_gio in ds_indices:
        start = (chi_gio * 2 - 1) % 24
        end = (chi_gio * 2 + 1) % 24
        ket_qua.append(f"{DIA_CHI[chi_gio]} ({start}-{end}h)")
    return ", ".join(ket_qua)

def check_han_xau(day_am, month_am, chi_ngay):
    han = []
    if day_am in [3, 7, 13, 18, 22, 27]: han.append("Tam Nương")
    if day_am in [5, 14, 23]: han.append("Nguyệt Kỵ")
    if SAT_CHU.get(month_am) == chi_ngay: han.append("Sát Chủ")
    return han

def check_xung_tuoi(nam_sinh, chi_ngay_idx):
    if not nam_sinh: return None
    chi_tuoi = (nam_sinh - 4) % 12
    if LUC_XUNG.get(chi_tuoi) == chi_ngay_idx:
        return f"Tuổi {DIA_CHI[chi_tuoi]} xung khắc ngày {DIA_CHI[chi_ngay_idx]}"
    return None

# --- HÀM TÍNH SAO CHIẾU MỆNH (MỚI) ---
def tinh_sao_chieu_menh(nam_sinh, gioi_tinh_nam=True):
    """Tính sao chiếu mệnh theo năm sinh và giới tính"""
    if not nam_sinh: return None
    current_year = datetime.now().year
    tuoi_am = current_year - nam_sinh + 1
    
    # Tính số dư khi chia cho 9
    rem = tuoi_am % 9
    
    # Index 0 cho Nam, 1 cho Nữ
    idx = 0 if gioi_tinh_nam else 1
    
    ten_sao = SAO_LOOKUP[rem][idx]
    info_sao = SAO_PROPERTIES[ten_sao]
    
    return {
        "ten": ten_sao,
        "tuoi_am": tuoi_am,
        "info": info_sao
    }

# --- MAIN LOGIC FUNCTION ---
def phan_tich_ngay(date_obj, nam_sinh_user=None):
    lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
    can_ngay, chi_ngay = tinh_can_chi_ngay_julian(date_obj.day, date_obj.month, date_obj.year)
    
    can_nam = (lunar.year + 6) % 10; chi_nam = (lunar.year + 8) % 12
    can_thang = ((can_nam * 2 + 1) % 10 + lunar.month - 1) % 10; chi_thang = (2 + lunar.month - 1) % 12

    is_hoang_dao = check_ngay_hoang_dao(lunar.month, chi_ngay)
    han_xau = check_han_xau(lunar.day, lunar.month, chi_ngay)
    xung_tuoi = check_xung_tuoi(nam_sinh_user, chi_ngay) if nam_sinh_user else None
    tiet_khi, _ = get_tiet_khi(date_obj)
    info_truc = DATA_TRUC[(chi_ngay - (lunar.month + 1) + 12) % 12]
    
    return {
        "duong_lich": date_obj.strftime("%d/%m/%Y"),
        "am_lich_str": f"{lunar.day:02d}/{lunar.month:02d}",
        "am_lich_full": f"{lunar.day:02d}/{lunar.month:02d}/{lunar.year}",
        "can_chi_ngay": get_can_chi(can_ngay, chi_ngay),
        "can_chi_thang": get_can_chi(can_thang, chi_thang),
        "can_chi_nam": get_can_chi(can_nam, chi_nam),
        "tiet_khi": tiet_khi,
        "is_hoang_dao": is_hoang_dao,
        "gio_tot": lay_gio_hoang_dao(chi_ngay),
        "truc_ten": info_truc['ten'],
        "viec_tot": info_truc['tot'],
        "viec_xau": info_truc['xau'],
        "han_xau_list": han_xau,
        "xung_tuoi": xung_tuoi
    }

def doi_ngay_duong_sang_am(d, m, y):
    try:
        lunar = LunarDate.fromSolarDate(y, m, d)
        return {"string": f"{lunar.day:02d}/{lunar.month:02d}/{lunar.year}" + (" (Nhuận)" if lunar.isLeapMonth else "")}
    except: return None

def doi_ngay_am_sang_duong(d, m, y, leap=False):
    try:
        solar = LunarDate(y, m, d, leap).toSolarDate()
        return {"day": solar.day, "month": solar.month, "year": solar.year, "string": f"{solar.day:02d}/{solar.month:02d}/{solar.year}"}
    except: return None
