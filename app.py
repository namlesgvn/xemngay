import streamlit as st
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from datetime import datetime, timedelta
from pytz import timezone
from lunardate import LunarDate
import os

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lịch Vạn Niên & Thiên Văn", page_icon="🌌", layout="wide")

# --- DỮ LIỆU CỐ ĐỊNH ---
DS_TIET_KHI = [
    "Xuân phân", "Thanh minh", "Cốc vũ", "Lập hạ", "Tiểu mãn", "Mang chủng",
    "Hạ chí", "Tiểu thử", "Đại thử", "Lập thu", "Xử thử", "Bạch lộ",
    "Thu phân", "Hàn lộ", "Sương giáng", "Lập đông", "Tiểu tuyết", "Đại tuyết",
    "Đông chí", "Tiểu hàn", "Đại hàn", "Lập xuân", "Vũ thủy", "Kinh trập"
]

THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

DATA_GIO_HOANG_DAO = {
    0: [0, 1, 3, 5, 7, 9], 1: [2, 4, 5, 7, 9, 10], 2: [0, 1, 4, 7, 9, 10],
    3: [0, 2, 4, 6, 8, 10], 4: [2, 4, 5, 7, 9, 10], 5: [1, 4, 6, 8, 10, 0],
    6: [0, 1, 3, 5, 7, 9], 7: [2, 4, 5, 7, 9, 10], 8: [0, 1, 4, 7, 9, 10],
    9: [0, 2, 4, 6, 8, 10], 10: [2, 4, 5, 7, 9, 10], 11: [1, 4, 6, 8, 10, 0]
}

DATA_TRUC = [
    {"ten": "Kiến", "tot": "Xuất hành, giá thú, mưu sự", "xau": "Động thổ, đào ao"},
    {"ten": "Trừ",  "tot": "Cúng tế, giải oan, chữa bệnh", "xau": "Cưới hỏi, đi xa"},
    {"ten": "Mãn",  "tot": "Cúng tế, cầu tài, khai trương", "xau": "Kiện tụng, nhậm chức"},
    {"ten": "Bình", "tot": "Sửa nhà, nhập trạch, cưới hỏi", "xau": "Đào mương, thưa kiện"},
    {"ten": "Định", "tot": "Nhập học, mua bán, động thổ", "xau": "Tố tụng, xuất quân"},
    {"ten": "Chấp", "tot": "Lập khế ước, sửa nhà, trồng trọt", "xau": "Xuất vốn, chuyển nhà"},
    {"ten": "Phá",  "tot": "Phá dỡ nhà cũ, chữa bệnh", "xau": "Cưới hỏi, khai trương"},
    {"ten": "Nguy", "tot": "Cúng tế, san đường", "xau": "Đi thuyền, leo núi, cưới hỏi"},
    {"ten": "Thành", "tot": "Khai trương, nhập học, giá thú", "xau": "Kiện tụng, tranh chấp"},
    {"ten": "Thu",  "tot": "Thu nợ, mua súc vật, cấy gặt", "xau": "Mai táng, xuất vốn"},
    {"ten": "Khai", "tot": "Cưới hỏi, khai trương, động thổ", "xau": "Chôn cất, tranh chấp"},
    {"ten": "Bế",   "tot": "Đắp đập, xây tường, an táng", "xau": "Đi xa, chữa mắt, cưới hỏi"}
]

# --- CÁC HÀM TÍNH TOÁN (GIỮ NGUYÊN LOGIC CỦA BẠN) ---

# Dùng cache để không phải load lại file 16MB mỗi lần bấm nút
@st.cache_resource
def load_skyfield_data():
    if not os.path.exists('de421.bsp'):
        load('de421.bsp')
    ts = load.timescale()
    eph = load('de421.bsp')
    return ts, eph

def lay_tiet_khi_chinh_xac(date_obj, ts, eph):
    if date_obj.tzinfo is None:
        tz = timezone('Asia/Ho_Chi_Minh')
        date_obj = tz.localize(date_obj)
    t = ts.from_datetime(date_obj)
    earth, sun = eph['earth'], eph['sun']
    astrometric = earth.at(t).observe(sun).apparent()
    _, lon, _ = astrometric.frame_latlon(ecliptic_frame)
    degrees = lon.degrees
    index = int(degrees // 15)
    return DS_TIET_KHI[index], degrees

def lay_ten_can_chi(can, chi):
    return f"{THIEN_CAN[can]} {DIA_CHI[chi]}"

def tinh_can_chi_ngay_julian(d, m, y):
    a = (14 - m) // 12
    y_j = y + 4800 - a
    m_j = m + 12 * a - 3
    jdn = d + (153 * m_j + 2) // 5 + 365 * y_j + y_j // 4 - y_j // 100 + y_j // 400 - 32045
    return (jdn + 9) % 10, (jdn + 1) % 12

def check_ngay_hoang_dao(thang_am, chi_ngay_idx):
    khoi_thanh_long = ((thang_am - 1) % 6) * 2
    offset = (chi_ngay_idx - khoi_thanh_long + 12) % 12
    return offset in [0, 1, 4, 5, 7, 10]

def lay_danh_sach_gio_hoang_dao(chi_ngay_idx, can_ngay_idx):
    ds_indices = DATA_GIO_HOANG_DAO.get(chi_ngay_idx, [])
    ket_qua = []
    for chi_gio in ds_indices:
        can_gio = ((can_ngay_idx % 5) * 2 + chi_gio) % 10
        ten_can_chi = lay_ten_can_chi(can_gio, chi_gio)
        start = (chi_gio * 2 - 1) % 24
        end = (chi_gio * 2 + 1) % 24
        ket_qua.append(f"**{ten_can_chi}** ({start}h-{end}h)")
    return ", ".join(ket_qua)

def xac_dinh_truc(thang_am, chi_ngay_idx):
    khoi_kien = (thang_am + 1) % 12 
    truc_idx = (chi_ngay_idx - khoi_kien + 12) % 12
    return DATA_TRUC[truc_idx]

# --- GIAO DIỆN CHÍNH ---

st.title("🔮 Lịch Vạn Niên & Thiên Văn Học")
st.markdown("Chương trình tính toán Tiết khí và Ngày giờ tốt dựa trên **Skyfield (NASA)** và thuật toán lịch pháp cổ truyền.")

# Tải dữ liệu 1 lần duy nhất
ts, eph = load_skyfield_data()


# Tạo 2 tab để chia nội dung cho gọn
tab1, tab2 = st.tabs(["📅 Xem Hôm Nay", "🗓️ Ngày Tới (Ngày Tốt)"])

with tab1:
    st.header("Thông Tin Thời Gian Thực")
    
    tz_vietnam = timezone('Asia/Ho_Chi_Minh') # Khai báo múi giờ Việt Nam
    now = datetime.now(tz_vietnam)           # Lấy thời gian hiện tại CÓ MÚI GIỜ
    
    # 1. Tính Tiết Khí
    ten_tiet_khi, do_hoang_kinh = lay_tiet_khi_chinh_xac(now, ts, eph)
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Thời gian", now.strftime('%H:%M %d/%m/%Y'))
    col_b.metric("Tiết Khí", ten_tiet_khi)
    col_c.metric("Hoàng Kinh Mặt Trời", f"{do_hoang_kinh:.2f}°")
    
    st.divider()
    
    # 2. Tính Âm Lịch & Can Chi
    lunar = LunarDate.fromSolarDate(now.year, now.month, now.day)
    can_nam = (lunar.year + 6) % 10; chi_nam = (lunar.year + 8) % 12
    can_thang = ((can_nam * 2 + 1) % 10 + lunar.month - 1) % 10; chi_thang = (2 + lunar.month - 1) % 12
    can_ngay, chi_ngay = tinh_can_chi_ngay_julian(now.day, now.month, now.year)
    
    st.subheader("🐲 Thông Tin Âm Lịch")
    col_moon1, col_moon2 = st.columns([1, 2])
    
    with col_moon1:
        st.info(f"**Ngày Âm:** {lunar.day}/{lunar.month}/{lunar.year}")
    
    with col_moon2:
        str_ngay = lay_ten_can_chi(can_ngay, chi_ngay)
        str_thang = lay_ten_can_chi(can_thang, chi_thang)
        str_nam = lay_ten_can_chi(can_nam, chi_nam)
        st.success(f"Ngày **{str_ngay}** | Tháng **{str_thang}** | Năm **{str_nam}**")

    # 3. Giờ Hoàng Đạo
    ds_gio_tot = lay_danh_sach_gio_hoang_dao(chi_ngay, can_ngay)
    is_hoang_dao = check_ngay_hoang_dao(lunar.month, chi_ngay)
    
    st.write("### ⭐ Giờ Hoàng Đạo Hôm Nay")
    if is_hoang_dao:
        st.caption("✅ Hôm nay là ngày **Hoàng Đạo** (Tốt)")
    else:
        st.caption("🌑 Hôm nay là ngày **Hắc Đạo** (Xấu)")
        
    st.markdown(f"> {ds_gio_tot}")

with tab2:
    st.header("Dự Báo Các Ngày Tốt Trong 30 Ngày Tới")
    st.markdown("Danh sách các ngày **Hoàng Đạo** và việc nên/kỵ:")
    
    # Chuẩn bị dữ liệu cho bảng
    data_table = []
    
    for i in range(30):
        curr_date = now + timedelta(days=i)
        lunar = LunarDate.fromSolarDate(curr_date.year, curr_date.month, curr_date.day)
        can_ngay, chi_ngay = tinh_can_chi_ngay_julian(curr_date.day, curr_date.month, curr_date.year)

        if check_ngay_hoang_dao(lunar.month, chi_ngay):
            # Thông tin Trực
            info_truc = xac_dinh_truc(lunar.month, chi_ngay)
            ten_can_chi_ngay = lay_ten_can_chi(can_ngay, chi_ngay)
            
            data_table.append({
                "Dương Lịch": curr_date.strftime("%d/%m/%Y"),
                "Âm Lịch": f"{lunar.day}/{lunar.month}",
                "Can Chi": ten_can_chi_ngay,
                "Trực": info_truc['ten'],
                "Việc Nên Làm": info_truc['tot'],
                "Việc Cần Tránh": info_truc['xau']
            })
    
    # Hiển thị bảng dữ liệu
    st.dataframe(data_table, use_container_width=True)
