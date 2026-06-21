import streamlit as st

# 1. CẤU HÌNH TRANG WEB (Loại bỏ khoảng trắng thừa, thiết kế mở rộng)
st.set_page_config(page_title="Cổng Tra cứu Thông tin - ULAW", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# 2. TÙY CHỈNH CSS CHUYÊN SÂU (Mô phỏng cấu trúc Portal Thư viện)
st.markdown("""
<style>
    /* Reset padding mặc định của Streamlit để giao diện tràn viền đẹp hơn */
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 1200px;}
    
    /* Phông chữ */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {font-family: 'Roboto', sans-serif;}

    /* HEADER - THANH ĐIỀU HƯỚNG TRÊN CÙNG */
    .top-header {
        background-color: #003366; /* Xanh ULAW */
        color: white;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px 8px 0 0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .top-header-logo {font-size: 18px; font-weight: 700; letter-spacing: 1px;}
    .top-header-links a {
        color: white; 
        text-decoration: none; 
        margin-left: 25px; 
        font-size: 14px; 
        font-weight: 500;
        transition: opacity 0.3s;
    }
    .top-header-links a:hover {opacity: 0.7;}

    /* HERO SECTION - KHU VỰC GIỚI THIỆU */
    .hero-section {
        background-color: #f8f9fa;
        padding: 35px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 25px;
    }
    .hero-title {color: #003366; font-size: 26px; font-weight: 700; margin-bottom: 15px;}
    .hero-text {color: #444; font-size: 16px; margin-bottom: 25px; line-height: 1.6;}
    .quote-box {
        font-style: italic; color: #555; font-size: 15px; 
        border-left: 4px solid #cc9900; /* Màu vàng Gold ULAW */
        padding-left: 15px; margin-bottom: 25px;
    }

    /* ACTION BUTTONS - 4 NÚT CHỨC NĂNG (Giống ảnh mẫu) */
    .action-row {display: flex; justify-content: space-between; gap: 20px; margin-bottom: 10px;}
    .action-card {
        flex: 1; text-align: center; border: 1.5px solid #003366; color: #003366;
        padding: 12px; border-radius: 6px; font-weight: 600; font-size: 15px;
        background-color: white; cursor: pointer; transition: all 0.3s;
    }
    .action-card:hover {background-color: #003366; color: white;}

    /* KHU VỰC NHẬP LIỆU (FORM) */
    .form-container {
        border: 1px solid #dcdcdc; padding: 25px; border-radius: 8px;
        background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .form-title {color: #003366; font-size: 20px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #cc9900; padding-bottom: 10px; display: inline-block;}
    
    /* FOOTER */
    .footer-section {
        background-color: #003366; color: white; padding: 40px 30px;
        display: flex; justify-content: space-between; border-radius: 8px; margin-top: 50px;
    }
    .footer-col {flex: 1; margin: 0 15px;}
    .footer-title {font-weight: 700; font-size: 16px; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 10px; margin-bottom: 20px; letter-spacing: 1px;}
    .footer-text {font-size: 14px; margin-bottom: 10px; color: #e0e0e0;}
</style>
""", unsafe_allow_html=True)

# 3. HEADER (Thanh điều hướng giống Portal)
st.markdown("""
<div class="top-header">
    <div class="top-header-logo">🏛️ THƯ VIỆN TRƯỜNG ĐH LUẬT TP.HCM</div>
    <div class="top-header-links">
        <a href="#">Trang chủ</a>
        <a href="#">Danh mục lưu</a>
        <a href="#">Lịch sử tra cứu</a>
        <a href="#">👤 Đăng nhập (Thủ thư)</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. HERO SECTION & 4 NÚT TÍNH NĂNG CHÍNH
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Chào mừng đến với Cổng tra cứu thông tin thông minh (USRS)</div>
    <div class="hero-text">Hệ thống hỗ trợ cán bộ thư viện tự động hóa quy trình phân tích đề tài, tra cứu thư mục, loại bỏ trùng lặp và xuất báo cáo chuẩn định dạng ULAW.</div>
    <div class="quote-box">"Sứ mệnh của chúng tôi là kết nối tri thức pháp lý, xây dựng nền tảng nghiên cứu học thuật chuẩn mực."</div>
    <div class="action-row">
        <div class="action-card">🔍 Tra cứu Học thuật (USRS)</div>
        <div class="action-card">🌐 CSDL Điện tử (OPAC)</div>
        <div class="action-card">❓ Trợ giúp (FAQs)</div>
        <div class="action-card">✉️ Liên hệ Thủ thư</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. KHU VỰC NHẬP LIỆU TRA CỨU CHÍNH TÂM
st.markdown("<div class='form-container'>", unsafe_allow_html=True)
st.markdown("<div class='form-title'>BẢNG ĐIỀU KHIỂN TRA CỨU ĐỀ TÀI</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1]) # Chia cột linh hoạt hơn

with col1:
    topic = st.text_input("TÊN ĐỀ TÀI NGHIÊN CỨU HOẶC TỪ KHÓA:", placeholder="Nhập tên đề tài cần phân tích...")
    requester = st.text_input("TÊN NGƯỜI YÊU CẦU (TÁC GIẢ):", placeholder="VD: Trần Thị Xuân Thông")

with col2:
    # XỬ LÝ YÊU CẦU CỦA BẠN: Có giới hạn hoặc Không giới hạn thời gian
    st.markdown("<p style='font-size: 14px; font-weight: 500; color: #31333F; margin-bottom: 5px;'>GIỚI HẠN THỜI GIAN TÀI LIỆU:</p>", unsafe_allow_html=True)
    time_option = st.radio("Lựa chọn:", ["Tất cả các năm (Không giới hạn)", "Có giới hạn thời gian"], label_visibility="collapsed")
    
    if time_option == "Có giới hạn thời gian":
        time_filter = st.slider("Chọn khoảng năm xuất bản:", 1990, 2026, (2015, 2026))
    else:
        st.info("💡 Hệ thống sẽ quét toàn bộ tài liệu từ trước đến nay.")

st.markdown("<br>", unsafe_allow_html=True)

# Thiết kế nút bấm Action cực kỳ nổi bật
col_btn1, col_btn2, col_btn3 = st.columns([1, 1.5, 1])
with col_btn2:
    if st.button("PHÂN TÍCH ĐỀ TÀI & SINH TỪ KHÓA", type="primary", use_container_width=True):
        if topic == "":
            st.error("⚠️ Vui lòng nhập Tên đề tài trước khi thực hiện!")
        else:
            st.success(f"Đã tiếp nhận đề tài: '{topic}'")
            st.info("Hệ thống đang kết nối Trí tuệ nhân tạo (Gemini AI)...")

st.markdown("</div>", unsafe_allow_html=True)

# 6. FOOTER (Thông tin liên hệ)
st.markdown("""
<div class="footer-section">
    <div class="footer-col">
        <div class="footer-title">GIỜ PHỤC VỤ</div>
        <div class="footer-text"><strong>Thứ 2 - Thứ 6:</strong> 07:30 - 20:00</div>
        <div class="footer-text"><strong>Thứ 7 & Chủ Nhật:</strong> 07:30 - 17:00</div>
    </div>
    <div class="footer-col">
        <div class="footer-title">THÔNG TIN LIÊN HỆ</div>
        <div class="footer-text">📞 Điện thoại: (028) 3940 0989</div>
        <div class="footer-text">✉️ Email: thuvien@hcmulaw.edu.vn</div>
        <div class="footer-text">📍 Trụ sở: Số 02 Nguyễn Tất Thành, Q.4, TP.HCM</div>
    </div>
    <div class="footer-col">
        <div class="footer-title">KẾT NỐI</div>
        <div class="footer-text">🌐 Website: lib.hcmulaw.edu.vn</div>
        <div class="footer-text">🔵 Facebook: Thư viện ĐH Luật TP.HCM</div>
    </div>
</div>
""", unsafe_allow_html=True)
