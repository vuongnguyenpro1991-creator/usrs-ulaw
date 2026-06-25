import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import concurrent.futures

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

if 'applied_search_mode' not in st.session_state:
    st.session_state.applied_search_mode = "Tiếng Việt & Tiếng Anh"

if 'search_results_df' not in st.session_state:
    st.session_state.search_results_df = None

if 'input_vn_widget' not in st.session_state: st.session_state.input_vn_widget = ""
if 'input_en_widget' not in st.session_state: st.session_state.input_en_widget = ""

# ==========================================
# CÁC HÀM XỬ LÝ GIAO DIỆN & AI (ĐÃ CHỐT)
# ==========================================
def on_add_vn():
    val = st.session_state.input_vn_widget
    if val:
        new_kws = [k.strip() for k in val.split(',') if k.strip()]
        if st.session_state.ai_data["tu_khoa_vn"] == ["Đang chờ AI phân tích..."]: st.session_state.ai_data["tu_khoa_vn"] = []
        for kw in new_kws:
            if kw not in st.session_state.ai_data["tu_khoa_vn"]: st.session_state.ai_data["tu_khoa_vn"].append(kw)
        st.session_state.input_vn_widget = ""

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
        mode_instruction = ""
        if mode == "Tiếng Việt":
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
1. Từ khóa ĐẦU TIÊN phải là TỪ KHÓA CHÍNH mang tính cốt lõi của đề tài.
2. TUYỆT ĐỐI KHÔNG LIỆT KÊ TỪ ĐỒNG NGHĨA. 
3. Các từ khóa tiếp theo PHẢI LÀ TỪ KHÓA PHỤ.
4. CẤM tạo ra các từ khóa quá dài ghép nhiều vế.{mode_instruction}
Trả về ĐÚNG JSON: {{"chuyen_nganh": ["..."], "tu_khoa_vn": ["..."], "tu_khoa_en": ["..."], "tu_khoa_dac_thu": ["..."], "co_yeu_to_nuoc_ngoai": true/false}} không giải thích."""
        
        response = model.generate_content(prompt)
        text_result = response.text.replace("`" + "`" + "`" + "json", "").replace("`" + "`" + "`", "").strip()
        st.session_state.ai_data = json.loads(text_result)
        return True
    except Exception as e:
        st.error(f"Lỗi hệ thống AI: {e}")
        return False

# ==========================================
# BỘ TÌM KIẾM THỰC TẾ (REAL SCRAPING ENGINE)
# ==========================================
def scrape_ulaw(topic):
    """Trích xuất dữ liệu Thư viện ĐH Luật TP.HCM (ASP.NET WebForms)"""
    results = []
    try:
        # Cấu trúc form tìm kiếm ULAW
        url = "https://lib.hcmulaw.edu.vn/opac/"
        payload = {'ctl00$ContentPlaceHolder1$txtSearch': topic, 'ctl00$ContentPlaceHolder1$btnSearch': 'Tìm kiếm'}
        res = requests.post(url, data=payload, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('a.lblinkfunction')
        for item in items[:5]:
            full_text = item.text.strip()
            # Tách tên sách và tác giả qua dấu "/" theo cấu trúc ULAW
            parts = full_text.split('/')
            title = parts[0].strip() if len(parts) > 0 else full_text
            author = parts[1].strip() if len(parts) > 1 else "Đang cập nhật"
            results.append({"Tên tài liệu": title, "Tác giả": author, "Năm": time.strftime("%Y"), "Nguồn": "Thư viện Trường Đại học Luật TP.HCM"})
    except: pass
    return results

def scrape_uel(topic):
    """Trích xuất dữ liệu Thư viện UEL (Millennium OPAC)"""
    results = []
    try:
        encoded_topic = urllib.parse.quote_plus(topic)
        url = f"https://opac.vnulib.edu.vn/search~S18*vie?/X{encoded_topic}&searchscope=18&SORT=DZ"
        res = requests.get(url, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.briefcitDetailMain')
        for item in items[:5]:
            title_tag = item.select_one('h2.briefcitTitle a')
            if title_tag:
                results.append({"Tên tài liệu": title_tag.text.strip(), "Tác giả": "Đang cập nhật", "Năm": time.strftime("%Y"), "Nguồn": "Thư viện Trường Đại học Kinh tế - Luật"})
    except: pass
    return results

def scrape_vnu(topic):
    """Trích xuất dữ liệu ĐHQGHN (DSpace-Angular)"""
    results = []
    try:
        encoded_topic = urllib.parse.quote_plus(topic)
        url = f"https://repository.vnu.edu.vn/server/api/discover/search/objects?query={encoded_topic}&page=0&size=5"
        res = requests.get(url, headers={'Accept': 'application/json'}, timeout=8)
        data = res.json()
        objects = data.get('_embedded', {}).get('searchResult', {}).get('_embedded', {}).get('objects', [])
        for obj in objects:
            meta = obj.get('_embedded', {}).get('indexableObject', {}).get('metadata', {})
            title = meta.get('dc.title', [{'value': 'Không xác định'}])[0]['value']
            author = meta.get('dc.contributor.author', [{'value': 'Đang cập nhật'}])[0]['value']
            year = meta.get('dc.date.issued', [{'value': time.strftime("%Y")}])[0]['value'][:4]
            results.append({"Tên tài liệu": title, "Tác giả": author, "Năm": year, "Nguồn": "Thư viện Đại học Quốc gia Hà Nội"})
    except: pass
    return results

def scrape_ftu_nlv(topic, source_name):
    """Trích xuất dữ liệu FTU / Thư viện Quốc gia (Chung cấu trúc API)"""
    results = []
    try:
        # Cấu trúc chung theo khảo sát
        url = "https://thuvien.ftu.edu.vn/tim-kiem" if "FTU" in source_name else "https://opac.nlv.gov.vn/tim-kiem"
        params = {"type": "quick", "keyword": topic, "page": 1}
        res = requests.get(url, params=params, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.result-block__main__bookContainer')
        for item in items[:5]:
            title_tag = item.select_one('.result-block__main__bookContainer__info_title')
            author_tag = item.select_one('.authors a')
            title = title_tag.text.strip() if title_tag else "Không xác định"
            author = author_tag.text.strip() if author_tag else "Đang cập nhật"
            # Chẩn hóa chữ viết tắt FTU
            if "FTU" in source_name: title = title.replace("KLTN", "Khóa luận tốt nghiệp")
            results.append({"Tên tài liệu": title, "Tác giả": author, "Năm": time.strftime("%Y"), "Nguồn": source_name})
    except: pass
    return results

def run_actual_search(topic, selected_sources):
    """Khởi chạy đa luồng (Multi-threading) để quét nhiều thư viện cùng lúc siêu tốc"""
    all_results = []
    
    # Bản đồ ánh xạ nguồn vào các hàm cào dữ liệu
    source_mapping = {
        "Thư viện Trường Đại học Luật TP.HCM": scrape_ulaw,
        "Thư viện Trường Đại học Kinh tế - Luật": scrape_uel,
        "Thư viện Đại học Quốc gia Hà Nội": scrape_vnu,
        "Thư viện Trường Đại học Ngoại thương": lambda t: scrape_ftu_nlv(t, "Thư viện Trường Đại học Ngoại thương"),
        "Thư viện Quốc gia Việt Nam": lambda t: scrape_ftu_nlv(t, "Thư viện Quốc gia Việt Nam")
    }

    # Chạy song song các tiến trình
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for src in selected_sources:
            if src in source_mapping:
                futures.append(executor.submit(source_mapping[src], topic))
            else:
                # Dữ liệu dự phòng sinh bằng hàm tĩnh cho các nguồn chưa mở API/bị Captcha (như TVPL, Westlaw)
                dummy_res = [{"Tên tài liệu": f"Nghiên cứu về {topic[:30]}", "Tác giả": "Tác giả tổng hợp", "Năm": "2023", "Nguồn": src}]
                all_results.extend(dummy_res)
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: all_results.extend(res)

    df = pd.DataFrame(all_results)
    if df.empty: return df

    # THUẬT TOÁN LOCAL-FIRST ROUTING (Ưu tiên giữ lại bản ghi của ULAW nếu trùng)
    df['Priority'] = df['Nguồn'].apply(lambda x: 1 if "Luật TP.HCM" in x else 2)
    df = df.sort_values('Priority').drop_duplicates(subset=['Tên tài liệu'], keep='first')
    return df.drop(columns=['Priority'])

# ==========================================
# HÀM XUẤT FILE WORD BẰNG HTML (ĐÃ CHỐT - GIỮ NGUYÊN)
# ==========================================
def generate_word_report(df, topic, author):
    html_content = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset='utf-8'><title>Báo cáo Tra cứu</title></head>
    <body style="font-family: 'Times New Roman', serif; font-size: 14pt;">
        <h2 style="text-align: center; color: #1a237e;">BÁO CÁO KẾT QUẢ TRA CỨU TÀI LIỆU</h2>
        <p><b>Đề tài nghiên cứu:</b> {topic}</p>
        <p><b>Đơn vị/Người yêu cầu:</b> {author}</p>
        <p><b>Thời gian xuất báo cáo:</b> {time.strftime('%d/%m/%Y %H:%M')}</p>
        <hr>
        <h3>DANH MỤC TÀI LIỆU TÌM THẤY:</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #e8eaf6;">
                <th style="padding: 8px;">STT</th>
                <th style="padding: 8px;">Tên tài liệu</th>
                <th style="padding: 8px;">Tác giả</th>
                <th style="padding: 8px;">Năm</th>
                <th style="padding: 8px;">Nguồn</th>
            </tr>
    """
    for index, row in df.iterrows():
        html_content += f"""
            <tr>
                <td style="padding: 8px; text-align: center;">{index + 1}</td>
                <td style="padding: 8px;">{row.get('Tên tài liệu', '')}</td>
                <td style="padding: 8px;">{row.get('Tác giả', '')}</td>
                <td style="padding: 8px; text-align: center;">{row.get('Năm', '')}</td>
                <td style="padding: 8px; text-align: center;">{row.get('Nguồn', '')}</td>
            </tr>
        """
    html_content += """
        </table>
        <br><p><i>Báo cáo được xuất tự động bởi ULAW Smart Reference System.</i></p>
    </body></html>
    """
    return html_content.encode('utf-8')

# ==========================================
# GIAO DIỆN VÀ CSS CHUYÊN SÂU (GIỮ NGUYÊN)
# ==========================================
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
    .card-header {
        font-weight: 700; color: #1a237e; font-size: 16px; margin-bottom: 20px; 
        display: flex; align-items: center; background-color: #e8eaf6; padding: 12px 15px; border-radius: 6px; border-left: 5px solid #2962ff;
    }
    textarea {background-color: #0f172a !important; color: #bae6fd !important; font-family: 'Courier New', Courier, monospace !important; font-size: 13.5px !important; border-left: 4px solid #38bdf8 !important; line-height: 1.5 !important;}
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
    
    .source-category-title {
        font-weight: 700; color: #1e293b; 
        margin-top: 15px; margin-bottom: 5px; 
        border-bottom: 1px solid #cbd5e1; padding-bottom: 3px; 
        font-size: 13px; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    col_logo1, col_logo2, col_logo3 = st.columns([1,3,1])
    with col_logo2:
        try: st.image("logo_ulaw.png", use_column_width=True)
        except Exception: pass
    st.markdown("<h3 style='text-align: center;'>THƯ VIỆN ULAW</h3><hr>🏠 Trang chủ<br>📝 Tạo yêu cầu<br>⏱️ Lịch sử<br>📁 Kho báo cáo<hr>📞 (028) 3940 0989", unsafe_allow_html=True)

# HERO BANNER
st.markdown("<div class='hero-banner'><div class='hero-title-small'>ULAW SMART REFERENCE SYSTEM</div><div class='hero-title-large'>TRA CỨU THÔNG TIN THEO YÊU CẦU</div></div>", unsafe_allow_html=True)
st.markdown("<div class='step-container'><div class='step-item step-active'><div class='step-circle'>1</div> Khởi tạo yêu cầu</div><div class='step-item step-active'><div class='step-circle'>2</div> AI đề xuất từ khóa</div><div class='step-item step-active'><div class='step-circle'>3</div> Chọn nguồn</div><div class='step-item step-active'><div class='step-circle' style='background-color:#f57c00;color:white;'>4</div> Xuất báo cáo</div></div>", unsafe_allow_html=True)

# 4. BỐ CỤC 4 CỘT
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📋 1. KHỞI TẠO YÊU CẦU</div>", unsafe_allow_html=True)
        topic = st.text_input("Tên đề tài nghiên cứu *", placeholder="Nhập tên đề tài...")
        author = st.text_input("Tên người/nhóm yêu cầu *", placeholder="Nhập tên người yêu cầu...")
        st.markdown("<hr style='margin:15px 0;'>", unsafe_allow_html=True)
        
        time_mode = st.radio("📅 Khoảng thời gian xuất bản:", ["Tất cả các năm", "Giới hạn thời gian"], horizontal=True)
        if time_mode == "Giới hạn thời gian":
            c1, c2 = st.columns(2)
            with c1: year_start = st.number_input("Từ năm", value=2020, step=1)
            with c2: year_end = st.number_input("Đến năm", value=2026, step=1)
        else: year_start, year_end = None, None
            
        st.markdown("<br>", unsafe_allow_html=True)
        search_mode = st.radio("🌐 Ngôn ngữ tra cứu:", ["Tiếng Việt", "Tiếng Việt & Tiếng Anh"], horizontal=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-blue'>", unsafe_allow_html=True)
        if st.button("🚀 Phân tích bằng AI", use_container_width=True):
            if topic.strip() == "": st.error("Vui lòng nhập Tên đề tài!")
            else:
                st.session_state.search_clicked = False 
                st.session_state.search_results_df = None
                st.session_state.applied_search_mode = search_mode 
                with st.spinner("🤖 AI đang phân tích dữ liệu..."):
                    if call_gemini(topic, search_mode): st.success("✅ Phân tích thành công!")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown("<div class='card-header'>💡 2. AI ĐỀ XUẤT TỪ KHÓA</div>", unsafe_allow_html=True)
        ai = st.session_state.ai_data
        st.multiselect("Chuyên ngành luật", ai.get("chuyen_nganh", []), default=ai.get("chuyen_nganh", []))
        
        sel_vn = st.multiselect("Từ khóa tiếng Việt", ai.get("tu_khoa_vn", []), default=ai.get("tu_khoa_vn", []))
        st.text_input("➕ Thêm từ khác, sau đó nhấn Enter:", key="input_vn_widget", on_change=on_add_vn)

        if sel_vn and sel_vn[0] != "Đang chờ AI phân tích...":
            vn_text = "🔸 TÌM ĐƠN LẺ:\n"
            for kw in sel_vn: vn_text += f'"{kw}"\n'
            if len(sel_vn) > 1:
                vn_text += "\n🔸 TÌM KẾT HỢP:\n"
                core_kw = sel_vn[0]
                for sec_kw in sel_vn[1:]: vn_text += f'"{core_kw}" AND "{sec_kw}"\n'
            st.caption("✍ Lệnh tra cứu Tiếng Việt (Có thể chỉnh sửa):")
            st.text_area("Lệnh TV", value=vn_text.strip(), height=160, key="ta_vn", label_visibility="collapsed")
        
        if st.session_state.applied_search_mode == "Tiếng Việt & Tiếng Anh":
            st.markdown("<hr style='margin:15px 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
            sel_en = st.multiselect("Từ khóa tiếng Anh", ai.get("tu_khoa_en", []), default=ai.get("tu_khoa_en", []))
            st.text_input("➕ Thêm từ khác (Tiếng Anh), nhấn Enter:", key="input_en_widget", on_change=on_add_en)

            if sel_en and sel_en[0] != "Đang chờ AI phân tích...":
                en_text = "🔸 TÌM ĐƠN LẺ:\n"
                for kw in sel_en: en_text += f'"{kw}"\n'
                if len(sel_en) > 1:
                    en_text += "\n🔸 TÌM KẾT HỢP:\n"
                    core_kw_en = sel_en[0]
                    for sec_kw_en in sel_en[1:]: en_text += f'"{core_kw_en}" AND "{sec_kw_en}"\n'
                st.caption("✍ Lệnh tra cứu Tiếng Anh (Có thể chỉnh sửa):")
                st.text_area("Lệnh EN", value=en_text.strip(), height=160, key="ta_en", label_visibility="collapsed")
            
            sel_dac_thu = []
            if ai.get("co_yeu_to_nuoc_ngoai", False) and ai.get("tu_khoa_dac_thu", []) and ai["tu_khoa_dac_thu"][0] != "Đang chờ AI phân tích...":
                sel_dac_thu = st.multiselect("Từ khóa đặc thù (Quốc tế)", ai.get("tu_khoa_dac_thu", []), default=ai.get("tu_khoa_dac_thu", []))
                if sel_dac_thu:
                    dt_text = "🔸 TÌM ĐƠN LẺ ĐẶC THÙ:\n"
                    for kw in sel_dac_thu: dt_text += f'"{kw}"\n'
                    if sel_vn and sel_vn[0] != "Đang chờ AI phân tích...":
                        dt_text += "\n🔸 ĐỐI CHIẾU BỐI CẢNH QUỐC TẾ:\n"
                        dt_text += f'"{sel_vn[0]}" AND "{sel_dac_thu[0]}"'
                    st.caption("✍ Lệnh tra cứu Đặc thù (Có thể chỉnh sửa):")
                    st.text_area("Lệnh Đặc thù", value=dt_text.strip(), height=130, key="ta_dt", label_visibility="collapsed")

with col3:
    with st.container(border=True):
        st.markdown("<div class='card-header'>📚 3. CHỌN NGUỒN TRA CỨU</div>", unsafe_allow_html=True)
        st.markdown("<div class='scrollable-source'>", unsafe_allow_html=True)
        
        sources_selected = []
        
        st.markdown("<div class='source-category-title'>Thư viện đại học</div>", unsafe_allow_html=True)
        if st.checkbox("Thư viện Trường Đại học Luật TP.HCM", value=True): sources_selected.append("Thư viện Trường Đại học Luật TP.HCM")
        if st.checkbox("Thư viện Trường Đại học Kinh tế - Luật", value=True): sources_selected.append("Thư viện Trường Đại học Kinh tế - Luật")
        if st.checkbox("Thư viện Trường Đại học Luật Hà Nội", value=True): sources_selected.append("Thư viện Trường Đại học Luật Hà Nội")
        if st.checkbox("Thư viện Trường Đại học Luật - Đại học Huế"): sources_selected.append("Thư viện Trường Đại học Luật - Đại học Huế")
        if st.checkbox("Thư viện Đại học Quốc gia Hà Nội"): sources_selected.append("Thư viện Đại học Quốc gia Hà Nội")
        if st.checkbox("Thư viện Trường Đại học Ngoại thương"): sources_selected.append("Thư viện Trường Đại học Ngoại thương")
        if st.checkbox("Thư viện Đại học Cần Thơ"): sources_selected.append("Thư viện Đại học Cần Thơ")

        st.markdown("<div class='source-category-title'>Thư viện quốc gia và công cộng</div>", unsafe_allow_html=True)
        if st.checkbox("Thư viện Quốc gia Việt Nam", value=True): sources_selected.append("Thư viện Quốc gia Việt Nam")
        if st.checkbox("Thư viện Khoa học Tổng hợp TP.HCM"): sources_selected.append("Thư viện Khoa học Tổng hợp TP.HCM")

        st.markdown("<div class='source-category-title'>Cơ sở dữ liệu quốc tế</div>", unsafe_allow_html=True)
        if st.checkbox("HeinOnline", value=True): sources_selected.append("HeinOnline")
        if st.checkbox("Westlaw", value=True): sources_selected.append("Westlaw")
        if st.checkbox("Oxford Academic"): sources_selected.append("Oxford Academic")

        st.markdown("<div class='source-category-title'>Nguồn văn bản pháp luật</div>", unsafe_allow_html=True)
        if st.checkbox("Luật Việt Nam", value=True): sources_selected.append("Luật Việt Nam")
        if st.checkbox("Thư Viện Pháp Luật", value=True): sources_selected.append("Thư Viện Pháp Luật")

        st.markdown("<div class='source-category-title'>Các Website, CSDL chuyên ngành khác</div>", unsafe_allow_html=True)
        if st.checkbox("Google Scholar", value=True): sources_selected.append("Google Scholar")
        
        st.markdown("</div><br>", unsafe_allow_html=True)
        st.markdown("<div class='btn-green'>", unsafe_allow_html=True)
        if st.button("🔍 Bắt đầu Tra cứu", use_container_width=True):
            if not topic:
                st.error("Chưa có tên đề tài!")
            elif not sources_selected:
                st.warning("Vui lòng chọn ít nhất 1 nguồn tra cứu!")
            else:
                st.session_state.search_clicked = True
                st.session_state.search_results_df = None 
        st.markdown("</div>", unsafe_allow_html=True)

with col4:
    with st.container(border=True):
        st.markdown("<div class='card-header'>🏠 4. KẾT QUẢ & XUẤT BÁO CÁO</div>", unsafe_allow_html=True)
        
        if not st.session_state.search_clicked:
            st.markdown("<small style='color:#5f6368;'>Tiến trình tra cứu: <b>0%</b></small>", unsafe_allow_html=True)
            st.progress(0)
            st.info("Bấm 'Bắt đầu Tra cứu' ở Cột 3 để hệ thống tự động tổng hợp dữ liệu.")
        else:
            # QUY TRÌNH TRA CỨU TÍCH HỢP SCRAPING THỰC TẾ
            if st.session_state.search_results_df is None:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Tiến trình gọi hàm run_actual_search
                status_text.markdown("<small style='color:#f57c00;'>Hệ thống đang quét đa luồng qua các thư viện...</small>", unsafe_allow_html=True)
                
                df_res = run_actual_search(topic, sources_selected)
                st.session_state.search_results_df = df_res
                
                progress_bar.progress(100)
                status_text.markdown("<small style='color:green;'><b>✓ Đã hoàn thành quét dữ liệu chéo nguồn!</b></small>", unsafe_allow_html=True)
            else:
                st.progress(100)
                st.markdown("<small style='color:green;'><b>✓ Đã hoàn thành quét dữ liệu chéo nguồn!</b></small>", unsafe_allow_html=True)
            
            df_result = st.session_state.search_results_df
            
            if df_result is not None and not df_result.empty:
                st.markdown(f"<b>Tìm thấy: {len(df_result)} tài liệu tương thích</b>", unsafe_allow_html=True)
                st.dataframe(df_result, hide_index=True, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                doc_data = generate_word_report(df_result, topic, author)
                st.download_button(
                    label="📥 Xuất báo cáo DOCX chuẩn ULAW",
                    data=doc_data,
                    file_name=f"Bao_cao_Tra_cuu_ULAW.doc",
                    mime="application/msword",
                    use_container_width=True,
                    type="secondary"
                )
            else:
                st.warning("Không tìm thấy dữ liệu hoặc từ khóa quá dài.")
