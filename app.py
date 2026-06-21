import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# 1. CẤU HÌNH TRANG WEB & BỘ NHỚ HỆ THỐNG
st.set_page_config(page_title="ULAW Smart Reference System", layout="wide", initial_sidebar_state="expanded")

# Khởi tạo dữ liệu mẫu nếu chưa có dữ liệu từ AI
if 'ai_data' not in st.session_state:
    st.session_state.ai_data = {
        "chuyen_nganh": ["Luật Dân sự", "Luật Thương mại Quốc tế"],
        "tu_khoa_vn": ["dịch vụ đòi nợ", "tài sản bảo đảm", "tranh chấp hợp đồng"],
        "tu_khoa_en": ["debt collection", "collateral", "contract dispute"],
        "tu_khoa_dac_thu": ["FDCPA", "Servicer Act"], # Có sẵn từ khóa nước ngoài để test tính năng conditional
        "co_yeu_to_nuoc_ngoai": True # Đánh dấu đề tài có liên quan đến pháp luật nước ngoài hay không
    }

def call_gemini(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3.5-flash') 
        
        prompt = f"""Bạn là một Chuyên gia Thư viện và Luật sư giỏi tại Đại học Luật TP.HCM.
Nhiệm vụ: Phân tích đề tài nghiên cứu sau: "{topic}"
Yêu cầu: Hãy kiểm tra xem đề tài này có cần tra cứu pháp luật nước ngoài hoặc các bộ luật/đạo luật đặc thù quốc tế (ví dụ: CISG, FDCPA, UCC, INCOTERMS...) hay không.
Trả về ĐÚNG định dạng JSON dưới đây, không giải thích gì thêm, không dùng dấu markdown (```json):
{{
  "chuyen_nganh": ["tên chuyên ngành 1", "tên chuyên ngành 2"],
  "tu_khoa_vn": ["từ khóa 1", "từ khóa 2"],
  "tu_khoa_en": ["keyword 1", "keyword 2"],
  "tu_khoa_dac_thu": ["tên đạo luật/bộ luật nước ngoài đặc thù nếu có, nếu không có thì để mảng rỗng []"],
  "co_yeu_to_nuoc_ngoai": true hoặc false (ghi true nếu có đạo luật đặc thù hoặc có quốc gia nước ngoài xuất hiện trong đề tài, ngược lại ghi false)
}}"""
        response = model.generate_content(prompt)
        text_result = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        
        data = json.loads(text_result)
        st.session_state.ai_data = data
        return True
    except Exception as e:
        st.error(f"Lỗi hệ thống AI: {e}")
        return False

# 2. TÙY CHỈNH CSS CHUYÊN SÂU (TỐI ƯU CÁC Ô NHẬP LIỆU VÀ NỀN TIÊU ĐỀ ĐẬM THEO YÊU CẦU)
st.markdown("""
<style>
    @import url('[https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap)');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stApp {background-color: #f4f6f9;}
    header {visibility: hidden;}
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {background-color: #2b3b7c; color: white;}
    [data-testid="stSidebar"] * {color: white !important;}
    
    /* HERO BANNER CÓ NỀN ĐẬM HƠN VÀ CANH GIỮA NỀN ẢNH THƯ VIỆN */
    .hero-banner {
        background-image: linear-gradient(rgba(12, 19, 79, 0.9), rgba(12, 19, 79, 0.9)), url('[https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=2000&auto=format&fit=crop](https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=2000&auto=format&fit=crop)');
        background-size: cover; background-position: center;
        padding: 45px 30px; border-radius: 10px; margin-top: -50px; margin-bottom: 25px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    .hero-title-small {color: #90caf9; font-weight: 700; font-size: 16px; letter-spacing: 1.5px; text-transform: uppercase;}
    .hero-title-large {color: #ffffff; font-weight: 800; font-size: 36px; margin: 15px 0;}
    .hero-subtitle {color: #e3f2fd; font-size: 16px; max-width: 800px; margin: 0 auto;}
    
    /* Ô NHẬP DỮ LIỆU ĐẬM MÀU HƠN ĐỂ NỔI BẬT TRÊN NỀN TRẮNG */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, .stNumberInput input {
        background-color: #e2e8f0 !important; /* Đậm màu hơn bản cũ */
        border: 1.5px solid #94a3b8 !important;
        color: #0f172a !important;
    }
    
    /* TIÊU ĐỀ ĐẦU MỤC CÓ NỀN ĐẬM LÊN 1 CHÚT (CARD HEADER LUXURY) */
    .card-header {
        font-weight: 700; color: #0c134f; font-size: 15px; margin-bottom: 20px; 
        background-color: #dbeafe; padding: 12px 15px; border-radius: 6px;
        border-left: 5px solid #1d4ed8;
    }
    
    /* Ô HIỂN THỊ CHUỖI TRUY VẤN MINH BẠCH (QUERY PREVIEW BOX) */
    .query-preview-box {
        background-color: #0f172a; color: #38bdf8; padding: 12px; 
        border-radius: 6px; font-family: 'Courier New', Courier, monospace; 
        font-size: 13px; margin-top: 5px; margin-bottom: 15px;
        border-left: 4px solid #38bdf8; overflow-x: auto;
    }
    .query-label {font-size: 13px; font-weight: 600; color: #1e293b; margin-top: 10px; margin-bottom: 2px;}

    /* CẤU TRÚC KHUNG CHỨA KHỐI CHỨC NĂNG */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .scrollable-source {max-height: 380px; overflow-y: auto; padding-right: 10px;}
    
    /* NÚT BẤM CÓ MÀU SẮC NỔI BẬT THEO TỪNG HÀNH ĐỘNG */
    .btn-blue button {background-color: #1d4ed8 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; padding: 10px !important; border: none;}
    .btn-blue button:hover {background-color: #1e40af !important;}
    
    .btn-green button {background-color: #0d9488 !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; padding: 10px !important; border: none;}
    .btn-green button:hover {background-color: #0f766e !important;}
    
    .btn-orange button {background-color: #ea580c !important; color: white !important; width: 100%; border-radius: 8px !important; font-weight: 700 !important; padding: 10px !important; border: none;}
    .btn-orange button:hover {background-color: #c2410c !important;}
    
    .btn-outline button {background-color: white !important; color: #1d4ed8 !important; border: 1.5px solid #1d4ed8 !important; width: 100%; border-radius: 8px !important;}
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR (Logo & Điều hướng)
with st.sidebar:
    col_logo1, col_logo2, col_logo3 = st.columns([1,3,1])
    with col_logo2:
        try: st.image("logo_ulaw.png", use_column_width=True)
        except Exception: pass
            
    st.markdown("<h3 style='text-align: center; color: white;'>THƯ VIỆN ULAW</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🏠 Trang chủ")
    st.markdown("📝 Tạo yêu cầu tra cứu")
    st.markdown("⏱️ Lịch sử yêu cầu")
    st.markdown("📁 Kho báo cáo")
    st.markdown("---")
    st.markdown("📞 (028) 3940 0989")

# HERO BANNER CANH GIỮA NỀN ĐẬM
st.markdown("""
<div class="hero-banner">
    <div class="hero-title-small">ULAW SMART REFERENCE SYSTEM</div>
    <div class="hero-title-large">TRA CỨU THÔNG TIN THEO YÊU CẦU</div>
    <div class="hero-subtitle">Hệ thống hỗ trợ Thủ thư tự động hóa quy trình phân tích dữ liệu, tra cứu chéo nguồn tài liệu và đóng gói báo cáo chuẩn định dạng Thư viện ULAW.</div>
</div>
""", unsafe_allow_html=True)

# 4. BỐ CỤC 4 CỘT CHÍNH
col1, col2, col3, col4 = st.columns(4)

# ==================== CỘT 1: KHỞI TẠO YÊU CẦU ====================
with col1:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📋 1. KHỞI TẠO YÊU CẦU</div>", unsafe_allow_html=True)
        topic = st.text_input("Tên đề tài nghiên cứu *", placeholder="Nhập tên đề tài cần tra cứu...")
        author = st.text_input("Tên người/nhóm yêu cầu *", placeholder="VD: Trần Thị Xuân Thông")
        
        st.caption("Khoảng thời gian xuất bản")
        c1, c2 = st.columns(2)
        with c1: year_start = st.number_input("Từ", value=2020, step=1, label_visibility="collapsed")
        with c2: year_end = st.number_input("Đến", value=2026, step=1, label_visibility="collapsed")
        
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        
        st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
        if st.button("🚀 Phân tích bằng AI", use_container_width=True):
            if topic.strip() == "":
                st.error("Vui lòng nhập Tên đề tài trước khi phân tích!")
            else:
                with st.spinner("🤖 AI đang tối ưu hóa thuật ngữ..."):
                    if call_gemini(topic):
                        st.success("✅ Đã đồng bộ từ khóa!")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 2: AI ĐỀ XUẤT TỪ KHÓA (CẬP NHẬT MỚI) ====================
with col2:
    with st.container(border=True):
        st.markdown("<div class='card-header'>💡 2. AI ĐỀ XUẤT TỪ KHÓA</div>", unsafe_allow_html=True)
        
        ai = st.session_state.ai_data
        
        # 2.1 Chọn chuyên ngành
        sel_chuyen_nganh = st.multiselect("Chuyên ngành luật", ai["chuyen_nganh"], default=ai["chuyen_nganh"])
        
        # 2.2 Chọn từ khóa tiếng Việt & Hiển thị chuỗi tìm kiếm đơn lẻ/kết hợp ngầm định
        sel_vn = st.multiselect("Từ khóa tiếng Việt", ai["tu_khoa_vn"], default=ai["tu_khoa_vn"])
        
        # 2.3 Chọn từ khóa tiếng Anh & Hiển thị chuỗi tìm kiếm
        sel_en = st.multiselect("Từ khóa tiếng Anh", ai["tu_khoa_en"], default=ai["tu_khoa_en"])
        
        # XỬ LÝ ĐỀ XUẤT 1: Chỉ hiện Từ khóa đặc thù khi đề tài có yếu tố nước ngoài / luật đặc thù
        if ai.get("co_yeu_to_nuoc_ngoai", False) and len(ai["tu_khoa_dac_thu"]) > 0:
            sel_dac_thu = st.multiselect("Từ khóa đặc thù (Pháp luật quốc tế)", ai["tu_khoa_dac_thu"], default=ai["tu_khoa_dac_thu"])
        else:
            sel_dac_thu = []

        # XỬ LÝ ĐỀ XUẤT 2: Ô HIỂN THỊ CHUỖI TRUY VẤN MÁY SẼ CHẠY ĐỂ KIỂM SOÁT HỆ THỐNG
        st.markdown("<hr style='margin:15px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px; font-weight:700; color:#1e3a8a; margin-bottom:5px;'>🔍 ĐANG XEM TRƯỚC CHUỖI TRUY VẤN MÁY SẼ TÌM:</p>", unsafe_allow_html=True)
        
        # Thuật toán tự động ghép chuỗi để hiển thị trực quan cho Thủ thư
        if len(sel_vn) > 0:
            st.markdown("<div class='query-label'>Lớp 1: Tìm chính xác (Đơn lẻ)</div>", unsafe_allow_html=True)
            vn_queries = "<br>".join([f'"{keyword}"' for keyword in sel_vn])
            st.markdown(f"<div class='query-preview-box'>{vn_queries}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='query-label'>Lớp 2: Tìm đối chiếu (Kết hợp bối cảnh)</div>", unsafe_allow_html=True)
            combined_queries = []
            # Ghép cặp từ khóa Việt - Anh hoặc kết hợp quốc gia đặc thù
            if len(sel_en) > 0:
                combined_queries.append(f'"{sel_vn[0]}" AND "{sel_en[0]}"')
            if len(sel_dac_thu) > 0:
                combined_queries.append(f'"{sel_vn[0]}" AND "{sel_dac_thu[0]}"')
            else:
                combined_queries.append(f'"{sel_vn[0]}" AND "Việt Nam"')
            
            st.markdown("<div class='query-preview-box'>"+"<br>".join(combined_queries)+"</div>", unsafe_allow_html=True)
        else:
            st.caption("Nhập tên đề tài ở cột 1 để sinh chuỗi lệnh truy vấn hệ thống.")

        st.markdown("<br>", unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            st.markdown("<div class='btn-outline'>", unsafe_allow_html=True)
            if st.button("🔄 Khôi phục", use_container_width=True):
                st.session_state.ai_data = {"chuyen_nganh": [], "tu_khoa_vn": [], "tu_khoa_en": [], "tu_khoa_dac_thu": [], "co_yeu_to_nuoc_ngoai": False}
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with cb2:
            st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
            st.button("✓ Xác nhận", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 3: CHỌN NGUỒN TRA CỨU ====================
with col3:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📚 3. CHỌN NGUỒN TRA CỨU</div>", unsafe_allow_html=True)
        st.markdown("<div class='scrollable-source'>", unsafe_allow_html=True)
        
        st.caption("Nội bộ & Thư viện Quốc gia")
        st.checkbox("Thư viện Trường ĐH Luật TP.HCM", value=True)
        st.checkbox("Thư viện Quốc gia Việt Nam", value=True)
        st.checkbox("Thư viện Khoa học Tổng hợp TP.HCM", value=True)
        
        st.caption("Trường Đại học liên kết")
        st.checkbox("Đại học Kinh tế - Luật (UEL)", value=True)
        st.checkbox("Đại học Luật Hà Nội", value=True)
        st.checkbox("Đại học Quốc gia Hà Nội", value=True)
        st.checkbox("Đại học Luật – Đại học Huế", value=True)
        st.checkbox("Đại học Cần Thơ", value=True)
        st.checkbox("Đại học Ngoại thương", value=True)
        
        st.caption("Quốc tế")
        st.checkbox("HeinOnline", value=True)
        st.checkbox("Westlaw", value=True)
        
        st.caption("Pháp quy & Mở rộng")
        st.checkbox("Luật Việt Nam", value=True)
        st.checkbox("Thư Viện Pháp Luật", value=True)
        st.checkbox("Google (Website & CSDL chuyên ngành)", value=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<div class='btn-green'>", unsafe_allow_html=True)
        st.button("🔍 Bắt đầu Tra cứu", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== CỘT 4: XUẤT BÁO CÁO ====================
with col4:
    with st.container(border=True):
        st.markdown("<div class='card-header'>🏠 4. KIỂM DUYỆT & XUẤT BÁO CÁO</div>", unsafe_allow_html=True)
        st.markdown("<small style='color:#5f6368;'>Tiến trình tra cứu: <b>0%</b></small>", unsafe_allow_html=True)
        st.progress(0)
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.markdown("<b>Kết quả tìm thấy: 0 tài liệu</b>", unsafe_allow_html=True)
        st.info("Bấm 'Bắt đầu Tra cứu' ở Cột 3 để cào dữ liệu chéo nguồn.")
        
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-orange'>", unsafe_allow_html=True)
        if st.button("📥 Xuất báo cáo DOCX chuẩn ULAW", use_container_width=True):
            st.snow()
        st.markdown("</div>", unsafe_allow_html=True)

# 5. FOOTER TÍNH NĂNG ĐÁY
st.markdown("---")
f1, f2, f3, f4, f5 = st.columns(5)
with f1: st.markdown("🚀 **Tự động hóa 80-90%**<br><small>Tiết kiệm thời gian tra cứu</small>", unsafe_allow_html=True)
with f2: st.markdown("🧠 **AI thông minh**<br><small>Đề xuất từ khóa chính xác</small>", unsafe_allow_html=True)
with f3: st.markdown("🛡️ **Kết quả chính xác**<br><small>Lọc trùng lặp, ưu tiên nguồn</small>", unsafe_allow_html=True)
with f4: st.markdown("📄 **Báo cáo chuẩn ULAW**<br><small>Định dạng chính xác, thống kê</small>", unsafe_allow_html=True)
with f5: st.markdown("🕒 **Lưu trữ & Tái sử dụng**<br><small>Lịch sử tra cứu, clone dễ dàng</small>", unsafe_allow_html=True)
