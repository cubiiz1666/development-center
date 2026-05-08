import streamlit as st
import pandas as pd
import plotly.express as px

# 1. การตั้งค่าหน้าเว็บ (เน้นกึ่งทางการ โทน Navy Blue)
st.set_page_config(page_title="สพด. Dashboard 2567", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #003366; font-family: 'Sarabun', sans-serif; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. จัดการ URL และการดึงข้อมูล (Direct Export CSV)
# ใช้ ID และ GID ล่าสุดที่คุณให้มา
SHEET_ID = "1mGVj2fHIgwtOzbJTKP0_T-ABmSlmayQ1rb48rY4SSFI"
GID = "469626894"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=3600) # อัปเดตข้อมูลทุก 1 ชั่วโมง
def load_data(link):
    data = pd.read_csv(link)
    # ล้างช่องว่างและแปลงเป็นตัวเล็กเพื่อความแม่นยำในการอ้างอิง
    data.columns = data.columns.str.strip().str.lower()
    return data

try:
    df = load_data(url)
    
    st.title("📊 ระบบติดตามผลการประเมิน สพด. ปีการศึกษา 2567")
    st.write("---")

    # 3. Sidebar สำหรับคัดกรองข้อมูล (Filters)
    st.sidebar.header("🔍 ตัวเลือกการกรอง")
    
    # ตรวจสอบชื่อคอลัมน์ใหม่ (healthzone)
    col_zone = "healthzone"
    if col_zone in df.columns:
        zone_list = sorted(df[col_zone].unique())
        selected_zone = st.sidebar.multiselect("เลือกเขตสุขภาพ", options=zone_list, default=zone_list)
        df = df[df[col_zone].isin(selected_zone)]
    
    # ตัวกรองจังหวัด
    if "province" in df.columns:
        prov_list = sorted(df["province"].unique())
        selected_prov = st.sidebar.multiselect("เลือกจังหวัด", options=prov_list, default=prov_list)
        df = df[df["province"].isin(selected_prov)]

    # 4. ส่วนแสดงผลหลัก (Key Metrics)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("จำนวน สพด. ทั้งหมด", f"{len(df):,}")
    
    with col2:
        if "passfailed" in df.columns:
            pass_count = len(df[df["passfailed"].str.contains("ผ่าน", na=False)])
            pass_rate = (pass_count / len(df)) * 100 if len(df) > 0 else 0
            st.metric("ร้อยละการผ่านเกณฑ์", f"{pass_rate:.1f}%")
    
    with col3:
        # สมมติชื่อใหม่ของ 3.1.3ข คือ results313b (ตามกฎไม่มีไทย/จุด/ขีด)
        col_313 = "results313b" 
        if col_313 in df.columns:
            pass_313 = len(df[df[col_313].str.contains("ผ่าน", na=False)])
            st.metric("ผ่านเกณฑ์ 3.1.3ข", f"{pass_313:,}")

    # 5. กราฟวิเคราะห์ (Visualizations)
    st.subheader("📊 สรุปผลการประเมินแยกตามพื้นที่")
    
    if "province" in df.columns and "passfailed" in df.columns:
        fig = px.histogram(df, x="province", color="passfailed",
                           title="จำนวน สพด. ที่ผ่าน/ไม่ผ่านเกณฑ์ รายจังหวัด",
                           barmode="group",
                           color_discrete_map={"ผ่าน": "#004d40", "ไม่ผ่าน": "#b71c1c"},
                           template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # 6. ตารางข้อมูลดิบ (Data Table)
    with st.expander("📂 ดูรายละเอียดข้อมูลทั้งหมด"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลได้ หรือชื่อคอลัมน์ไม่ตรง: {e}")
    st.info("คำแนะนำ: ตรวจสอบว่าชื่อคอลัมน์ใน Google Sheets ตรงกับใน Code หรือไม่")
