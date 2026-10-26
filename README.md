# 💻 Computer Recommender System (Graph-based)

โปรเจค Final: ระบบแนะนำคอมพิวเตอร์โดยใช้หลักการ **Graph-based Collaborative Filtering**  
พัฒนาด้วย Python, Streamlit และ NetworkX

## 📌 เกี่ยวกับโปรเจค
ระบบนี้จะวิเคราะห์ความชอบของผู้ใช้ (User) ที่มีต่อคอมพิวเตอร์รุ่นต่างๆ โดยสร้างเป็นโครงข่ายความสัมพันธ์ (Graph Network) 
เมื่อผู้ใช้เลือกบุคคลต้นแบบ ระบบจะค้นหา "คนที่มีความชอบคล้ายกัน" และแนะนำคอมพิวเตอร์รุ่นอื่นๆ ที่คนกลุ่มนั้นชอบ แต่ยังอยู่ในรายการที่ผู้ใช้ต้นแบบยังไม่ได้เลือก

## ✨ ฟีเจอร์หลัก
- 🕸️ **Interactive Graph Visualization**: แสดงแผนภาพความสัมพันธ์ระหว่างคนและคอมพิวเตอร์แบบ Real-time
- 🎯 **Smart Recommendation**: คำนวณคะแนนความน่าจะเป็นในการแนะนำสินค้า
- 📊 **Data Dashboard**: แสดงข้อมูลสเปกและราคาของคอมพิวเตอร์ในรูปแบบตารางและ Metric
- 📱 **Responsive UI**: ออกแบบด้วย Streamlit รองรับทั้งหน้าจอคอมพิวเตอร์และมือถือ

## 🛠️ เทคโนโลยีที่ใช้
- **Python 3.9+**
- **Streamlit**: สำหรับสร้าง Web Application
- **NetworkX**: สำหรับสร้างและวิเคราะห์ Graph Network
- **Matplotlib**: สำหรับวาดแผนภาพ Graph
- **Pandas**: สำหรับจัดการข้อมูล (DataFrame)

## 🚀 วิธีติดตั้งและรันบนเครื่อง (Local)

1. Clone หรือดาวน์โหลดโปรเจคนี้
2. ติดตั้ง Dependencies ที่จำเป็น:
   ```bash
   pip install -r requirements.txt