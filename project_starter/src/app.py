import streamlit as st
import asyncio
import os
import sys
import io
import time
from pathlib import Path
from dotenv import load_dotenv


st.set_page_config(
    page_title="HR Smart Advisor",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.append(str(Path(__file__).parent.parent))
from src.agent.specialists import create_researcher, create_analyst, create_writer
from src.rag.engine import rag_engine
load_dotenv()

st.markdown("""
<style>
    .main { background-color: #fcfcfc; }
    .stApp { background-color: #fcfcfc; }
    
    /* تصميم بطاقات صفحة الهوم */
    .feature-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        text-align: right;
    }
    .feature-card:hover { transform: translateY(-5px); }
    
    /* تنسيق النصوص والعناوين */
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e3a8a; }
    .hero-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 60px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
    }
    .hero-section h1 { color: white !important; }
</style>
""", unsafe_allow_html=True)

async def run_agents_pipeline(query):
    researcher = create_researcher()
    analyst = create_analyst()
    writer = create_writer()
    
    with st.status("🔍 جاري البحث في المصادر...", expanded=False) as status:
        research_result = await researcher.run(query)
        status.update(label="✅ تم العثور على المراجع", state="complete")

    with st.status("⚖️ جاري التحليل النظامي...", expanded=False) as status:
        analyst_input = f"User Query: {query}\n\nResearch Data:\n{research_result['answer']}"
        analysis_result = await analyst.run(analyst_input)
        status.update(label="✅ تم الانتهاء من التحليل القانوني", state="complete")

    writer_input = f"Original Query: {query}\n\nLegal Analysis:\n{analysis_result['answer']}"
    final_output = await writer.run(writer_input)
    
    return final_output['answer'], research_result['answer']

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    st.title("HR Advisor")
    st.markdown("---")
    
    page = st.radio("القائمة الرئيسية", ["🏠 الصفحة الرئيسية", "💬 المستشار الذكي"], index=0)
    
    st.markdown("---")
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


if page == "🏠 الصفحة الرئيسية":
    st.markdown("""
        <div class="hero-section">
            <h1>مرحباً بك في المستشار الذكي للموارد البشرية 👋</h1>
            <p style="font-size: 1.2rem;">نظام متطور مدعوم بالذكاء الاصطناعي للإجابة على استفسارات نظام العمل السعودي</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>📖 مصادر موثوقة</h3>
                <p>يتم جلب المعلومات مباشرة من لوائح وزارة الموارد البشرية والـ PDFs المرفوعة في قاعدة البيانات.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>🧠 تحليل منطقي</h3>
                <p>لا يكتفي النظام بنقل النصوص، بل يقوم المحلل القانوني بربط المواد ببعضها لتقديم إجابة متماسكة.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="feature-card">
                <h3>🔍 بحث مباشر</h3>
                <p>في حال عدم توفر المعلومة محلياً، يقوم الأيجنت بالبحث في الويب لجلب أحدث التعاميم والقرارات.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🚀 كيف تبدأ؟")
    st.write("انتقل إلى صفحة **'المستشار الذكي'** من القائمة الجانبية وابدأ بطرح أسئلتك حول الإجازات، العقود، أو مكافأة نهاية الخدمة.")

elif page == "💬 المستشار الذكي":
    st.header("💬 المستشار القانوني الذكي")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 المصادر والمراجع"):
                    st.markdown(message["sources"])

    if query := st.chat_input("اسأل عن نظام العمل السعودي..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            try:
                
                response_text, raw_sources = asyncio.run(run_agents_pipeline(query))
                
                st.markdown(response_text)
                with st.expander("📚 المصادر والمراجع المستخدمة"):
                    st.info("تم بناء هذا الرد بناءً على الوثائق التالية:")
                    st.markdown(raw_sources)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "sources": raw_sources
                })
            except Exception as e:
                st.error(f"حدث خطأ: {e}")