import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from logic import phan_tich_ngay, doi_ngay_duong_sang_am, doi_ngay_am_sang_duong, tinh_sao_chieu_menh

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Lịch Vạn Niên - LeNamVN", page_icon="☯️", layout="wide")

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    /* 1. Đẩy nội dung sát lên trên cùng */
    .main .block-container {
        padding-top: 0rem; 
        padding-bottom: 1rem;
    }

    /* 2. BANNER HEADER TINH GỌN */
    .banner-header {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        color: #1a4a5a;
        padding: 10px 20px; 
        display: flex;
        align-items: baseline; 
        justify-content: flex-start;
        gap: 20px;
        border-bottom: 2px solid #4CB8C4;
        margin-bottom: 15px;
        border-radius: 0 0 10px 10px;
    }
    
    .banner-header h1 {
        margin: 0; 
        font-size: 2rem; 
        font-weight: 700; 
        color: #134E5E; 
        font-family: 'Times New Roman', serif;
        line-height: 1.2;
    }
    
    .banner-header p {
        margin: 0; 
        font-size: 1rem; 
        color: #666;
        font-weight: 400;
        font-style: italic;
        line-height: 1.2;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; margin-top: 5px;}
    .stTabs [data-baseweb="tab"] { height: 40px; padding-top: 8px; padding-bottom: 8px; background-color: #f8f9fa; border-radius: 5px; color: #555; font-size: 0.9rem;}
    .stTabs [aria-selected="true"] { background-color: #17a2b8; color: white; }
    
    /* 3. BOX NGÀY CHÍNH - COMPACT VERSION */
    .box-ngay { 
        padding: 15px 20px; 
        border-radius: 10px; 
        color: white; 
        box-shadow: 0 3px 10px rgba(0,0,0,0.1); 
        margin-bottom: 15px;
    }
    
    .box-flex {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }
    
    .box-left {
        flex: 0 0 35%; 
        text-align: center;
        border-right: 1px solid rgba(255,255,255,0.3);
        padding-right: 15px;
    }
    
    .box-right {
        flex: 1; 
        text-align: left;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .bg-hoang-dao { background: linear-gradient(to right, #4CB8C4, #3CD3AD); }
    .bg-hac-dao { background: linear-gradient(to right, #606c88, #3f4c6b); }
    
    .gio-tot-row { 
        margin-top: 10px; 
        font-size: 0.9rem; 
        background-color: rgba(255,255,255,0.2); 
        padding: 8px 12px; 
        border-radius: 6px; 
        color: #fff; 
        text-align: left;
        display: flex;
        gap: 10px;
    }

    .bad-box { background-color: #f8d7da; color: #721c24; padding: 8px; border-radius: 5px; border: 1px solid #f5c6cb; margin-bottom: 8px; font-size: 0.9rem;}
    .personal-box { background-color: #d1e7dd; color: #0f5132; padding: 8px; border-radius: 5px; border-left: 4px solid #0f5132; margin-bottom: 8px; font-size: 0.9rem;}
    
    .sao-box-tot { border-left: 4px solid #28a745; padding: 8px; background: #e6ffed; margin-top: 8px; border-radius: 4px; font-size: 0.9rem;}
    .sao-box-xau { border-left: 4px solid #dc3545; padding: 8px; background: #ffe6e6; margin-top: 8px; border-radius: 4px; font-size: 0.9rem;}
    .sao-box-trung { border-left: 4px solid #ffc107; padding: 8px; background: #fffbe6; margin-top: 8px; border-radius: 4px; font-size: 0.9rem;}

    button[title="View fullscreen"]{visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- HÀM HIỂN THỊ BOX NGÀY (QUAN TRỌNG: KHÔNG ĐƯỢC THỤT DÒNG HTML) ---
def render_day_box(data):
    bg_class = "bg-hoang-dao" if data['is_hoang_dao'] else "bg-hac-dao"
    icon_ngay = "★ HOÀNG ĐẠO" if data['is_hoang_dao'] else "● HẮC ĐẠO"
    
    # HTML phải viết sát lề trái để tránh lỗi hiển thị code
    html_content = f"""
<div class="box-ngay {bg_class}">
<div class="box-flex">
<div class="box-left">
<div style="font-size: 0.85rem; text-transform: uppercase; opacity: 0.9;">Dương Lịch</div>
<div style="font-size: 3.5rem; font-weight: 700; line-height: 1;">{data['duong_lich'].split('/')[0]}</div>
<div style="font-size: 1.2rem; font-weight: 500;">Tháng {data['duong_lich'].split('/')[1]}/{data['duong_lich'].split('/')[2]}</div>
</div>
<div class="box-right">
<div style="font-size: 1.8rem; font-weight: 600;">
<span style="font-size: 0.9rem; font-weight: 400; opacity: 0.9; vertical-align: middle;">Âm Lịch: </span>
{data['am_lich_str']}
</div>
<div style="font-size: 1.1rem; margin-top: 5px;">
<b>{data['can_chi_ngay']}</b> | Tháng {data['can_chi_thang']} | Năm {data['can_chi_nam']}
</div>
<div style="margin-top: 5px; font-weight: bold; color: #fff6cd; font-size: 0.9rem;">{icon_ngay}</div>
</div>
</div>
<div class="gio-tot-row">
<div style="font-weight: bold; white-space: nowrap;">⏰ Giờ Tốt:</div>
<div style="font-style: italic; white-space: normal;">{data['gio_tot']}</div>
</div>
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)

# --- HEADER BANNER ---
st.markdown("""
<div class="banner-header">
    <h1>Lịch Vạn Niên</h1>
    <p>| &nbsp; Xem Ngày & Phong Thủy</p>
</div>
""", unsafe_allow_html=True)


# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Thông tin Gia chủ")
    user_year = st.number_input("Năm sinh (Dương lịch):", min_value=1920, max_value=2030, value=1990, format="%d")
    gioi_tinh = st.radio("Giới tính:", ["Nam", "Nữ"], horizontal=True)
    
    can = (user_year + 6) % 10; chi = (user_year + 8) % 12
    ten_tuoi = f"{['Giáp','Ất','Bính','Đinh','Mậu','Kỷ','Canh','Tân','Nhâm','Quý'][can]} {['Tý','Sửu','Dần','Mão','Thìn','Tỵ','Ngọ','Mùi','Thân','Dậu','Tuất','Hợi'][chi]}"
    st.success(f"Tuổi: **{ten_tuoi}**")

    st.subheader("⭐ Sao chiếu mệnh")
    is_nam = gioi_tinh == "Nam"
    sao_info = tinh_sao_chieu_menh(user_year, is_nam)
    
    if sao_info:
        loai_sao = sao_info['info']['loai']
        css_sao = "sao-box-tot" if loai_sao == 1 else ("sao-box-xau" if loai_sao == -1 else "sao-box-trung")
        icon_sao = "🟢" if loai_sao == 1 else ("🔴" if loai_sao == -1 else "🟡")
        
        st.markdown(f"""
        <div class="{css_sao}">
            <strong>{icon_sao} {sao_info['ten']}</strong> (Tuổi âm: {sao_info['tuoi_am']})<br>
            <small>{sao_info['info']['desc']}</small>
        </div>
        """, unsafe_allow_html=True)

    st.caption("© LeNamVN Calendar")


# TABS
tab1, tab2 = st.tabs(["XEM LỊCH CHI TIẾT", "ĐỔI NGÀY ÂM DƯƠNG"])

# ================= TAB 1 =================
with tab1:
    c1, c2 = st.columns([1, 3])
    with c1:
        selected_date = st.date_input("Chọn ngày:", datetime.now(), format="DD/MM/YYYY")
    
    current_date = datetime.combine(selected_date, datetime.min.time())
    data = phan_tich_ngay(current_date, user_year)

    render_day_box(data)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🔍 Phân Tích")
        st.markdown(f"**🌍 Tiết khí:** {data['tiet_khi']}")
        st.markdown(f"**⚖️ Trực {data['truc_ten']}:** {data['viec_tot']}")
        st.write("---")

        if data['han_xau_list']:
            for han in data['han_xau_list']:
                st.markdown(f'<div class="bad-box">⚠️ <b>Phạm:</b> {han}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="personal-box">✅ Ngày lành, không phạm đại hạn.</div>', unsafe_allow_html=True)
            
        if data['xung_tuoi']:
            st.markdown(f'<div class="bad-box">⛔ <b>Xung tuổi {ten_tuoi}:</b> {data["xung_tuoi"]}</div>', unsafe_allow_html=True)
        else:
             st.markdown(f'<div class="personal-box">👍 <b>Hợp tuổi:</b> Ngày này tốt/bình hòa với tuổi {ten_tuoi}.</div>', unsafe_allow_html=True)

    with col_right:
        st.subheader("📜 Việc Nên & Kỵ")
        with st.container(border=True):
            st.info(f"**NÊN LÀM:** {data['viec_tot']}")
            st.warning(f"**KIÊNG KỴ:** {data['viec_xau']}")

    st.write("")
    with st.expander("📅 Danh sách ngày Tốt sắp tới (30 ngày)", expanded=False):
        list_days = []
        temp_date = current_date
        for i in range(1, 31):
            temp_date += timedelta(days=1)
            info = phan_tich_ngay(temp_date, user_year)
            if info['is_hoang_dao']:
                status = "⛔ Xung" if info['xung_tuoi'] else "✅ Tốt"
                list_days.append({
                    "Dương lịch": info['duong_lich'],
                    "Âm lịch": info['am_lich_str'],
                    "Can Chi": info['can_chi_ngay'],
                    "Tuổi": status,
                    "Giờ Tốt": info['gio_tot'].split(',')[0] + "..."
                })
        st.dataframe(pd.DataFrame(list_days), use_container_width=True)

# ================= TAB 2 =================
with tab2:
    st.header("🔄 Chuyển đổi Âm - Dương")
    st.caption("Nhập ngày để chuyển đổi và xem chi tiết tốt xấu.")
    
    type_convert = st.radio("", ["Dương sang Âm", "Âm sang Dương"], horizontal=True)
    result_date_obj = None 
    
    st.divider()
    
    if type_convert == "Dương sang Âm":
        d_in = st.date_input("Ngày Dương:", datetime.now(), format="DD/MM/YYYY", key="d2a")
        if st.button("Chuyển đổi", type="primary"):
            result_date_obj = datetime.combine(d_in, datetime.min.time())
            
    else:
        c1, c2, c3, c4 = st.columns([1, 1, 1.5, 1])
        d_am = c1.number_input("Ngày", 1, 30, 1)
        m_am = c2.number_input("Tháng", 1, 12, 1)
        y_am = c3.number_input("Năm", 1900, 2100, datetime.now().year)
        nhuan = c4.checkbox("Nhuận")
        
        if st.button("Chuyển đổi", type="primary"):
            res = doi_ngay_am_sang_duong(d_am, m_am, y_am, nhuan)
            if res: result_date_obj = datetime(res['year'], res['month'], res['day'])
            else: st.error("Ngày Âm lịch không hợp lệ!")

    if result_date_obj:
        st.success("✅ Kết quả chuyển đổi:")
        data_cv = phan_tich_ngay(result_date_obj, user_year)
        render_day_box(data_cv)
        st.info(f"**Nên làm:** {data_cv['viec_tot']}")
