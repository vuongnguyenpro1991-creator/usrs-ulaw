import streamlit as st
import pandas as pd

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="ULAW Smart Reference System", layout="wide", initial_sidebar_state="expanded")

# 2. TÙY CHỈNH CSS CHUYÊN SÂU THEO BẢN THIẾT KẾ
st.markdown("""
<style>
    /* Reset & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    
    /* Màu nền chính */
    .stApp {background-color: #f4f6f9;}
    
    /* Ẩn header mặc định của Streamlit */
    header {visibility: hidden;}
    
    /* SIDEBAR (Cột trái màu xanh đậm) */
    [data-testid="stSidebar"] {background-color: #2b3b7c; color: white;}
    [data-testid="stSidebar"] * {color: white !important;}
    
    /* HERO BANNER */
    .hero-banner {
        background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%);
        padding: 30px; border-radius: 10px; margin-top: -50px; margin-bottom: 20px;
        border: 1px solid #d2e3fc; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .hero-title-small {color: #1a237e; font-weight: 700; font-size: 16px; letter-spacing: 1px;}
    .hero-title-large {color: #1a237e; font-weight: 800; font-size: 32px; margin: 10px 0;}
    .hero-subtitle {color: #5f6368; font-size: 16px;}
    
    /* PROGRESS BAR (Thanh 4 bước) */
    .step-container {
        display: flex; justify-content: space-between; background: white; 
        padding: 15px 30px; border-radius: 10px; margin-bottom: 20px;
        border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .step-item {display: flex; align-items: center; font-weight: 600; color: #5f6368; font-size: 14px;}
    .step-circle {
        background-color: #e8eaf6; color: #3f51b5; width: 30px; height: 30px; 
        border-radius: 50%; display: flex; justify-content: center; align-items: center; 
        margin-right: 10px; font-weight: bold;
    }
    .step-active .step-circle {background-color: #3f51b5; color: white;}
    .step-active {color: #3f51b5;}
    
    /* NÚT BẤM (Màu cam cho nút Xuất báo cáo, Xanh cho nút Tiếp tục) */
    .btn-blue button {background-color: #2962ff !important; color: white !important; width: 100%; border-radius: 6px !important;}
    .btn-orange button {background-color: #f57c00 !important; color: white !important; width: 100%; border-radius: 6px !important;}
    .btn-outline button {background-color: white !important; color: #3f51b5 !important; border: 1px solid #3f51b5 !important; width: 100%;}
    
    /* Định dạng cột (Cards) */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    /* Tiêu đề Card */
    .card-header {font-weight: 700; color: #1a237e; font-size: 16px; margin-bottom: 15px; display: flex; align-items: center;}
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR (Cột trái)
with st.sidebar:
    st.markdown("### 🏛️ THƯ VIỆN ULAW")
    st.markdown("---")
    st.markdown("🏠 Trang chủ")
    st.markdown("📝 Tạo yêu cầu tra cứu")
    st.markdown("⏱️ Lịch sử yêu cầu")
    st.markdown("📁 Kho báo cáo")
    st.markdown("ℹ️ Hướng dẫn sử dụng")
    st.markdown("❓ Câu hỏi thường gặp")
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("📞 (028) 3720 6509")
    st.markdown("✉️ thuvien@hcmulaw.edu.vn")
    st.markdown("🕒 Thứ 2 - Thứ 6: 07:30 - 21:00")

# 4. HERO BANNER
st.markdown("""
<div class="hero-banner">
    <div class="hero-title-small">ULAW SMART REFERENCE SYSTEM</div>
    <div class="hero-title-large">TRA CỨU THÔNG TIN THEO YÊU CẦU</div>
    <div class="hero-subtitle">Hệ thống giúp Thủ thư tra cứu, tổng hợp và xuất báo cáo tài liệu một cách tự động, chính xác và nhanh chóng.</div>
</div>
""", unsafe_allow_html=True)

# 5. THANH TIẾN TRÌNH 4 BƯỚC
st.markdown("""
<div class="step-container">
    <div class="step-item step-active"><div class="step-circle">1</div> Khởi tạo yêu cầu</div>
    <div class="step-item step-active"><div class="step-circle">2</div> AI đề xuất từ khóa</div>
    <div class="step-item step-active"><div class="step-circle">3</div> Chọn nguồn tra cứu</div>
    <div class="step-item step-active"><div class="step-circle" style="background-color:#f57c00;color:white;">4</div> Kiểm duyệt & xuất báo cáo</div>
</div>
""", unsafe_allow_html=True)

# 6. BỐ CỤC 4 CỘT CHÍNH (Tương ứng 4 bước trong ảnh)
col1, col2, col3, col4 = st.columns(4)

# CỘT 1: KHỞI TẠO YÊU CẦU
with col1:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📋 1. KHỞI TẠO YÊU CẦU</div>", unsafe_allow_html=True)
        topic = st.text_input("Tên đề tài nghiên cứu *", placeholder="Nhập tên đề tài...")
        author = st.text_input("Tên người/nhóm yêu cầu *", placeholder="Nhập tên người yêu cầu...")
        
        st.caption("Khoảng thời gian xuất bản")
        c1, c2 = st.columns(2)
        with c1: year_start = st.number_input("Từ", value=2020, step=1, label_visibility="collapsed")
        with c2: year_end = st.number_input("Đến", value=2026, step=1, label_visibility="collapsed")
        
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True) # Đệm khoảng trống
        st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
        st.button("Tiếp tục →", key="btn_step1", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# CỘT 2: AI ĐỀ XUẤT TỪ KHÓA
with col2:
    with st.container(border=True):
        st.markdown("<div class='card-header'>💡 2. AI ĐỀ XUẤT TỪ KHÓA</div>", unsafe_allow_html=True)
        st.multiselect("Chuyên ngành luật", ["Luật Dân sự", "Luật Thương mại", "Luật Đầu tư"], default=["Luật Dân sự", "Luật Thương mại", "Luật Đầu tư"])
        st.multiselect("Từ khóa tiếng Việt", ["hợp đồng", "thanh toán", "tranh chấp"], default=["hợp đồng", "thanh toán", "tranh chấp"])
        st.multiselect("Từ khóa tiếng Anh", ["contract", "payment", "dispute"], default=["contract", "payment", "dispute"])
        st.multiselect("Từ khóa đặc thù", ["CISG", "FDCPA", "INCOTERMS"], default=["CISG", "FDCPA", "INCOTERMS"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            st.markdown("<div class='btn-outline'>", unsafe_allow_html=True)
            st.button("🔄 Đề xuất lại", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with cb2:
            st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
            st.button("✓ Xác nhận", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# CỘT 3: CHỌN NGUỒN TRA CỨU
with col3:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📚 3. CHỌN NGUỒN TRA CỨU</div>", unsafe_allow_html=True)
        
        st.caption("Nội bộ")
        st.checkbox("OPAC Thư viện ULAW", value=True)
        st.checkbox("Cơ sở dữ liệu nội sinh", value=True)
        
        st.caption("Liên kết")
        st.checkbox("Thư viện ĐH Luật Hà Nội", value=True)
        st.checkbox("Thư viện ĐHQG Hà Nội", value=True)
        st.checkbox("Thư viện ĐH Kinh tế - Luật", value=True)
        
        st.caption("Quốc tế")
        st.checkbox("HeinOnline", value=True)
        st.checkbox("Westlaw", value=True)
        
        st.caption("Pháp quy")
        st.checkbox("Thư viện Pháp luật", value=True)
        st.checkbox("Luật Việt Nam", value=True)
        
        st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
        st.button("Tiếp tục →", key="btn_step3", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# CỘT 4: KIỂM DUYỆT & XUẤT BÁO CÁO
with col4:
    with st.container(border=True):
        st.markdown("<div class='card-header'>🏠 4. KIỂM DUYỆT & XUẤT BÁO CÁO</div>", unsafe_allow_html=True)
        
        st.markdown("<small style='color:#5f6368;'>Tiến trình tra cứu: <b>78%</b></small>", unsafe_allow_html=True)
        st.progress(78)
        st.markdown("<small style='color:#5f6368;'>Đang truy vấn: HeinOnline... (5/8 nguồn)</small>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.markdown("<b>Kết quả tìm thấy: 128 tài liệu</b>", unsafe_allow_html=True)
        
        # Bảng dữ liệu mô phỏng
        data = {
            "#": [1, 2, 3, 4],
            "Tiêu đề": ["Pháp luật về hợp đồng...", "Giải quyết tranh chấp...", "Thực tiễn áp dụng...", "Contract and dispute..."],
            "Nguồn": ["ULAW", "UEL", "ĐH Luật HN", "HeinOnline"],
            "Chọn": [True, True, True, True]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-orange'>", unsafe_allow_html=True)
        if st.button("📥 Xuất báo cáo DOCX chuẩn ULAW", use_container_width=True):
            st.snow() # Hiệu ứng khi bấm nút xuất báo cáo
        st.markdown("</div>", unsafe_allow_html=True)

# 7. FOOTER 5 TÍNH NĂNG Ở ĐÁY
st.markdown("---")
f1, f2, f3, f4, f5 = st.columns(5)
with f1: st.markdown("🚀 **Tự động hóa 80-90%**<br><small>Tiết kiệm thời gian tra cứu</small>", unsafe_allow_html=True)
with f2: st.markdown("🧠 **AI thông minh**<br><small>Đề xuất từ khóa chính xác</small>", unsafe_allow_html=True)
with f3: st.markdown("🛡️ **Kết quả chính xác**<br><small>Lọc trùng lặp, ưu tiên nguồn</small>", unsafe_allow_html=True)
with f4: st.markdown("📄 **Báo cáo chuẩn ULAW**<br><small>Định dạng chính xác, thống kê</small>", unsafe_allow_html=True)
with f5: st.markdown("🕒 **Lưu trữ & Tái sử dụng**<br><small>Lịch sử tra cứu, clone dễ dàng</small>", unsafe_allow_html=True)
