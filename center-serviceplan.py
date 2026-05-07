import pandas as pd
import streamlit as st

# ... (ส่วนการตั้งค่า URL เหมือนเดิม) ...

try:
    df = load_data(url)
    
    # 1. ล้างช่องว่างที่อาจติดมากับชื่อคอลัมน์ (เพื่อความชัวร์)
    df.columns = df.columns.str.strip()
    
    # 2. (เลือกทำ) ถ้าอยากเช็คว่าตอนนี้ระบบเห็นคอลัมน์ชื่ออะไรบ้าง ให้เอาเครื่องหมาย # ออก
    # st.write("รายชื่อคอลัมน์ที่พบ:", df.columns.tolist())

    st.success("เชื่อมต่อข้อมูลสำเร็จ!")

    # 3. ส่วน Side bar (ใช้ชื่อคอลัมน์ให้ตรงกับที่เห็นในไฟล์)
    # หมายเหตุ: ตรวจสอบใน Google Sheets ว่าชื่อคือ 'health-zone' หรือ 'เขตสุขภาพ'
    col_zone = "health-zone" 
    
    if col_zone in df.columns:
        selected_zone = st.sidebar.multiselect(
            "เลือกเขตสุขภาพ", 
            options=df[col_zone].unique(), 
            default=df[col_zone].unique()
        )
        filtered_df = df[df[col_zone].isin(selected_zone)]
    else:
        st.error(f"ไม่พบคอลัมน์ '{col_zone}' กรุณาตรวจสอบการสะกดคำ")
        filtered_df = df

    # 4. แสดงตัวชี้วัด (Metrics)
    # อิงตามชื่อคอลัมน์ในไฟล์ DATA2567(y68): 'pass-failed' และ 'results-3.1.3ข'
    col1, col2, col3 = st.columns(3)
    
    if "pass-failed" in filtered_df.columns:
        total_centers = len(filtered_df)
        pass_count = len(filtered_df[filtered_df["pass-failed"] == "ผ่าน"])
        pass_rate = (pass_count / total_centers) * 100 if total_centers > 0 else 0
        
        col1.metric("จำนวน สพด. ทั้งหมด", f"{total_centers:,} แห่ง")
        col2.metric("ผ่านเกณฑ์มาตรฐาน", f"{pass_rate:.1f}%")
        
    if "results-3.1.3ข" in filtered_df.columns:
        col3.metric("ผลประเมิน 3.1.3ข (ผ่าน)", len(filtered_df[filtered_df["results-3.1.3ข"] == "ผ่าน"]))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
