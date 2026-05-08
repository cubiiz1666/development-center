import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & CUSTOM CSS ---
st.set_page_config(page_title="สพด. Dashboard 2567", layout="wide")

# ปรับแต่ง UI ให้เป็นกึ่งทางการ (Navy Blue & Amber)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #002d62; font-family: 'Sarabun', sans-serif; }
    .header-box { background-color: #ffd54f; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING (Direct Export) ---
SHEET_ID = "1mGVj2fHIgwtOzbJTKP0_T-ABmSlmayQ1rb48rY4SSFI"
GID = "469626894"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=3600)
def load_data(link):
    data = pd.read_csv(link)
    # ล้างชื่อคอลัมน์: ตัดช่องว่าง, ตัวเล็กหมด, ลบจุดและขีดตามที่คุณแก้ไข
    data.columns = data.columns.str.strip().str.lower().str.replace('.', '').str.replace('-', '')
    return data

try:
    df = load_data(url)
    
    # --- 3. SIDEBAR FILTERS ---
    st.sidebar.image("https://www.anamai.moph.go.th/assets/img/logo_anamai.png", width=100) # ตัวอย่าง Logo
    st.sidebar.title("ตัวกรองข้อมูล")
    
    # Filter: เขตสุขภาพ
    if 'healthzone' in df.columns:
        zone_options = sorted(df['healthzone'].unique())
        selected_zones = st.sidebar.multiselect("เลือกเขตสุขภาพ", zone_options, default=zone_options)
        df_filtered = df[df['healthzone'].isin(selected_zones)]
    else:
        df_filtered = df

    # Filter: สังกัด (ministry)
    if 'ministry' in df.columns:
        ministry_options = sorted(df['ministry'].unique())
        selected_min = st.sidebar.multiselect("เลือกสังกัด", ministry_options, default=ministry_options)
        df_filtered = df_filtered[df_filtered['ministry'].isin(selected_min)]

    # --- 4. TOP ROW: 3 COLUMNS ---
    st.title("📊 ระบบติดตามผลการประเมิน สพด. ปีการศึกษา 2567")
    
    top_col1, top_col2, top_col3 = st.columns([3, 4, 3])

   # คอลัมน์ 1: Donut Chart (ระดับคุณภาพ)
    with top_col1:
        st.markdown('<div class="header-box">ระดับคุณภาพการประเมิน</div>', unsafe_allow_html=True)
        if 'passfailed' in df_filtered.columns:
            status_counts = df_filtered['passfailed'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig_donut = px.pie(status_counts, values='count', names='status', hole=0.6,
                               color='status',
                               color_discrete_map={'ผ่าน': '#ffd54f', 'ไม่ผ่าน': '#002d62'})
            
            # ปรับตำแหน่ง Legend ไว้ด้านล่าง (Horizontal Legend)
            fig_donut.update_layout(
                legend=dict(
                    orientation="h",      # กำหนดเป็นแนวนอน
                    yanchor="bottom",
                    y=-0.3,               # ปรับค่าติดลบเพื่อให้ลงไปอยู่ใต้กราฟ
                    xanchor="center",
                    x=0.5                 # จัดให้อยู่กึ่งกลาง
                ),
                margin=dict(t=0, b=80, l=0, r=0), # เพิ่ม Margin ด้านล่าง (b) เพื่อไม่ให้โดนตัดขอบ
                height=300 # เพิ่มความสูงเล็กน้อยเพื่อให้มีพื้นที่สำหรับ Legend
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    # คอลัมน์ 2: แผนภูมิแท่งรายจังหวัด (แทนแผนที่เพื่อให้เห็นความเปรียบเทียบชัดเจน)
    with top_col2:
        st.markdown('<div class="header-box">การกระจายตัวรายจังหวัด</div>', unsafe_allow_html=True)
        if 'province' in df_filtered.columns:
            prov_data = df_filtered.groupby(['province', 'passfailed']).size().reset_index(name='counts')
            fig_bar = px.bar(prov_data, x='province', y='counts', color='passfailed',
                             barmode='stack', height=300,
                             color_discrete_map={'ผ่าน': '#ffd54f', 'ไม่ผ่าน': '#002d62'},
                             template="plotly_white")
            fig_bar.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)

    # คอลัมน์ 3: Search & KPI
    with top_col3:
        st.markdown('<div class="header-box">ค้นหาและสรุปผล</div>', unsafe_allow_html=True)
        search_id = st.text_input("🔍 ค้นหารหัส สพด. (10 หลัก)", placeholder="ใส่รหัสที่นี่...")
        
        if search_id:
            search_res = df_filtered[df_filtered['userid'].astype(str).str.contains(search_id)]
            if not search_res.empty:
                st.info(f"พบข้อมูล: {search_res.iloc[0]['center']}")
            else:
                st.warning("ไม่พบรหัสนี้ในฐานข้อมูล")

        # KPI Metrics
        total_n = len(df_filtered)
        st.metric("จำนวน สพด. ทั้งหมด (แห่ง)", f"{total_n:,}")
        
        if 'passfailed' in df_filtered.columns:
            pass_n = len(df_filtered[df_filtered['passfailed'] == "ผ่าน"])
            st.metric("ผ่านเกณฑ์มาตรฐาน (แห่ง)", f"{pass_n:,}")

    # --- 5. BOTTOM ROW: DATA TABLE ---
    st.markdown("---")
    st.subheader("📂 รายละเอียดข้อมูลสถานพัฒนาเด็กปฐมวัย")
    
    # ตกแต่งตารางให้น่าอ่าน
    display_cols = ['userid', 'center', 'province', 'healthzone', 'passfailed', 'results313b']
    # กรองเฉพาะคอลัมน์ที่มีอยู่จริงเพื่อป้องกัน Error
    existing_cols = [c for c in display_cols if c in df_filtered.columns]
    
    st.dataframe(df_filtered[existing_cols], use_container_width=True, height=400)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดทางเทคนิค: {e}")
    st.info("กรุณาตรวจสอบชื่อคอลัมน์ใน Google Sheets อีกครั้ง")
