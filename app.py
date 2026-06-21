import streamlit as st

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="HỆ THỐNG TRA CỨU THÔNG TIN ULAW", layout="wide")

# 2. TÙY CHỈNH CSS (Đẹp, sang trọng, phông chữ chuyên nghiệp)
st.markdown("""
<style>
    /* Import phông chữ thanh lịch từ Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&family=Playfair+Display:wght@600;700&display=swap');

    /* Phông chữ tổng thể */
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }

    /* Tiêu đề chính (Sang trọng, viết hoa) */
    .main-title {
        color: #003366; 
        text-align: center; 
        font-family: 'Playfair Display', serif; 
        font-weight: 700;
        text-transform: UPPERCASE;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }
    
    /* Tiêu đề phụ */
    .sub-title {
        color: #555555; 
        text-align: center; 
        font-size: 1.1rem;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: UPPERCASE;
        margin-bottom: 40px;
    }

    /* Đầu mục lớn (Viết hoa, thanh lịch) */
    .section-header {
        color: #003366;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 1.15rem;
        text-transform: UPPERCASE;
        border-bottom: 1.5px solid #003366;
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 25px;
        letter-spacing: 0.5px;
    }

    /* Tùy chỉnh Nút bấm (Hiện đại, tối giản) */
    .stButton>button {
        background-color: #003366; 
        color: white; 
        font-weight: 500;
        font-size: 0.95rem;
        border-radius: 3px;
        border: none;
        padding: 8px 24px;
        transition: all 0.3s ease;
        text-transform: UPPERCASE;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #004080; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    
    /* Tùy chỉnh nhãn của các ô nhập liệu */
    .stTextInput>label, .stSlider>label {
        font-weight: 500;
        color: #003366;
    }
</style>
""", unsafe_allow_html=True)

# 3. TIÊU ĐỀ HỆ THỐNG
st.markdown("<h1 class='main-title'>HỆ THỐNG TRA CỨU THÔNG TIN THÔNG MINH</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Trường Đại học Luật TP.HCM (USRS)</div>", unsafe_allow_html=True)

# 4. BƯỚC 1: KHỞI TẠO YÊU CẦU
st.markdown("<div class='section-header'>BƯỚC 1: KHỞI TẠO YÊU CẦU TRA CỨU</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("TÊN ĐỀ TÀI NGHIÊN CỨU:")
    requester = st.text_input("NGƯỜI YÊU CẦU (TÁC GIẢ / NHÓM TÁC GIẢ):")
    
with col2:
    time_filter = st.slider("GIỚI HẠN THỜI GIAN TÀI LIỆU (NĂM):", 2000, 2026, (2018, 2026))

st.write("")
st.write("")

# 5. NÚT KÍCH HOẠT
if st.button("PHÂN TÍCH ĐỀ TÀI"):
    if topic == "":
        st.error("Vui lòng nhập Tên đề tài nghiên cứu trước khi thực hiện phân tích.")
    else:
        st.success(f"Đã tiếp nhận yêu cầu phân tích cho đề tài: {topic}")
        st.info("Hệ thống đang kết nối dữ liệu máy học. Vui lòng chờ trong giây lát...")
