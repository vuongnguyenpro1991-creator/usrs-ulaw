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

# Khởi tạo bộ nhớ tạm để tự động xóa trắng ô nhập liệu sau khi Enter
if 'input_vn_widget' not in st.session_state: st.session_state.input_vn_widget = ""
if 'input_en_widget' not in st.session_state: st.session_state.input_en_widget = ""

# Hàm xử lý khi ấn Enter ở ô Tiếng Việt (Thêm từ & Tự động dịch sang Tiếng Anh)
def on_add_vn():
    val = st.session_state.input_vn_widget
    if val:
        new_kws = [k.strip() for k in val.split(',') if k.strip()]
        
        # Gọi AI dịch ngầm các từ mới sang Tiếng Anh
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
                
        # Xóa trắng ô nhập liệu để sẵn sàng cho từ tiếp theo
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

def call_gemini(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3.5-flash') 
        
        # ĐÃ SIẾT CHẶT KỶ LUẬT ĐỂ AI RA TỪ KHÓA ĐÚNG CHỦ ĐỀ CHÍNH XÁC NHẤT
        prompt = f"""Bạn là một Chuyên gia Thư viện học và Luật sư cấp cao tại Đại học Luật TP.HCM. 
Nhiệm vụ của bạn là phân tích đề tài nghiên cứu sau để tạo ra bộ từ khóa tra cứu chuẩn xác: "{topic}".
KỶ LUẬT NGHIỆP VỤ THƯ VIỆN BẮT BUỘC:
1. Chỉ bóc tách từ 2 đến 3 từ khóa là THỰC THỂ PHÁP LÝ TRỌNG TÂM của đề tài. (Ví dụ với đề tài thanh toán điện tử, từ khóa bắt buộc phải có là "thanh toán điện tử", "hoạt động thanh toán điện tử").
2. TUYỆT ĐỐI KHÔNG tách các danh từ chung chung như "khách hàng", "ngân hàng", "nhà nước" đứng độc lập. Phải ghép thành cụm phức hợp có nghĩa (VD: "bảo vệ khách hàng", "thanh toán qua ngân hàng").
3. TUYỆT ĐỐI LOẠI BỎ các từ rườm rà: thực tiễn, đường lối, giải quyết, quy định, pháp luật, bất cập, hoàn thiện, một số vấn đề.
4. Đề tài nghiên cứu trong nước, không có từ khóa quốc tế thì "co_yeu_to_nuoc_ngoai" BẮT BUỘC ghi false và "tu_khoa_dac_thu" là mảng rỗng [].
Trả về ĐÚNG định dạng JSON: {{"chuyen_nganh": ["..."], "tu_khoa_vn": ["..."], "tu_khoa_en": ["..."], "tu_khoa_dac_thu": ["..."], "co_yeu_to_nuoc_ngoai": true/false}} không giải thích thêm."""
        
        response = model.generate_content(prompt)
        text_result = response.text.strip()
        
        if text_result.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### 🎯 HƯỚNG DẪN KIỂM TRA HỆ THỐNG SAU UPDATE:
1. Bạn dán code mới này đè lên `app.py` trên GitHub và bấm Commit.
2. Sang trang Streamlit và thực hiện **Reboot app**.
3. Bạn test thử với đề tài thanh toán điện tử vừa rồi:
   * Hãy nhìn vào hộp đen xem trước: Các chữ *"Tìm đơn lẻ"* và *"Tìm kết hợp cặp đôi (Thu hẹp)"* đã sáng bừng lên màu vàng cực kỳ chuyên nghiệp.
   * Thử gõ cụm từ: `thanh toán điện tử, bảo vệ người tiêu dùng, hoạt động ngân hàng` rồi ấn **Enter**. Bạn sẽ thấy các chuỗi kết hợp chỉ bắt cặp 2 từ với nhau dạng: `"thanh toán điện tử" AND "bảo vệ người tiêu dùng"`.
   * Vì là đề tài thuần túy Việt Nam, ô danh mục "Từ khóa đặc thù (Quốc tế)" đã được hệ thống **ẩn đi hoàn toàn**, giao diện gọn gàng tuyệt đối đúng như ý bạn! 

Bạn chạy thử nghiệm xem phiên bản tinh gọn chuẩn nghiệp vụ này đã khiến bạn hoàn toàn hài lòng chưa nhé!
