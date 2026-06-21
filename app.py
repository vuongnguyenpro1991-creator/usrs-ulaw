import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="ULAW Smart Reference System", layout="wide", initial_sidebar_state="expanded")

if 'ai_data' not in st.session_state:
    st.session_state.ai_data = {
        "chuyen_nganh": ["Đang chờ AI phân tích..."],
        "tu_khoa_dinh": "Đang chờ AI phân tích...",
        "tu_khoa_vn": ["Đang chờ AI phân tích..."],
        "tu_khoa_en": ["Đang chờ AI phân tích..."],
        "tu_khoa_dac_thu": ["Đang chờ AI phân tích..."],
        "co_yeu_to_nuoc_ngoai": False
    }

if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

# Khởi tạo state cho ô nhập liệu tự động xóa
if 'input_vn_widget' not in st.session_state: st.session_state.input_vn_widget = ""
if 'input_en_widget' not in st.session_state: st.session_state.input_en_widget = ""

# Hàm xử lý khi ấn Enter ở ô Tiếng Việt (Thêm từ & Tự động dịch sang Tiếng Anh)
def on_add_vn():
    val = st.session_state.input_vn_widget
    if val:
        new_kws = [k.strip() for k in val.split(',') if k.strip()]
        
        # Gọi AI dịch ngầm sang Tiếng Anh
        en_kws = []
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-3.5-flash')
            trans_res = model.generate_content(f"Dịch các cụm từ pháp lý sau sang tiếng Anh, chỉ trả về các cụm từ cách nhau bằng dấu phẩy, không giải thích gì thêm: {val}")
            en_kws = [k.strip() for k in trans_res.text.split(',') if k.strip()]
        except: pass
        
        if st.session_state.ai_data["tu_khoa_vn"] == ["Đang chờ AI phân tích..."]: st.session_state.ai_data["tu_khoa_vn"] = []
        for kw in new_kws:
            if kw not in st.session_state.ai_data["tu_khoa_vn"]: st.session_state.ai_data["tu_khoa_vn"].append(kw)
            
        if en_kws:
            if st.session_state.ai_data["tu_khoa_en"] == ["Đang chờ AI phân tích..."]: st.session_state.ai_data["tu_khoa_en"] = []
            for kw in en_kws:
                if kw not in st.session_state.ai_data["tu_khoa_en"]: st.session_state.ai_data["tu_khoa_en"].append(kw)
                
        # Tự động xóa trắng ô nhập
        st.session_state.input_vn_widget = ""

# Hàm xử lý khi ấn Enter ở ô Tiếng Anh
def on_add_en():
    val = st.session_state.input_en_widget
    if val:
        new_kws = [k.strip() for k in val.split(',') if k.strip()]
        if st.session_state.ai_data["tu_khoa_en"] == ["Đang chờ AI phân tích..."]: st.session_state.ai_data["tu_khoa_en"] = []
        for kw in new_kws:
            if kw not in st.session_state.ai_data["tu_khoa_en"]: st.session_state.ai_data["tu_khoa_en"].append(kw)
        # Tự động xóa trắng ô nhập
        st.session_state.input_en_widget = ""

def call_gemini(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3.5-flash') 
        
        prompt = f"""Bạn là một Chuyên gia Thư viện học và Luật sư tại Đại học Luật TP.HCM. 
Phân tích đề tài: "{topic}".
KỶ LUẬT NGHIỆP VỤ:
1. Xác định đúng 1 "Từ khóa đinh" (Core Keyword) cốt lõi nhất, định danh cho đề tài.
2. Từ khóa phải là CỤM TỪ CÓ NGHĨA PHÁP LÝ. CẤM tách các danh từ chủ thể chung chung (khách hàng, ngân hàng, nhà nước) đứng một mình. Phải ghép thành cụm (VD: quyền lợi khách hàng, hoạt động ngân hàng).
3. Đề tài thuần túy ở Việt Nam thì "co_yeu_to_nuoc_ngoai" BẮT BUỘC là false và "tu_khoa_dac_thu" là [].
Trả về ĐÚNG JSON: {{"chuyen_nganh": ["..."], "tu_khoa_dinh": "...", "tu_khoa_vn": ["..."], "tu_khoa_en": ["..."], "tu_khoa_dac_thu": ["..."], "co_yeu_to_nuoc_ngoai": true/false}} không giải thích thêm."""
        
        response = model.generate_content(prompt)
        text_result = response.text.strip().removeprefix("```json").removesuffix("
```").strip()
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

    /* ĐÃ NÂNG CẤP MÀU SẮC CHO CHỮ TRONG HỘP TRUY VẤN */
    .query-preview-box {
        background-color: #0f172a; color: #bae6fd; padding: 12px; 
        border-radius: 6px; font-family: 'Courier New', Courier, monospace; 
        font-size: 13px; margin-top: -10px; margin-bottom: 15px;
        border-left: 4px solid #38bdf8; overflow-x: auto; line-height: 1.5;
    }
    .query-label {
        font-size: 13px; font-weight: 700; 
        color: #fcd34d; /* MÀU VÀNG SÁNG NỔI BẬT */
        margin-top: 8px; margin-bottom: 4px; 
        text-transform: uppercase; letter-spacing: 0.5px; display: block;
    }
    
    .core-keyword-box {
        background-color: #f0fdf4; border: 1.5px solid #22c55e;
        padding: 12px; border-radius: 6px; margin-bottom: 20px; text-align: center;
    }

    .step-container {display: flex; justify-content: space-between; background: white; padding: 15px 30px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #e0e0e0;}
    .step-item {display: flex; align-items: center; font-weight: 600; color: #5f6368; font-size: 14px;}
    .step-circle {background-color: #e8eaf6; color: #3f51b5; width: 30px; height: 30px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;}
    .step-active .step-circle {background-color: #3f51b5; color: white;}
    .step-active {color: #3f51b5;}
    
    .btn-blue button {background-color: #2962ff !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; border: none; padding: 10px !important;}
    .btn-blue button:hover {background-color: #1c44b2 !important;}
    .btn-green button {background-color: #00897b !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; border: none; padding: 10px !important;}
    .btn-green button:hover {background-color: #00695c !important;}
    .btn-orange button {background-color: #f57c00 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; border: none; padding: 10px !important;}
    .btn-orange button:hover {background-color: #ef6c00 !important;}
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
    st.markdown("ℹ️ Hướng dẫn sử dụng")
    st.markdown("❓ Câu hỏi thường gặp")
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("📞 (028) 3940 0989")
    st.markdown("✉️ thuvien@hcmulaw.edu.vn")

st.markdown("""
<div class="hero-banner">
    <div class="hero-title-small">ULAW SMART REFERENCE SYSTEM</div>
    <div class="hero-title-large">TRA CỨU THÔNG TIN THEO YÊU CẦU</div>
    <div class="hero-subtitle">Hệ thống giúp Thủ thư tra cứu, tổng hợp và xuất báo cáo tài liệu một cách tự động, chính xác và nhanh chóng.</div>
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
        
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        
        st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
        if st.button("🚀 Phân tích bằng AI", use_container_width=True):
            if topic.strip() == "":
                st.error("Vui lòng nhập Tên đề tài!")
            else:
                st.session_state.search_clicked = False 
                with st.spinner("🤖 AI đang phân tích dữ liệu..."):
                    if call_gemini(topic):
                        st.success("✅ Phân tích thành công!")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 2: GIAO DIỆN MỚI THÔNG MINH HƠN ====================
with col2:
    with st.container(border=True):
        st.markdown("<div class='card-header'>💡 2. AI ĐỀ XUẤT TỪ KHÓA</div>", unsafe_allow_html=True)
        
        ai = st.session_state.ai_data
        
        # HIỂN THỊ TỪ KHÓA ĐINH (CORE KEYWORD)
        st.markdown(f"""
        <div class='core-keyword-box'>
            <span style='color:#166534; font-weight:700; font-size:12px; text-transform:uppercase;'>🎯 Từ khóa đinh (Cốt lõi):</span><br>
            <span style='color:#15803d; font-size:18px; font-weight:800;'>{ai.get('tu_khoa_dinh', 'Đang chờ...')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.multiselect("Chuyên ngành luật", ai.get("chuyen_nganh", []), default=ai.get("chuyen_nganh", []))
        
        # --- TIẾNG VIỆT ---
        sel_vn = st.multiselect("Từ khóa tiếng Việt", ai.get("tu_khoa_vn", []), default=ai.get("tu_khoa_vn", []))
        
        st.text_input("➕ Thêm từ (Cách nhau bằng dấu phẩy, ấn Enter tự dịch):", key="input_vn_widget", on_change=on_add_vn, placeholder="VD: mã hóa dữ liệu...")

        if sel_vn and sel_vn[0] != "Đang chờ AI phân tích...":
            vn_queries = ["<span class='query-label'>🔸 Tìm đơn lẻ:</span>"]
            for kw in sel_vn: vn_queries.append(f'"{kw}"')
            if len(sel_vn) > 1:
                vn_queries.append("<span class='query-label'>🔸 Tìm kết hợp (Thu hẹp):</span>")
                vn_queries.append(" AND ".join([f'"{kw}"' for kw in sel_vn]))
            st.markdown(f"<div class='query-preview-box'>{'<br>'.join(vn_queries)}</div>", unsafe_allow_html=True)
        
        # --- TIẾNG ANH ---
        sel_en = st.multiselect("Từ khóa tiếng Anh", ai.get("tu_khoa_en", []), default=ai.get("tu_khoa_en", []))
        
        st.text_input("➕ Thêm từ Tiếng Anh (Ấn Enter):", key="input_en_widget", on_change=on_add_en, placeholder="VD: data encryption...")

        if sel_en and sel_en[0] != "Đang chờ AI phân tích...":
            en_queries = ["<span class='query-label'>🔸 Tìm đơn lẻ:</span>"]
            for kw in sel_en: en_queries.append(f'"{kw}"')
            if len(sel_en) > 1:
                en_queries.append("<span class='query-label'>🔸 Tìm kết hợp (Thu hẹp):</span>")
                en_queries.append(" AND ".join([f'"{kw}"' for kw in sel_en]))
            st.markdown(f"<div class='query-preview-box'>{'<br>'.join(en_queries)}</div>", unsafe_allow_html=True)
        
        # --- ĐẶC THÙ (CHỈ HIỆN KHI CẦN) ---
        sel_dac_thu = []
        if ai.get("co_yeu_to_nuoc_ngoai", False) and ai.get("tu_khoa_dac_thu", []) and ai["tu_khoa_dac_thu"][0] != "Đang chờ AI phân tích...":
            sel_dac_thu = st.multiselect("Từ khóa đặc thù (Quốc tế)", ai.get("tu_khoa_dac_thu", []), default=ai.get("tu_khoa_dac_thu", []))
            if sel_dac_thu:
                dt_queries = ["<span class='query-label'>🔸 Tìm đơn lẻ:</span>"]
                for kw in sel_dac_thu: dt_queries.append(f'"{kw}"')
                st.markdown(f"<div class='query-preview-box'>{'<br>'.join(dt_queries)}</div>", unsafe_allow_html=True)

        if (sel_vn and sel_vn[0] != "Đang chờ AI phân tích...") and sel_dac_thu:
            st.markdown("<hr style='margin:10px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
            combined = [f'"{sel_vn[0]}" AND "{sel_dac_thu[0]}"']
            st.markdown(f"<div class='query-preview-box' style='background-color:#1e293b; border-left:4px solid #34d399;'><span class='query-label' style='color:#34d399;'>🔗 ĐỐI CHIẾU BỐI CẢNH QUỐC TẾ:</span><br>{'<br>'.join(combined)}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            st.markdown("<div class='btn-outline'>", unsafe_allow_html=True)
            if st.button("🔄 Khôi phục", use_container_width=True):
                st.session_state.ai_data = {"chuyen_nganh": ["Đang chờ AI phân tích..."], "tu_khoa_dinh": "Đang chờ AI phân tích...", "tu_khoa_vn": ["Đang chờ AI phân tích..."], "tu_khoa_en": ["Đang chờ AI phân tích..."], "tu_khoa_dac_thu": ["Đang chờ AI phân tích..."], "co_yeu_to_nuoc_ngoai": False}
                st.session_state.search_clicked = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with cb2:
            st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
            st.button("✓ Xác nhận", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 3 & 4 (GIỮ NGUYÊN) ====================
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
        src_ctho = st.checkbox("Đại học Cần Thơ", value=True)
        src_ntg = st.checkbox("Đại học Ngoại thương", value=True)
        
        st.caption("Quốc tế")
        src_hein = st.checkbox("HeinOnline", value=True)
        src_west = st.checkbox("Westlaw", value=True)
        
        st.caption("Pháp quy & Mở rộng")
        src_lvn = st.checkbox("Luật Việt Nam", value=True)
        src_tvpl = st.checkbox("Thư Viện Pháp Luật", value=True)
        src_gg = st.checkbox("Google (Website & CSDL chuyên ngành)", value=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
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
                    "Pháp luật về giải quyết tranh chấp đất đai tại Việt Nam", 
                    "Thực tiễn giải quyết tranh chấp quyền sử dụng đất tại Tòa án", 
                    "Land Disputes and Resolution Mechanisms: A Comparative Study", 
                    "Bình luận án về tranh chấp hợp đồng chuyển nhượng đất đai"
                ],
                "Nguồn": ["ULAW", "TVPL", "HeinOnline", "ĐH Luật HN"],
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

st.markdown("---")
f1, f2, f3, f4, f5 = st.columns(5)
with f1: st.markdown("🚀 **Tự động hóa 80-90%**<br><small>Tiết kiệm thời gian tra cứu</small>", unsafe_allow_html=True)
with f2: st.markdown("🧠 **AI thông minh**<br><small>Đề xuất từ khóa chính xác</small>", unsafe_allow_html=True)
with f3: st.markdown("🛡️ **Kết quả chính xác**<br><small>Lọc trùng lặp, ưu tiên nguồn</small>", unsafe_allow_html=True)
with f4: st.markdown("📄 **Báo cáo chuẩn ULAW**<br><small>Định dạng chính xác, thống kê</small>", unsafe_allow_html=True)
with f5: st.markdown("🕒 **Lưu trữ & Tái sử dụng**<br><small>Lịch sử tra cứu, clone dễ dàng</small>", unsafe_allow_html=True)
