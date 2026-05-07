import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ (โทนสีน้ำเงินเข้ม - กึ่งทางการ)
st.set_page_config(page_title="Oral Health Dashboard 2026", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    h1 { color: #003366; } /* Navy Blue */
    </style>
    """, unsafe_allow_html=True)

st.title("📊 ระบบรายงานผลการประเมิน สพด. ปีการศึกษา 2567")

# 2. เชื่อมต่อข้อมูลจาก Google Sheets (ระบุ URL ของชีทคุณ)
sheet_id = "1mGVj2fHIgwtOzbJTKP0_T-ABmSlmayQ1rb48rY4SSFI"
gid_id = "469626894"
url = "https://docs.google.com/spreadsheets/d/1mGVj2fHIgwtOzbJTKP0_T-ABmSlmayQ1rb48rY4SSFI/edit?gid=469626894#gid=469626894"

@st.cache_data(ttl=86400) # อัปเดตข้อมูลทุก 24 ชั่วโมง
def load_data(url):
    # ใช้ pandas อ่านโดยตรง จะเสถียรกว่าในกรณี public sheet
    return pd.read_csv(url)

try:
    df = load_data(url)
    st.success("เชื่อมต่อข้อมูลสำเร็จ!")
except Exception as e:
    st.error(f"ไม่สามารถดึงข้อมูลได้: {e}")

# 3. ส่วนฟิลเตอร์สำหรับเจ้าหน้าที่ (Sidebar)
st.sidebar.header("ตัวเลือกการกรองข้อมูล")
selected_zone = st.sidebar.multiselect("เลือกเขตสุขภาพ", options=df["health-zone"].unique(), default=df["health-zone"].unique())
filtered_df = df[df["health-zone"].isin(selected_zone)]

# 4. หน้าจอหลักสำหรับผู้บริหาร (Metrics)
col1, col2, col3 = st.columns(3)
total_centers = len(filtered_df)
pass_rate = (len(filtered_df[filtered_df["pass-failed"] == "ผ่าน"]) / total_centers) * 100

col1.metric("จำนวน สพด. ทั้งหมด", f"{total_centers:,} แห่ง")
col2.metric("ผ่านเกณฑ์มาตรฐาน", f"{pass_rate:.1f}%")
col3.metric("ผลประเมิน 3.1.3ข (ผ่าน)", len(filtered_df[filtered_df["results-3.1.3ข"] == "ผ่าน"]))

# 5. กราฟวิเคราะห์รายพื้นที่
st.subheader("📈 สถานะการประเมินแยกตามจังหวัด")
fig = px.histogram(filtered_df, x="province", color="pass-failed", 
                   barmode="group", color_discrete_map={"ผ่าน": "#2E7D32", "ไม่ผ่าน": "#C62828"})
st.plotly_chart(fig, use_container_width=True)

# 6. ตารางข้อมูลละเอียด
with st.expander("ดูข้อมูลรายสถานประกอบการ"):
    st.write(filtered_df[["no.", "development-center", "province", "pass-failed", "results-3.1.3ข"]])
