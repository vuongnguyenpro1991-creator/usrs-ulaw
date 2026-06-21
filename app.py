import streamlit as st
import pandas as pd

st.set_page_config(page_title="USRS - ULAW Smart Reference System", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {font-family: Inter, sans-serif;}
.stApp{background:#f4f7ff;}
.hero{
background:linear-gradient(135deg,#1e40af,#6d28d9);
padding:30px;border-radius:24px;color:white;
box-shadow:0 10px 30px rgba(0,0,0,.12);
}
.card{
background:white;border-radius:18px;padding:18px;
box-shadow:0 4px 15px rgba(0,0,0,.06);
height:100%;
}
.metric{
background:white;border-radius:16px;padding:15px;text-align:center;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("📚 USRS")
    st.caption("ULAW Smart Reference System")
    menu = st.radio("Điều hướng",[
        "Tra cứu mới","Lịch sử tra cứu","Kho báo cáo","Hướng dẫn","Cài đặt"
    ])
    st.divider()
    st.markdown("### Liên hệ")
    st.write("📞 (028) 3720 6509")
    st.write("✉️ thuvien@hcmulaw.edu.vn")

col1,col2 = st.columns([8,2])
with col1:
    st.markdown("""
    <h2 style='color:#1e3a8a;margin-bottom:0'>
    THƯ VIỆN TRƯỜNG ĐẠI HỌC LUẬT TP. HỒ CHÍ MINH
    </h2>
    <div style='color:#475569;font-weight:600'>
    HO CHI MINH CITY UNIVERSITY OF LAW LIBRARY
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.button("Đăng ký", use_container_width=True)
    st.button("Đăng nhập", use_container_width=True)

st.markdown("""
<div class="hero">
<h3>ULAW SMART REFERENCE SYSTEM (USRS)</h3>
<h1>TRA CỨU THÔNG TIN THEO YÊU CẦU</h1>
<p>Kết nối nguồn tri thức phục vụ học tập, nghiên cứu và đổi mới sáng tạo.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

steps = st.columns(4)
titles = [
"1. Khởi tạo yêu cầu",
"2. AI đề xuất từ khóa",
"3. Chọn nguồn tra cứu",
"4. Kiểm duyệt & Xuất báo cáo"
]
for c,t in zip(steps,titles):
    c.success(t)

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Khởi tạo yêu cầu")
    st.text_input("Tên đề tài nghiên cứu")
    st.text_input("Người/nhóm yêu cầu")
    a,b = st.columns(2)
    a.number_input("Từ năm", 2000,2100,2020)
    b.number_input("Đến năm", 2000,2100,2026)
    st.button("Tiếp tục", key="b1", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("AI đề xuất từ khóa")
    st.multiselect("Chuyên ngành",
    ["Luật Dân sự","Luật Hình sự","Luật Thương mại","Luật Quốc tế"])
    st.multiselect("Từ khóa AI",
    ["Contract","FDCPA","CISG","Arbitration","Dispute Resolution"])
    st.button("Xác nhận từ khóa", key="b2", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Nguồn tra cứu")
    st.checkbox("OPAC ULAW", True)
    st.checkbox("CSDL Nội sinh", True)
    st.checkbox("ĐH Luật Hà Nội")
    st.checkbox("ĐHQG Hà Nội")
    st.checkbox("UEL")
    st.checkbox("HeinOnline", True)
    st.checkbox("Westlaw", True)
    st.checkbox("Thư Viện Pháp Luật")
    st.button("Bắt đầu tra cứu", key="b3", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Kiểm duyệt kết quả")
    st.progress(78)
    df = pd.DataFrame({
        "Tiêu đề":["Giải quyết tranh chấp hợp đồng","Pháp luật đất đai"],
        "Năm":[2025,2024],
        "Nguồn":["ULAW","HeinOnline"]
    })
    st.dataframe(df, use_container_width=True)
    st.button("📥 Xuất báo cáo DOCX chuẩn ULAW", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
m1,m2,m3,m4,m5 = st.columns(5)
m1.info("🚀 Tự động hóa 80-90%")
m2.info("🧠 AI thông minh")
m3.info("✅ Kết quả chính xác")
m4.info("📄 Báo cáo chuẩn ULAW")
m5.info("♻️ Tái sử dụng dữ liệu")

st.divider()

st.subheader("Thống kê hệ thống")
a,b,c,d = st.columns(4)
a.metric("Hồ sơ tra cứu", "1,245")
b.metric("Tài liệu xử lý", "82,540")
c.metric("Tỷ lệ tự động hóa", "90%")
d.metric("Thời gian tiết kiệm", "75%")

