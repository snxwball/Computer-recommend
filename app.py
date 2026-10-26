import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

# ==========================================
# 🎨 ตั้งค่าหน้า Streamlit
# ==========================================
st.set_page_config(
    page_title="Computer Recommender System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🗄️ ฐานข้อมูลคอมพิวเตอร์
# ==========================================
computer_db = [
    {'id': 'C001', 'brand': 'Dell',     'model': 'Dell XPS 13',                  'category': 'Ultrabook',  'price': 42900},
    {'id': 'C002', 'brand': 'HP',       'model': 'HP Spectre x360',              'category': '2-in-1',     'price': 48900},
    {'id': 'C003', 'brand': 'Lenovo',   'model': 'Lenovo ThinkPad X1 Carbon',    'category': 'Business',   'price': 55900},
    {'id': 'C004', 'brand': 'Apple',    'model': 'Apple MacBook Pro',            'category': 'Ultrabook',  'price': 69900},
    {'id': 'C005', 'brand': 'ASUS',     'model': 'ASUS ROG Zephyrus G14',        'category': 'Gaming',     'price': 52900},
    {'id': 'C006', 'brand': 'Acer',     'model': 'Acer Swift 3',                 'category': 'Ultrabook',  'price': 25900},
    {'id': 'C007', 'brand': 'MSI',      'model': 'MSI Prestige 14',              'category': 'Creator',    'price': 39900},
    {'id': 'C008', 'brand': 'Microsoft','model': 'Microsoft Surface Laptop 5',   'category': 'Ultrabook',  'price': 44900},
    {'id': 'C009', 'brand': 'Samsung',  'model': 'Samsung Galaxy Book3',         'category': 'Ultrabook',  'price': 38900},
    {'id': 'C010', 'brand': 'Razer',    'model': 'Razer Blade 15',               'category': 'Gaming',     'price': 79900},
]

df_computers = pd.DataFrame(computer_db)

# ==========================================
#  ข้อมูลคนและความชอบ
# ==========================================
people = ['Ing', 'Somying', 'Natee', 'Mana', 'Wichai', 'On', 'Beam', 'Non', 'Games', 'Palm']

likes = [
    ('Ing', 'Dell XPS 13'), ('Ing', 'HP Spectre x360'), ('Ing', 'Lenovo ThinkPad X1 Carbon'),
    ('Somying', 'Dell XPS 13'), ('Somying', 'HP Spectre x360'), ('Somying', 'Apple MacBook Pro'), ('Somying', 'ASUS ROG Zephyrus G14'),
    ('Natee', 'Dell XPS 13'), ('Natee', 'Apple MacBook Pro'), ('Natee', 'Acer Swift 3'),
    ('Mana', 'ASUS ROG Zephyrus G14'), ('Mana', 'Acer Swift 3'), ('Mana', 'MSI Prestige 14'),
    ('Wichai', 'HP Spectre x360'), ('Wichai', 'Apple MacBook Pro'), ('Wichai', 'Samsung Galaxy Book3'),
    ('On', 'Dell XPS 13'), ('On', 'Microsoft Surface Laptop 5'), ('On', 'Lenovo ThinkPad X1 Carbon'),
    ('Beam', 'Apple MacBook Pro'), ('Beam', 'Acer Swift 3'), ('Beam', 'Lenovo ThinkPad X1 Carbon'),
    ('Non', 'ASUS ROG Zephyrus G14'), ('Non', 'MSI Prestige 14'), ('Non', 'Samsung Galaxy Book3'),
    ('Games', 'Samsung Galaxy Book3'), ('Games', 'Razer Blade 15'), ('Games', 'Apple MacBook Pro'),
    ('Palm', 'Microsoft Surface Laptop 5'), ('Palm', 'Dell XPS 13'), ('Palm', 'HP Spectre x360')
]

# ==========================================
# ️ สร้าง Graph
# ==========================================
@st.cache_resource
def build_graph():
    G = nx.Graph()
    for person in people:
        G.add_node(person, node_type="person")
    for comp in computer_db:
        G.add_node(comp['model'], node_type="computer", comp_id=comp['id'])
    G.add_edges_from(likes)
    return G

G = build_graph()

# ==========================================
# 🧠 ฟังก์ชันแนะนำคอมพิวเตอร์
# ==========================================
def recommend_computers(G, target_person, top_n=5):
    recommendations = Counter()
    liked_computers = set(G.neighbors(target_person))
    
    for computer in liked_computers:
        for similar_person in G.neighbors(computer):
            if similar_person == target_person:
                continue
            for other_computer in G.neighbors(similar_person):
                if other_computer not in liked_computers:
                    recommendations[other_computer] += 1
    
    return recommendations.most_common(top_n)

# ==========================================
# 🎨 วาด Graph
# ==========================================
def draw_graph(G, highlight_person=None):
    fig, ax = plt.subplots(figsize=(10, 7))
    pos = nx.spring_layout(G, seed=42, k=1.2)
    
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        if G.nodes[node].get('node_type') == 'person':
            if node == highlight_person:
                node_colors.append('#FF4500')  # สีแดงส้มสำหรับคนที่เลือก
                node_sizes.append(1200)
            else:
                node_colors.append('#87CEEB')  # ฟ้า
                node_sizes.append(700)
        else:
            node_colors.append('#FFA500')  # ส้ม
            node_sizes.append(900)
    
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', alpha=0.4, width=1)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')
    
    ax.set_title("Computer Recommender System - Graph Network", fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    return fig

# ==========================================
# 🖥️ UI ส่วนหัว
# ==========================================
st.title(" Computer Recommender System")
st.markdown("""
ระบบแนะนำคอมพิวเตอร์ด้วย **Graph-based Collaborative Filtering**  
ค้นหาคนที่มีความชอบคล้ายกัน → แนะนำคอมพิวเตอร์รุ่นใหม่ที่ตรงรสนิยม
""")

st.divider()

# ==========================================
# 📊 Sidebar: เลือกคน & ดูข้อมูล
# ==========================================
st.sidebar.header("⚙️ ตั้งค่า")
selected_person = st.sidebar.selectbox(
    " เลือกบุคคลที่ต้องการแนะนำ",
    people,
    index=0
)

top_n = st.sidebar.slider("📈 จำนวนคำแนะนำที่ต้องการ", 1, 10, 5)

st.sidebar.divider()
st.sidebar.subheader("📋 ข้อมูลคอมพิวเตอร์ทั้งหมด")
st.sidebar.dataframe(
    df_computers[['id', 'brand', 'model', 'category', 'price']],
    use_container_width=True,
    hide_index=True
)

# ==========================================
# ️ แสดง Graph
# ==========================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🕸️ Graph Network")
    st.caption("โหนดสีฟ้า = คน | โหนดสีส้ม = คอมพิวเตอร์ | โหนดแดง = คนที่เลือก")
    fig = draw_graph(G, highlight_person=selected_person)
    st.pyplot(fig)

# ==========================================
# 👤 ข้อมูลคนที่เลือก
# ==========================================
with col2:
    st.subheader(f"👤 {selected_person}")
    liked = list(G.neighbors(selected_person))
    st.markdown(f"**ชอบคอมพิวเตอร์ {len(liked)} รุ่น:**")
    for comp in liked:
        st.markdown(f"  • 💚 {comp}")
    
    # หาเพื่อนที่มีความชอบร่วมกัน
    st.markdown("**👥 คนที่มีความชอบร่วมกัน:**")
    common_friends = set()
    for comp in liked:
        for person in G.neighbors(comp):
            if person != selected_person:
                common_friends.add(person)
    for friend in common_friends:
        st.markdown(f"  •  {friend}")

st.divider()

# ==========================================
# 🎯 ส่วนแนะนำ
# ==========================================
st.subheader(f"🎯 คำแนะนำคอมพิวเตอร์สำหรับ {selected_person}")
st.caption("เรียงตามคะแนนความน่าจะเป็น (ยิ่งสูง = ยิ่งตรงกับรสนิยม)")

recommendations = recommend_computers(G, selected_person, top_n=top_n)

if recommendations:
    cols = st.columns(min(len(recommendations), 5))
    for idx, (comp, score) in enumerate(recommendations):
        with cols[idx % len(cols)]:
            # ดึงข้อมูลจาก database
            comp_info = df_computers[df_computers['model'] == comp].iloc[0]
            
            with st.container(border=True):
                st.markdown(f"### {comp}")
                st.markdown(f"**ยี่ห้อ:** {comp_info['brand']}")
                st.markdown(f"**ประเภท:** {comp_info['category']}")
                st.metric(label="💰 ราคา", value=f"฿{comp_info['price']:,}")
                st.metric(label="⭐ คะแนนแนะนำ", value=score)
else:
    st.info(f"ไม่พบคำแนะนำสำหรับ {selected_person} (อาจชอบคอมพิวเตอร์ทุกตัวแล้ว)")

st.divider()

# ==========================================
# 📊 ตารางเปรียบเทียบ
# ==========================================
st.subheader("📊 ตารางเปรียบเทียบคำแนะนำ")
if recommendations:
    rec_df = pd.DataFrame(recommendations, columns=['model', 'score'])
    rec_df = rec_df.merge(df_computers[['model', 'brand', 'category', 'price']], on='model')
    rec_df = rec_df[['model', 'brand', 'category', 'price', 'score']]
    rec_df.columns = ['รุ่น', 'ยี่ห้อ', 'ประเภท', 'ราคา (บาท)', 'คะแนน']
    st.dataframe(rec_df, use_container_width=True, hide_index=True)

# ==========================================
# 📖 อธิบายหลักการทำงาน
# ==========================================
with st.expander(" หลักการทำงานของระบบ"):
    st.markdown("""
    ### Graph-based Collaborative Filtering
    
    1. **สร้าง Graph 2 โหนด**: Person (คน) และ Computer (คอมพิวเตอร์)
    2. **สร้างความสัมพันธ์**: `(Person)-[:LIKES]->(Computer)`
    3. **หาคนที่ชอบคล้ายกัน**: ดู Neighbor ร่วมกันของคอมพิวเตอร์ที่คนๆ นั้นชอบ
    4. **นับคะแนน**: คอมพิวเตอร์ที่คนมีความชอบคล้ายกันชอบ → บวกคะแนน +1
    5. **เรียงลำดับ**: แนะนำรุ่นที่ได้คะแนนสูงสุด
    
    ### สูตรอย่างง่าย
    ```
    Score(Computer X) = จำนวนคนที่ชอบคอมพิวเตอร์เดียวกันกับเรา 
                        และชอบ Computer X ด้วย
    ```
    """)

# ==========================================
# 🔚 Footer
# ==========================================
st.divider()
st.caption("💻 Final Project - Computer Recommender System with Graph Network | Built with Streamlit + NetworkX")