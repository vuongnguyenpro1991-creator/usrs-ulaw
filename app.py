import streamlit as st
import pandas as pd
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import datetime
import json
import time

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN (UI/UX)
# ==========================================
st.set_page_config(page_title="USRS - ULAW Smart Reference", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stApp {background-color: #f4f6f9;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {background-color: #1a237e; color: white;}
    [data-testid="stSidebar"] * {color: white !important;}
    .hero-banner {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        padding: 30px; border-radius: 10px; color: white; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .hero-title-small {color: #90caf9; font-weight: 700; font-size: 16px; letter-spacing: 1.5px; text-transform: uppercase;}
    .hero-title-large {color: #ffffff; font-weight: 800; font-size: 32px; margin: 10px 0;}
    .card-header {
        font-weight: 700; color: #1a237e; font-size: 16px; margin-bottom: 15px; 
        background-color: #e8eaf6; padding: 10px 15px; border-radius: 6px; border-left: 5px solid #2962ff;
    }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .source-category-title {font-weight: 700; color: #1e293b; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #cbd5e1; padding-bottom: 3px; font-size: 13px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

# Khởi tạo Session State
if 'ai_data' not in st.session_state:
    st.session_state.ai_data = {"chuyen_nganh": [], "tu_khoa_vn": [], "tu_khoa_en": [], "tu_khoa_dac_thu": []}
if 'search_results_df' not in st.session_state:
    st.session_state.search_results_df = None
if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

# ==========================================
# 2. THUẬT TOÁN LÕI (CORE ALGORITHMS)
# ==========================================

def call_gemini(topic, mode):
    """Phân tích đề tài bằng AI Gemini để sinh từ khóa chuẩn xác"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3.5-flash') 
        mode_instruction = 'Không dịch sang tiếng Anh.' if mode == "Tiếng Việt" else 'Dịch từ khóa sang tiếng Anh vào mảng "tu_khoa_en".'
        
        prompt = f"""Phân tích đề tài luật học: "{topic}". {mode_instruction}
        Trả về JSON: {{"chuyen_nganh": ["..."], "tu_khoa_vn": ["..."], "tu_khoa_en": ["..."], "tu_khoa_dac_thu": ["..."]}}. Chỉ xuất JSON."""
        
        response = model.generate_content(prompt)
        text_result = response.text.replace("```json", "").replace("```", "").strip()
        st.session_state.ai_data = json.loads(text_result)
        return True
    except Exception as e:
        st.error(f"Lỗi hệ thống AI: Lấy API Key từ secrets.toml thất bại hoặc quá tải.")
        return False

def run_search_engine(topic, sources):
    """
    THUẬT TOÁN TÌM KIẾM & LỌC TRÙNG (LOCAL-FIRST ROUTING)
    Mô phỏng cơ chế cào dữ liệu chéo nguồn và ưu tiên nguồn nội bộ (ULAW)
    """
    # 1. Dữ liệu thô thu thập từ nhiều nguồn (Mô phỏng Scraping)
    raw_data = [
        {"Tên tài liệu": f"Pháp luật về {topic[:20]}", "Tác giả": "Nguyễn Văn A", "Năm": 2023, "Nguồn": "Thư viện ĐH Luật TP.HCM", "Loại hình": "Luận văn", "Nơi xuất bản": "TP.HCM", "Nhà xuất bản": "", "Người hướng dẫn": "PGS.TS Lê B", "Số trang": "85", "Tạp chí": "", "Số kỳ": "", "Link": ""},
        {"Tên tài liệu": f"Pháp luật về {topic[:20]}", "Tác giả": "Nguyễn Văn A", "Năm": 2023, "Nguồn": "Thư viện ĐH Luật HN", "Loại hình": "Luận văn", "Nơi xuất bản": "TP.HCM", "Nhà xuất bản": "", "Người hướng dẫn": "Lê B", "Số trang": "85", "Tạp chí": "", "Số kỳ": "", "Link": ""}, # Trùng lặp
        {"Tên tài liệu": f"Thực trạng {topic[:15]}", "Tác giả": "Trần Thị C", "Năm": 2024, "Nguồn": "Thư viện UEL", "Loại hình": "Bài báo", "Nơi xuất bản": "", "Nhà xuất bản": "", "Người hướng dẫn": "", "Số trang": "12-18", "Tạp chí": "Tạp chí Khoa học Pháp lý", "Số kỳ": "02", "Link": ""},
        {"Tên tài liệu": "Comparative Analysis of Debt Collection", "Tác giả": "John Doe", "Năm": 2022, "Nguồn": "HeinOnline", "Loại hình": "Bài báo", "Nơi xuất bản": "", "Nhà xuất bản": "", "Người hướng dẫn": "", "Số trang": "45-60", "Tạp chí": "Harvard Law Review", "Số kỳ": "1", "Link": "https://heinonline.org/..."},
        {"Tên tài liệu": f"Nghị định quy định về {topic[:10]}", "Tác giả": "Chính phủ", "Năm": 2020, "Nguồn": "Thư Viện Pháp Luật", "Loại hình": "Văn bản pháp quy", "Nơi xuất bản": "", "Nhà xuất bản": "", "Người hướng dẫn": "", "Số trang": "", "Tạp chí": "", "Số kỳ": "", "Link": "https://thuvienphapluat.vn/..."},
        {"Tên tài liệu": f"Giáo trình {topic[:15]}", "Tác giả": "Trường ĐH Luật TP.HCM", "Năm": 2021, "Nguồn": "Thư viện ĐH Luật TP.HCM", "Loại hình": "Sách", "Nơi xuất bản": "TP.HCM", "Nhà xuất bản": "NXB Hồng Đức", "Người hướng dẫn": "", "Số trang": "300", "Tạp chí": "", "Số kỳ": "", "Link": ""}
    ]
    df = pd.DataFrame(raw_data)
    
    # Chỉ giữ lại tài liệu thuộc các nguồn user đã chọn
    if sources:
        df = df[df['Nguồn'].isin(sources)]
    
    if df.empty:
        return df

    # 2. THUẬT TOÁN LOCAL-FIRST ROUTING (Ưu tiên ULAW)
    # Gắn trọng số ưu tiên: ULAW = 1, Các trường khác = 2, Quốc tế = 3, Web = 4
    def get_priority(src):
        if "ULAW" in src or "Luật TP.HCM" in src: return 1
        if "ĐH" in src or "UEL" in src: return 2
        if "HeinOnline" in src or "Westlaw" in src: return 3
        return 4

    df['Priority'] = df['Nguồn'].apply(get_priority)
    df = df.sort_values('Priority')
    
    # Lọc trùng lặp dựa trên Tên tài liệu và Năm, giữ lại bản ghi có Priority cao nhất
    df = df.drop_duplicates(subset=['Tên tài liệu', 'Năm'], keep='first')
    
    # 3. THÊM CỘT KIỂM DUYỆT (Human-in-the-loop)
    df.insert(0, 'Chọn', True)
    return df.drop(columns=['Priority'])

# ==========================================
# 3. REPORT ENGINE (XUẤT WORD CHUẨN ULAW BẰNG PYTHON-DOCX)
# ==========================================

def format_citation(row):
    """Định dạng chuỗi tĩnh (Hard-coded Formatting) cho từng loại tài liệu"""
    t = row['Loại hình']
    title = str(row['Tên tài liệu']).strip()
    author = str(row['Tác giả']).strip()
    year = str(row['Năm']).strip()
    
    def get_val(col):
        val = row.get(col, "")
        return str(val).strip() if pd.notna(val) else ""

    pages = f", {get_val('Số trang')} tr." if get_val('Số trang') else ""
    guide = f"; Người hướng dẫn: {get_val('Người hướng dẫn')}" if get_val('Người hướng dẫn') else ""
    place = f", {get_val('Nơi xuất bản')}" if get_val('Nơi xuất bản') else ""
    publisher = f", {get_val('Nhà xuất bản')}" if get_val('Nhà xuất bản') else ""
    journal = f", {get_val('Tạp chí')}" if get_val('Tạp chí') else ""
    issue = f", Số {get_val('Số kỳ')}" if get_val('Số kỳ') else ""
    link = f" {get_val('Link')} (Truy cập ngày {datetime.datetime.now().strftime('%d/%m/%Y')})" if get_val('Link') else ""

    if t in ["Luận án", "Luận văn", "Khóa luận tốt nghiệp", "Khóa luận"]:
        return f"{title} : {t}, {author}{guide}{place}, {year}{pages}"
    elif t in ["Bài báo", "Tạp chí"]:
        return f"{title}, {author}{journal}{publisher}, {year}{issue}{pages}"
    elif t == "Sách":
        return f"{title}, {author}{place}{publisher}, {year}{pages}"
    elif t == "Văn bản pháp quy":
        return f"{title}, Cơ quan ban hành: {author}, Năm ban hành: {year}{link}"
    elif t in ["Website chuyên ngành", "Website / CSDL Chuyên ngành"]:
        return f"{title}{link}"
    else:
        return f"{title}, {author}, {year}{pages}"

def generate_docx_report(df, topic, author_name, tk_vn, tk_en):
    doc = Document()
    
    # Header: Bảng 2 cột chuẩn hành chính
    table = doc.add_table(rows=1, cols=2)
    table.autofit = True
    
    p_left = table.cell(0, 0).paragraphs[0]
    p_left.add_run("TRƯỜNG ĐẠI HỌC LUẬT TP.HCM\nTHƯ VIỆN\n-------").bold = True
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_right = table.cell(0, 1).paragraphs[0]
    p_right.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n--------------------").bold = True
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("KẾT QUẢ TRA CỨU THÔNG TIN")
    title_run.bold = True
    title_run.font.size = Pt(16)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Metadata
    doc.add_paragraph(f"Đề tài: “{topic}”")
    doc.add_paragraph(f"Từ khóa tiếng Việt: “{', '.join(tk_vn)}”")
    doc.add_paragraph(f"Từ khóa tiếng Anh: “{', '.join(tk_en)}”")
    doc.add_paragraph(f"Kính gửi tác giả hoặc nhóm tác giả: {author_name}")
    doc.add_paragraph("Sau khi tiến hành các quy trình tra cứu khảo sát thông tin đề tài nghiên cứu, Thư viện Trường ĐH Luật TP. Hồ Chí Minh kính gửi đến anh, chị danh mục tài liệu có liên quan đến đề tài sau đây:")
    
    # THUẬT TOÁN SẮP XẾP 4 LỚP (Strict 4-Layer Sorting)
    df_sorted = df.sort_values(by=['Năm', 'Tên tài liệu'], ascending=[False, True])
    
    # PHẦN A: TÀI LIỆU HỌC THUẬT
    doc.add_heading("PHẦN A: CÁC WEBSITE PHẢI SỬ DỤNG TRONG TRA CỨU ĐỐI VỚI TẤT CẢ ĐỀ TÀI", level=1)
    academic_sources = df_sorted[~df_sorted['Loại hình'].isin(['Văn bản pháp quy', 'Website chuyên ngành', 'Website / CSDL Chuyên ngành'])]['Nguồn'].unique()
    type_order = ["Luận án", "Luận văn", "Khóa luận tốt nghiệp", "Đề tài nghiên cứu khoa học", "Sách", "Bài báo"]
    
    for idx, source in enumerate(academic_sources, 1):
        doc.add_paragraph(f"{idx}. {source}:").runs[0].bold = True
        source_df = df_sorted[df_sorted['Nguồn'] == source]
        
        for t in type_order:
            type_df = source_df[source_df['Loại hình'] == t]
            p = doc.add_paragraph()
            p.add_run(f"    • {t}: ")
            if type_df.empty:
                p.add_run("Không có tài liệu").italic = True
            else:
                for _, row in type_df.iterrows():
                    doc.add_paragraph(format_citation(row), style='List Bullet 2')
                    
    # PHẦN B: VĂN BẢN PHÁP QUY
    doc.add_heading("PHẦN B: VĂN BẢN PHÁP QUY LIÊN QUAN ĐẾN ĐỀ TÀI", level=1)
    vb_df = df_sorted[df_sorted['Loại hình'] == 'Văn bản pháp quy']
    if vb_df.empty:
        doc.add_paragraph("    Không có tài liệu").italic = True
    else:
        for _, row in vb_df.iterrows():
            doc.add_paragraph(format_citation(row), style='List Bullet')

    # PHẦN D: BẢNG THỐNG KÊ (Tự động sinh)
    doc.add_heading("PHẦN D: THỐNG KÊ KẾT QUẢ KHẢO SÁT", level=1)
    stat_table = doc.add_table(rows=1, cols=3)
    stat_table.style = 'Table Grid'
    hdr_cells = stat_table.rows[0].cells
    hdr_cells[0].text = 'STT'
    hdr_cells[1].text = 'Loại hình tài liệu'
    hdr_cells[2].text = 'Số lượng'
    
    total_docs = 0
    all_types = type_order + ['Văn bản pháp quy', 'Website chuyên ngành']
    for i, t in enumerate(all_types, 1):
        count = len(df_sorted[df_sorted['Loại hình'] == t])
        total_docs += count
        row_cells = stat_table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = t
        row_cells[2].text = f"{count:02d}"
        
    row_total = stat_table.add_row().cells
    row_total[0].text = ""
    row_total[1].text = "TỔNG"
    row_total[1].paragraphs[0].runs[0].bold = True
    row_total[2].text = f"{total_docs:02d}"
    
    # Footer Chữ ký
    doc.add_paragraph("\n")
    footer_p = doc.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer_p.add_run(f"TP. Hồ Chí Minh, ngày {datetime.datetime.now().day:02d} tháng {datetime.datetime.now().month:02d} năm {datetime.datetime.now().year}\n").italic = True
    footer_p.add_run("GIÁM ĐỐC THƯ VIỆN\n\n\n\n").bold = True
    footer_p.add_run("Ngô Kim Hoàng Nguyên").bold = True

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ==========================================
# 4. TRẢI NGHIỆM NGƯỜI DÙNG (WIZARD FLOW UI)
# ==========================================

with st.sidebar:
    st.markdown("<h3 style='text-align: center;'>THƯ VIỆN ULAW</h3><hr>🏠 Trang chủ<br>📝 Tạo yêu cầu<br>⏱️ Lịch sử<br>📁 Kho báo cáo<hr>📞 (028) 3940 0989", unsafe_allow_html=True)

st.markdown("<div class='hero-banner'><div class='hero-title-small'>ULAW SMART REFERENCE SYSTEM</div><div class='hero-title-large'>TRA CỨU THÔNG TIN THEO YÊU CẦU</div></div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# BƯỚC 1: KHỞI TẠO YÊU CẦU
with col1:
    with st.container():
        st.markdown("<div class='card-header'>📋 1. KHỞI TẠO YÊU CẦU</div>", unsafe_allow_html=True)
        topic = st.text_input("Tên đề tài nghiên cứu *", placeholder="Nhập tên đề tài...")
        author = st.text_input("Tên người/nhóm yêu cầu *", placeholder="Nhập tên...")
        time_mode = st.radio("📅 Khoảng thời gian:", ["Tất cả", "Giới hạn"], horizontal=True)
        if time_mode == "Giới hạn":
            c1, c2 = st.columns(2)
            with c1: year_start = st.number_input("Từ năm", value=2020)
            with c2: year_end = st.number_input("Đến năm", value=2026)
            
        search_mode = st.radio("🌐 Ngôn ngữ:", ["Tiếng Việt", "Tiếng Việt & Tiếng Anh"], horizontal=True)
        
        if st.button("🚀 Phân tích bằng AI", use_container_width=True, type="primary"):
            if not topic: st.error("Vui lòng nhập Tên đề tài!")
            else:
                with st.spinner("🤖 AI đang phân tích dữ liệu..."):
                    if call_gemini(topic, search_mode):
                        st.session_state.search_results_df = None
                        st.success("✅ Phân tích thành công!")

# BƯỚC 2: AI ĐỀ XUẤT TỪ KHÓA
with col2:
    with st.container():
        st.markdown("<div class='card-header'>💡 2. KIỂM DUYỆT TỪ KHÓA</div>", unsafe_allow_html=True)
        ai = st.session_state.ai_data
        sel_vn = st.multiselect("Từ khóa tiếng Việt", ai.get("tu_khoa_vn", []), default=ai.get("tu_khoa_vn", []))
        sel_en = st.multiselect("Từ khóa tiếng Anh", ai.get("tu_khoa_en", []), default=ai.get("tu_khoa_en", []))
        
        if sel_vn:
            st.caption("✍ Lệnh truy vấn mô phỏng (Layered Search):")
            query = f'"{sel_vn[0]}"' + (f' AND "{sel_en[0]}"' if sel_en else '')
            st.code(query, language="sql")

# BƯỚC 3: CHỌN NGUỒN TRA CỨU
with col3:
    with st.container():
        st.markdown("<div class='card-header'>📚 3. CHỌN NGUỒN TRA CỨU</div>", unsafe_allow_html=True)
        sources_selected = []
        
        st.markdown("<div class='source-category-title'>Thư viện đại học & Công cộng</div>", unsafe_allow_html=True)
        if st.checkbox("Thư viện ĐH Luật TP.HCM (Ưu tiên)", value=True): sources_selected.append("Thư viện ĐH Luật TP.HCM")
        if st.checkbox("Thư viện UEL", value=True): sources_selected.append("Thư viện UEL")
        if st.checkbox("Thư viện ĐH Luật HN", value=True): sources_selected.append("Thư viện ĐH Luật HN")
        if st.checkbox("Thư viện Quốc gia Việt Nam", value=True): sources_selected.append("Thư viện Quốc gia")

        st.markdown("<div class='source-category-title'>CSDL Quốc tế & Pháp quy</div>", unsafe_allow_html=True)
        if st.checkbox("HeinOnline", value=True): sources_selected.append("HeinOnline")
        if st.checkbox("Thư Viện Pháp Luật", value=True): sources_selected.append("Thư Viện Pháp Luật")
        
        if st.button("🔍 Bắt đầu Tra cứu", use_container_width=True, type="primary"):
            if not topic: st.error("Chưa có tên đề tài!")
            elif not sources_selected: st.warning("Chọn ít nhất 1 nguồn!")
            else:
                st.session_state.search_clicked = True
                with st.spinner("Đang chạy thuật toán Lọc trùng (Local-first)..."):
                    time.sleep(1.5) # Giả lập tiến trình cào mạng
                    st.session_state.search_results_df = run_search_engine(topic, sources_selected)

# BƯỚC 4: KẾT QUẢ & XUẤT BÁO CÁO
with col4:
    with st.container():
        st.markdown("<div class='card-header'>🏠 4. KẾT QUẢ & XUẤT BẢN</div>", unsafe_allow_html=True)
        
        if st.session_state.search_results_df is not None and not st.session_state.search_results_df.empty:
            st.success("Tài liệu đã được thu thập. Vui lòng kiểm duyệt:")
            
            # Khởi tạo Trình chỉnh sửa dữ liệu (Data Editor) cho Thủ thư
            edited_df = st.data_editor(
                st.session_state.search_results_df,
                column_config={"Chọn": st.column_config.CheckboxColumn("Giữ lại", default=True)},
                disabled=["Tên tài liệu", "Tác giả", "Loại hình", "Nguồn", "Năm"],
                hide_index=True,
                use_container_width=True,
                height=250
            )
            
            # Lọc các dòng Thủ thư đã tick "Chọn"
            final_df = edited_df[edited_df['Chọn'] == True].drop(columns=['Chọn'])
            
            st.markdown("<br>", unsafe_allow_html=True)
            doc_data = generate_docx_report(final_df, topic, author, sel_vn, sel_en)
            
            st.download_button(
                label="📥 XUẤT BÁO CÁO DOCX",
                data=doc_data,
                file_name="Bao_cao_Tra_cuu_USRS.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary"
            )
        elif st.session_state.search_clicked:
            st.warning("Không tìm thấy tài liệu phù hợp.")
        else:
            st.info("Chờ lệnh quét dữ liệu từ Cột 3...")
