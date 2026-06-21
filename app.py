import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import os

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

def call_gemini(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3.5-flash') 
        
        prompt = f"""Bạn là một Chuyên gia Thư viện học và Luật sư cấp cao tại Đại học Luật TP.HCM. 
Nhiệm vụ: Phân tích đề tài nghiên cứu sau để tạo ra bộ từ khóa tra cứu cơ sở dữ liệu chuyên ngành: "{topic}".
LƯU Ý NGHIỆP VỤ THƯ VIỆN ĐẶC BIỆT QUAN TRỌNG:
1. Từ khóa phải là CỤM TỪ CÓ NGHĨA PHÁP LÝ HOÀN CHỈNH, đủ hẹp để không sinh ra dữ liệu rác.
2. TUYỆT ĐỐI KHÔNG tách các danh từ chủ thể chung chung thành từ khóa đơn lẻ. (Ví dụ: KHÔNG BAO GIỜ để các từ "khách hàng", "ngân hàng", "doanh nghiệp", "nhà nước", "cá nhân", "tòa án" đứng một mình).
3. Buộc phải ghép các chủ thể chung chung với hành vi/quyền lợi pháp lý tương ứng trong đề tài. (Ví dụ: thay vì "khách hàng", hãy dùng "quyền lợi khách hàng" hoặc "bảo vệ khách hàng"; thay vì "ngân hàng", hãy dùng "hoạt động ngân hàng" hoặc "thanh toán qua ngân hàng").
4. Tiếp tục bỏ qua các từ mào đầu: "thực tiễn", "đường lối", "giải quyết", "quy định", "pháp luật", "bất cập", "hoàn thiện", "một số vấn đề".
5. Kiểm tra xem đề tài có liên quan đến pháp luật nước ngoài hay đạo luật đặc thù quốc tế (CISG, FDCPA...) không.
Trả về ĐÚNG JSON: {{"chuyen_nganh": ["..."], "tu_khoa_vn": ["..."], "tu_khoa_en": ["..."], "tu_khoa_dac_thu": ["..."], "co_yeu_to_nuoc_ngoai": true/false}} không giải thích thêm."""
        
        response = model.generate_content(prompt)
        text_result = response.text.strip().removeprefix("```json").removesuffix("```").strip()
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

    .query-preview-box {
        background-color: #0f172a; color: #38bdf8; padding: 10px 12px; 
        border-radius: 6px; font-family: 'Courier New', Courier, monospace; 
        font-size: 12.5px; margin-top: -12px; margin-bottom: 15px;
        border-left: 4px solid #38bdf8; overflow-x: auto; line-height: 1.4;
    }
    .query-label {font-size: 12.5px; font-weight: 700; color: #1e293b; margin-top: 8px; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.3px;}

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

with col2:
    with st.container(border=True):
        st.markdown("<div class='card-header'>💡 2. AI ĐỀ XUẤT TỪ KHÓA</div>", unsafe_allow_html=True)
        
        ai = st.session_state.ai_data
        st.multiselect("Chuyên ngành luật", ai.get("chuyen_nganh", []), default=ai.get("chuyen_nganh", []))
        
        # --- KHỐI TIẾNG VIỆT ---
        sel_vn = st.multiselect("Từ khóa tiếng Việt", ai.get("tu_khoa_vn", []), default=ai.get("tu_khoa_vn", []))
        
        # Đã cập nhật tính năng tách chuỗi dấu phẩy và tự động xóa text sau khi ấn Enter
        custom_vn = st.text_input("➕ Thêm từ (Cách nhau bằng dấu phẩy, ấn Enter):", key="input_vn", placeholder="VD: thanh toán số, mã hóa dữ liệu...")
        if custom_vn:
            # Cắt chuỗi bằng dấu phẩy, loại bỏ khoảng trắng thừa
            new_kws = [k.strip() for k in custom_vn.split(',') if k.strip()]
            
            # Xóa dòng chữ mặc định "Đang chờ AI..." nếu có
            if st.session_state.ai_data["tu_khoa_vn"] == ["Đang chờ AI phân tích..."]:
                st.session_state.ai_data["tu_khoa_vn"] = []
                
            # Đẩy hàng loạt từ mới vào danh sách
            for kw in new_kws:
                if kw not in st.session_state.ai_data["tu_khoa_vn"]:
                    st.session_state.ai_data["tu_khoa_vn"].append(kw)
            
            del st.session_state['input_vn'] # Tuyệt chiêu xóa trắng ô input
            st.rerun()

        if sel_vn and sel_vn[0] != "Đang chờ AI phân tích...":
            vn_queries = ["<span class='query-label'>🔸 Tìm đơn lẻ:</span>"]
            for kw in sel_vn: vn_queries.append(f'"{kw}"')
            if len(sel_vn) > 1:
                vn_queries.append("<span class='query-label'>🔸 Tìm kết hợp (Thu hẹp):</span>")
                vn_queries.append(" AND ".join([f'"{kw}"' for kw in sel_vn]))
            st.markdown(f"<div class='query-preview-box'>🔍 Máy tìm Tiếng Việt:<br>{'<br>'.join(vn_queries)}</div>", unsafe_allow_html=True)
        
        # --- KHỐI TIẾNG ANH ---
        sel_en = st.multiselect("Từ khóa tiếng Anh", ai.get("tu_khoa_en", []), default=ai.get("tu_khoa_en", []))
        
        custom_en = st.text_input("➕ Thêm từ (Cách nhau bằng dấu phẩy, ấn Enter):", key="input_en", placeholder="VD: digital payment, data encryption...")
        if custom_en:
            new_kws = [k.strip() for k in custom_en.split(',') if k.strip()]
            if st.session_state.ai_data["tu_khoa_en"] == ["Đang chờ AI phân tích..."]:
                st.session_state.ai_data["tu_khoa_en"] = []
                
            for kw in new_kws:
                if kw not in st.session_state.ai_data["tu_khoa_en"]:
                    st.session_state.ai_data["tu_khoa_en"].append(kw)
            
            del st.session_state['input_en'] # Tuyệt chiêu xóa trắng ô input
            st.rerun()

        if sel_en and sel_en[0] != "Đang chờ AI phân tích...":
            en_queries = ["<span class='query-label'>🔸 Tìm đơn lẻ:</span>"]
            for kw in sel_en: en_queries.append(f'"{kw}"')
            if len(sel_en) > 1:
                en_queries.append("<span class='query-label'>🔸 Tìm kết hợp (Thu hẹp):</span>")
                en_queries.append(" AND ".join([f'"{kw}"' for kw in sel_en]))
            st.markdown(f"<div class='query-preview-box'>🔍 Máy tìm Tiếng Anh:<br>{'<br>'.join(en_queries)}</div>", unsafe_allow_html=True)
        
        # --- KHỐI ĐẶC THÙ QUỐC TẾ ---
        sel_dac_thu = []
        if ai.get("co_yeu_to_nuoc_ngoai", False) and ai.get("tu_khoa_dac_thu", []) and ai["tu_khoa_dac_thu"][0] != "Đang chờ AI phân tích...":
            sel_dac_thu = st.multiselect("Từ khóa đặc thù (Quốc tế)", ai.get("tu_khoa_dac_thu", []), default=ai.get("tu_khoa_dac_thu", []))
            if sel_dac_thu:
                dt_queries = ["<span class='query-label'>🔸 Tìm đơn lẻ:</span>"]
                for kw in sel_dac_thu: dt_queries.append(f'"{kw}"')
                st.markdown(f"<div class='query-preview-box'>🔍 Máy tìm Đặc thù riêng lẻ:<br>{'<br>'.join(dt_queries)}</div>", unsafe_allow_
