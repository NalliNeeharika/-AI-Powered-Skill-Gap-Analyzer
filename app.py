import streamlit as st
from utils import apply_custom_css

# --- HOME CONTENT CONFIGURATION (Integrated) ---
HOME_CONTENT = {
    "hero_title": "AI Skill Gap Analyzer",
    "hero_subtitle": "🚀 Supercharge Your Career Path",
    "hero_description": """
    <div style="font-size: 1.2rem; margin-top: 20px; line-height: 1.6; color: #e0e0e0;">
        Unlock your potential with our AI-driven insights. 
        Follow our structured 4-step milestone process to analyze your resume vs job descriptions with precision.
    </div>
    """,
    "hero_image_url": "assets/ai_brain_hero.png", 
    "hero_image_caption": "Future of AI Analysis",
    "features": [
        {"icon": "📄", "text": "Resume Parsing"},
        {"icon": "🧠", "text": "AI Analysis"},
        {"icon": "📊", "text": "Smart Reports"},
        {"icon": "⚡", "text": "Instant Feedback"}
    ],
    "milestones": [
        {
            "id": 1,
            "title": "Ingestion",
            "icon": "📂",
            "description": "Dynamic parsing of resumes (PDF, DOCX) and JDs. Extract text with high fidelity.",
            "button_text": "Start Ingestion",
            "page": "pages/1_📂_Milestone_1_Ingestion.py"
        },
        {
            "id": 2,
            "title": "Extraction",
            "icon": "🧠",
            "description": "Identify skills using Spacy & BERT. Specialized NER for tech terms.",
            "button_text": "Start Extraction",
            "page": "pages/2_🧠_Milestone_2_Extraction.py"
        },
        {
            "id": 3,
            "title": "Analysis",
            "icon": "📊",
            "description": "Compare Resume vs JD. Visualize gaps with heatmaps & compatibility scores.",
            "button_text": "Start Analysis",
            "page": "pages/3_📊_Milestone_3_Analysis.py"
        },
        {
            "id": 4,
            "title": "Report",
            "icon": "🎓",
            "description": "Generate comprehensive PDF reports with actionable learning recommendations.",
            "button_text": "View Report",
            "page": "pages/4_🎓_Milestone_4_Report.py"
        }
    ],
    "workflow_steps": [
        {"step": 1, "title": "Upload", "text": "Drag & drop your resume.", "color": "#FF512F"},
        {"step": 2, "title": "Analyze", "text": "AI extracts key skills.", "color": "#DA22FF"},
        {"step": 3, "title": "Compare", "text": "Match against JD.", "color": "#00C6FF"},
        {"step": 4, "title": "Improve", "text": "Get learning paths.", "color": "#11998e"}
    ],
    "footer_text": "AI Skill Gap Analyzer © 2025 | Developed with ❤️"
}

st.set_page_config(
    page_title=HOME_CONTENT["hero_title"],
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Global Theme
apply_custom_css()

# Main Hero Section
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.title(HOME_CONTENT["hero_title"])
    st.markdown(f"### {HOME_CONTENT['hero_subtitle']}")
    st.markdown(HOME_CONTENT["hero_description"], unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature highlights
    cols = st.columns(len(HOME_CONTENT["features"]))
    for i, feature in enumerate(HOME_CONTENT["features"]):
        cols[i].info(f"{feature['icon']} {feature['text']}")

with col2:
    st.markdown("""
    <style>
    .hero-img {
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 210, 255, 0.3);
        transition: transform 0.3s ease;
    }
    .hero-img:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)
    
    try:
        st.image(HOME_CONTENT["hero_image_url"], 
                 caption=HOME_CONTENT.get("hero_image_caption", ""), 
                 use_container_width=True)
    except:
        st.error("Could not load hero image.")

# --- How It Works Section ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'>💡 How It Works</h3>", unsafe_allow_html=True)

if "workflow_steps" in HOME_CONTENT:
    step_cols = st.columns(len(HOME_CONTENT["workflow_steps"]))
    for i, step in enumerate(HOME_CONTENT["workflow_steps"]):
        with step_cols[i]:
            st.markdown(f"""
            <div class="workflow-step">
                <div class="step-circle" style="background: linear-gradient(135deg, {step['color']} 0%, #ffffff 150%);">
                    {step['step']}
                </div>
                <h4 style="color:{step['color']} !important;">{step['title']}</h4>
                <p style="font-size: 0.9rem;">{step['text']}</p>
            </div>
            """, unsafe_allow_html=True)

st.write("---")

# Milestone Navigation Section
st.markdown("<h2 style='text-align: center; margin-bottom: 40px;'>🚀 Start Your Journey</h2>", unsafe_allow_html=True)

cols = st.columns(len(HOME_CONTENT["milestones"]))

for i, milestone in enumerate(HOME_CONTENT["milestones"]):
    with cols[i]:
        st.markdown(f"""
        <div class="glass-card">
            <h3>{milestone['icon']} Milestone {milestone['id']}</h3>
            <h4 style="margin:0; padding:0; color:#bdc3c7 !important;">{milestone['title']}</h4>
            <div style="flex-grow: 1;">
                 <p style="font-size: 0.9rem; margin-top: 10px;">{milestone['description']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.page_link(milestone['page'], label=milestone['button_text'], icon=milestone['icon'], use_container_width=True)

st.markdown(f"<center style='color: #7f8c8d;'>{HOME_CONTENT.get('footer_text', '')}</center>", unsafe_allow_html=True)
