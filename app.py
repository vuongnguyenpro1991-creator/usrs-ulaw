import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import itertools

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="ULAW Smart Reference System", layout="wide", initial_sidebar_state="expanded")

if 'ai_data' not in st.session_state:
    st.session_state.ai_data = {
        "chuyen_nganh": ["Đang chờ AI phân tích..."],
        "tu_khoa_vn": ["Đang chờ AI phân tích..."],
        "tu_khoa_en": ["Đang chờ AI phân tích..."],
        "tu_khoa_dac_thu": ["Đang chờ AI phân tích..."],
        "co_yeu_to_nuoc_ngoai": False
    }

if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

# Khởi tạo trạng thái ngôn ngữ tra cứu mặc định
if 'applied_search_mode' not in st.session_state:
    st.session_state.applied_search_mode = "Tiếng Việt & Tiếng Anh (Quốc tế)"

# Khởi tạo bộ nhớ tạm để tự động xóa trắng ô nhập liệu sau khi Enter
if 'input_vn_widget' not in st.session_state: st.session_state.input_vn_widget = ""
if 'input_en_widget' not in st.session_state: st.session_state.input_en_widget = ""

# Hàm xử lý khi ấn Enter ở ô Tiếng Việt
def on_add_vn():
    val = st.session_state.input_vn_widget
    if val:
        new_kws = [k.strip() for k in val.split(',') if k.strip()]
        if st.session_state.ai_data["tu_khoa_vn"] == ["Đang chờ AI phân tích..."]: st.session_state.ai_data["tu_khoa_vn"] = []
        for kw in new_kws:
            if kw not in st.session_state.ai_data["tu_khoa_vn"]: st.session_state.ai_data["tu_khoa_vn"].append(kw)
        st.session_state.input_vn_widget = ""

# Hàm xử lý khi ấn Enter ở ô Tiếng Anh
def on_add_en():
    val = st.session_state.input_en_widget
    if val:
        new_kws = [k.strip() for k in val.split(',') if k.strip()]
        if st.session_state.ai_data["tu_khoa_en"] == ["Đang chờ AI phân tích..."]: st.session_state.ai_data["tu_khoa_en"] = []
        for kw in new_kws:
            if kw not in st.session_state.ai_data["tu_khoa_en"]: st.session_state.ai_data["tu_khoa_en"].append(kw)
        st.session_state.input_en_widget = ""

def call_gemini(topic, mode):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3.5-flash') 
        
        # ĐIỀU HƯỚNG AI DỰA TRÊN TÙY CHỌN NGÔN NGỮ CỦA NGƯỜI DÙNG
        mode_instruction = ""
        if mode == "Chỉ Tiếng Việt":
            mode_instruction = """
5. PHẠM VI NGÔN NGỮ: Người dùng CHỈ yêu cầu tra cứu bằng Tiếng Việt.
- "tu_khoa_en" BẮT BUỘC là mảng rỗng [].
- "tu_khoa_dac_thu" BẮT BUỘC là mảng rỗng [].
- "co_yeu_to_nuoc_ngoai" BẮT BUỘC là false.
"""
        else:
            mode_instruction = """
5. PHẠM VI NGÔN NGỮ: Dịch các từ khóa cốt lõi sang Tiếng Anh để đưa vào "tu_khoa_en". Nếu có yếu tố đặc thù quốc tế, hãy cập nhật "tu_khoa_dac_thu".
"""

        prompt = f"""Bạn là một Chuyên gia Thư viện học tại Đại học Luật TP.HCM. 
Nhiệm vụ: Phân tích đề tài sau để tạo bộ từ khóa tra cứu: "{topic}".
KỶ LUẬT NGHIỆP VỤ:
1. Từ khóa ĐẦU TIÊN phải là TỪ KHÓA CHÍNH mang tính cốt lõi của đề tài (VD: "giao dịch bảo đảm", "thanh toán điện tử").
2. TUYỆT ĐỐI KHÔNG LIỆT KÊ TỪ ĐỒNG NGHĨA. 
3. Các từ khóa tiếp theo PHẢI LÀ TỪ KHÓA PHỤ, chỉ các khía cạnh/đối tượng để làm sáng tỏ.
4. CẤM tạo ra các từ khóa quá dài ghép nhiều vế.{mode_instruction}
Trả về ĐÚNG JSON: {{"chuyen_nganh": ["..."], "tu_khoa_vn": ["..."], "tu_khoa_en": ["..."], "tu_khoa_dac_thu": ["..."], "co_yeu_to_nuoc_ngoai": true/false}} không giải thích."""
        
        response = model.generate_content(prompt)
        text_result = response.text.replace("`" + "`" + "`" + "json", "").replace("`" + "`" + "`", "").strip()
        st.session_state.ai_data = json.loads(text_result)
        return True
    except Exception as e:
        st.error(f"Lỗi hệ thống AI: {e}")
        return False

# 2. TÙY CHỈNH CSS CHUYÊN SÂU
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stApp {background-color: #f4f6f9;}
    header {visibility: hidden;}
    
    [data-testid="stSidebar"] {background-color: #2b3b7c; color: white;}
    [data-testid="stSidebar"] * {color: white !important;}
    
    .hero-banner {
        background-image: linear-gradient(rgba(26, 35, 126, 0.85), rgba(26, 35, 126, 0.85)), url('https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=2000&auto=format&fit=crop');
        background-size: cover; background-position: center;
        padding: 40px 30px; border-radius: 10px; margin-top: -50px; margin-bottom: 20px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .hero-title-small {color: #90caf9; font-weight: 700; font-size: 16px; letter-spacing: 1.5px; text-transform: uppercase;}
    .hero-title-large {color: #ffffff; font-weight: 800; font-size: 36px; margin: 15px 0; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);}
    .hero-subtitle {color: #e3f2fd; font-size: 16px; max-width: 800px; margin: 0 auto;}
    
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, .stNumberInput input {
        background-color: #ebf0f8 !important;
        border: 1px solid #b0bec5 !important;
    }
    
    .card-header {
        font-weight: 700; color: #1a237e; font-size: 16px; margin-bottom: 20px; 
        display: flex; align-items: center;
        background-color: #e8eaf6; padding: 12px 15px; border-radius: 6px;
        border-left: 5px solid #2962ff;
    }

    textarea {
        background-color: #0f172a !important; 
        color: #bae6fd !important; 
        font-family: 'Courier New', Courier, monospace !important; 
        font-size: 13.5px !important; 
        border-left: 4px solid #38bdf8 !important;
        line-height: 1.5 !important;
    }

    .query-preview-box {
        background-color: #0f172a; color: #bae6fd; padding: 12px; 
        border-radius: 6px; font-family: 'Courier New', Courier, monospace; 
        font-size: 13px; margin-top: -10px; margin-bottom: 15px;
        border-left: 4px solid #38bdf8; overflow-x: auto; line-height: 1.5;
    }
    .query-label {
        font-size: 12.5px; font-weight: 700; color: #fcd34d; 
        margin-top: 6px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; display: block;
    }

    .step-container {display: flex; justify-content: space-between; background: white; padding: 15px 30px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #e0e0e0;}
    .step-item {display: flex; align-items: center; font-weight: 600; color: #5f6368; font-size: 14px;}
    .step-circle {background-color: #e8eaf6; color: #3f51b5; width: 30px; height: 30px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;}
    .step-active .step-circle {background-color: #3f51b5; color: white;}
    .step-active {color: #3f51b5;}
    
    .btn-blue button {background-color: #2962ff !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; border: none; padding: 10px !important;}
    .btn-green button {background-color: #00897b !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; border: none; padding: 10px !important;}
    .btn-orange button {background-color: #f57c00 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; border: none; padding: 10px !important;}
    .btn-outline button {background-color: white !important; color: #3f51b5 !important; border: 1.5px solid #3f51b5 !important; width: 100%; border-radius: 8px !important; font-weight: 600 !important;}
    
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.03);}
    .scrollable-source {max-height: 380px; overflow-y: auto; padding-right: 10px;}
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    col_logo1, col_logo2, col_logo3 = st.columns([1,3,1])
    with col_logo2:
        try: st.image("logo_ulaw.png", use_column_width=True)
        except Exception: pass
            
    st.markdown("<h3 style='text-align: center;'>THƯ VIỆN ULAW</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🏠 Trang chủ")
    st.markdown("📝 Tạo yêu cầu tra cứu")
    st.markdown("⏱️ Lịch sử yêu cầu")
    st.markdown("📁 Kho báo cáo")
    st.markdown("---")
    st.markdown("📞 (028) 3940 0989")

# HERO BANNER
st.markdown("""
<div class="hero-banner">
    <div class="hero-title-small">ULAW SMART REFERENCE SYSTEM</div>
    <div class="hero-title-large">TRA CỨU THÔNG TIN THEO YÊU CẦU</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="step-container">
    <div class="step-item step-active"><div class="step-circle">1</div> Khởi tạo yêu cầu</div>
    <div class="step-item step-active"><div class="step-circle">2</div> AI đề xuất từ khóa</div>
    <div class="step-item step-active"><div class="step-circle">3</div> Chọn nguồn tra cứu</div>
    <div class="step-item step-active"><div class="step-circle" style="background-color:#f57c00;color:white;">4</div> Kiểm duyệt & xuất báo cáo</div>
</div>
""", unsafe_allow_html=True)

# 4. BỐ CỤC 4 CỘT
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📋 1. KHỞI TẠO YÊU CẦU</div>", unsafe_allow_html=True)
        topic = st.text_input("Tên đề tài nghiên cứu *", placeholder="Nhập tên đề tài...")
        author = st.text_input("Tên người/nhóm yêu cầu *", placeholder="Nhập tên người yêu cầu...")
        
        st.caption("Khoảng thời gian xuất bản")
        c1, c2 = st.columns(2)
        with c1: year_start = st.number_input("Từ", value=2020, step=1, label_visibility="collapsed")
        with c2: year_end = st.number_input("Đến", value=2026, step=1, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # TÙY CHỌN NGÔN NGỮ TRA CỨU
        search_mode = st.radio("🌐 Phạm vi ngôn ngữ tra cứu:", ["Chỉ Tiếng Việt", "Tiếng Việt & Tiếng Anh (Quốc tế)"], horizontal=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
        if st.button("🚀 Phân tích bằng AI", use_container_width=True):
            if topic.strip() == "": st.error("Vui lòng nhập Tên đề tài!")
            else:
                st.session_state.search_clicked = False 
                st.session_state.applied_search_mode = search_mode # Ghi nhớ tùy chọn
                with st.spinner("🤖 AI đang phân tích dữ liệu..."):
                    if call_gemini(topic, search_mode): st.success("✅ Phân tích thành công!")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 2: KHỐI TỪ KHÓA (ẨN/HIỆN THÔNG MINH) ====================
with col2:
    with st.container(border=True):
        st.markdown("<div class='card-header'>💡 2. AI ĐỀ XUẤT TỪ KHÓA</div>", unsafe_allow_html=True)
        ai = st.session_state.ai_data
        st.multiselect("Chuyên ngành luật", ai.get("chuyen_nganh", []), default=ai.get("chuyen_nganh", []))
        
        # --- KHỐI TIẾNG VIỆT (Luôn hiển thị) ---
        sel_vn = st.multiselect("Từ khóa tiếng Việt", ai.get("tu_khoa_vn", []), default=ai.get("tu_khoa_vn", []))
        st.text_input("➕ Thêm từ khác, sau đó nhấn Enter để thêm từ:", key="input_vn_widget", on_change=on_add_vn, placeholder="VD: giao dịch bảo đảm...")

        if sel_vn and sel_vn[0] != "Đang chờ AI phân tích...":
            vn_text = "🔸 TÌM ĐƠN LẺ:\n"
            for kw in sel_vn: vn_text += f'"{kw}"\n'
            
            if len(sel_vn) > 1:
                vn_text += "\n🔸 TÌM KẾT HỢP (Từ khóa chính + Từ khóa phụ):\n"
                core_kw = sel_vn[0]
                for sec_kw in sel_vn[1:]: vn_text += f'"{core_kw}" AND "{sec_kw}"\n'
                    
            st.caption("✍️ Tùy chỉnh chuỗi lệnh tra cứu (có thể gõ thêm/xóa bớt):")
            st.text_area("Lệnh TV", value=vn_text.strip(), height=160, key="ta_vn", label_visibility="collapsed")
        
        # --- KHỐI TIẾNG ANH & QUỐC TẾ (Chỉ hiển thị khi người dùng chọn) ---
        if st.session_state.applied_search_mode == "Tiếng Việt & Tiếng Anh (Quốc tế)":
            st.markdown("<hr style='margin:15px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
            
            sel_en = st.multiselect("Từ khóa tiếng Anh", ai.get("tu_khoa_en", []), default=ai.get("tu_khoa_en", []))
            st.text_input("➕ Thêm từ khác, sau đó nhấn Enter để thêm từ (Tiếng Anh):", key="input_en_widget", on_change=on_add_en, placeholder="VD: secured transaction...")

            if sel_en and sel_en[0] != "Đang chờ AI phân tích...":
                en_text = "🔸 TÌM ĐƠN LẺ:\n"
                for kw in sel_en: en_text += f'"{kw}"\n'
                
                if len(sel_en) > 1:
                    en_text += "\n🔸 TÌM KẾT HỢP (Từ khóa chính + Từ khóa phụ):\n"
                    core_kw_en = sel_en[0]
                    for sec_kw_en in sel_en[1:]: en_text += f'"{core_kw_en}" AND "{sec_kw_en}"\n'
                        
                st.caption("✍️ Tùy chỉnh chuỗi lệnh tra cứu Tiếng Anh:")
                st.text_area("Lệnh EN", value=en_text.strip(), height=160, key="ta_en", label_visibility="collapsed")
            
            # Khối Đặc thù Quốc tế
            sel_dac_thu = []
            if ai.get("co_yeu_to_nuoc_ngoai", False) and ai.get("tu_khoa_dac_thu", []) and ai["tu_khoa_dac_thu"][0] != "Đang chờ AI phân tích...":
                sel_dac_thu = st.multiselect("Từ khóa đặc thù (Quốc tế)", ai.get("tu_khoa_dac_thu", []), default=ai.get("tu_khoa_dac_thu", []))
                if sel_dac_thu:
                    dt_text = "🔸 TÌM ĐƠN LẺ ĐẶC THÙ:\n"
                    for kw in sel_dac_thu: dt_text += f'"{kw}"\n'
                    
                    if sel_vn and sel_vn[0] != "Đang chờ AI phân tích...":
                        dt_text += "\n🔸 ĐỐI CHIẾU BỐI CẢNH QUỐC TẾ:\n"
                        dt_text += f'"{sel_vn[0]}" AND "{sel_dac_thu[0]}"'
                        
                    st.caption("✍️ Tùy chỉnh chuỗi lệnh tra cứu đặc thù:")
                    st.text_area("Lệnh Đặc thù", value=dt_text.strip(), height=130, key="ta_dt", label_visibility="collapsed")

        # Nút Khôi phục / Xác nhận
        st.markdown("<br>", unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            st.markdown("<div class='btn-outline'>", unsafe_allow_html=True)
            if st.button("🔄 Khôi phục", use_container_width=True):
                st.session_state.ai_data = {"chuyen_nganh": ["Đang chờ AI phân tích..."], "tu_khoa_vn": ["Đang chờ AI phân tích..."], "tu_khoa_en": ["Đang chờ AI phân tích..."], "tu_khoa_dac_thu": ["Đang chờ AI phân tích..."], "co_yeu_to_nuoc_ngoai": False}
                st.session_state.search_clicked = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with cb2:
            st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
            st.button("✓ Xác nhận", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 3 & CỘT 4 ====================
with col3:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📚 3. CHỌN NGUỒN TRA CỨU</div>", unsafe_allow_html=True)
        st.markdown("<div class='scrollable-source'>", unsafe_allow_html=True)
        
        st.caption("Nội bộ & Thư viện Quốc gia")
        src_ulaw = st.checkbox("Thư viện Trường ĐH Luật TP.HCM", value=True)
        src_nat = st.checkbox("Thư viện Quốc gia Việt Nam", value=True)
        src_khth = st.checkbox("Thư viện Khoa học Tổng hợp TP.HCM", value=True)
        st.caption("Trường Đại học liên kết")
        src_uel = st.checkbox("Đại học Kinh tế - Luật (UEL)", value=True)
        src_lhn = st.checkbox("Đại học Luật Hà Nội", value=True)
        src_qghn = st.checkbox("Đại học Quốc gia Hà Nội", value=True)
        src_lhue = st.checkbox("Đại học Luật – Đại học Huế", value=True)
        st.caption("Quốc tế")
        src_hein = st.checkbox("HeinOnline", value=True)
        src_west = st.checkbox("Westlaw", value=True)
        st.caption("Pháp quy & Mở rộng")
        src_lvn = st.checkbox("Luật Việt Nam", value=True)
        src_tvpl = st.checkbox("Thư Viện Pháp Luật", value=True)
        
        st.markdown("</div><br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-green'>", unsafe_allow_html=True)
        if st.button("🔍 Bắt đầu Tra cứu", use_container_width=True):
            st.session_state.search_clicked = True
        st.markdown("</div>", unsafe_allow_html=True)

with col4:
    with st.container(border=True):
        st.markdown("<div class='card-header'>🏠 4. XUẤT BÁO CÁO</div>", unsafe_allow_html=True)
        
        if not st.session_state.search_clicked:
            st.markdown("<small style='color:#5f6368;'>Tiến trình tra cứu: <b>0%</b></small>", unsafe_allow_html=True)
            st.progress(0)
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.markdown("<b>Kết quả tìm thấy: 0 tài liệu</b>", unsafe_allow_html=True)
            st.info("Bấm 'Bắt đầu Tra cứu' ở Cột 3 để hệ thống tự động cào dữ liệu.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            sources_to_scan = ["Thư viện ULAW", "Thư viện Quốc gia", "ĐH Luật Hà Nội", "HeinOnline", "Thư Viện Pháp Luật"]
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
                current_src = sources_to_scan[percent_complete // 20 % len(sources_to_scan)]
                status_text.markdown(f"<small style='color:#5f6368;'>Đang truy vấn: {current_src}... ({percent_complete+1}%)</small>", unsafe_allow_html=True)
            
            status_text.markdown("<small style='color:green;'><b>✓ Đã hoàn thành quét dữ liệu chéo nguồn!</b></small>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.markdown("<b>Kết quả tìm thấy: 4 tài liệu tương thích</b>", unsafe_allow_html=True)
            
            data_sample = {
                "Tiêu đề tài liệu": [
                    "Pháp luật về giải quyết tranh chấp tại Việt Nam", 
                    "Thực tiễn giải quyết quyền sử dụng đất tại Tòa án", 
                    "Disputes and Resolution Mechanisms: A Comparative Study", 
                    "Bình luận án về tranh chấp hợp đồng"
                ],
                "Năm": [2023, 2024, 2022, 2025]
            }
            df_result = pd.DataFrame(data_sample)
            st.dataframe(df_result, hide_index=True, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='btn-orange'>", unsafe_allow_html=True)
            if st.button("📥 Xuất báo cáo DOCX chuẩn ULAW", use_container_width=True):
                st.snow()
                st.success("🎉 Đã xuất file báo cáo thành công!")
            st.markdown("</div>", unsafe_allow_html=True)
