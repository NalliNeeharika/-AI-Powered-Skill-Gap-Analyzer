import streamlit as st
import os
import re

# --- STYLES (Formerly src/styles.py) ---
def apply_custom_css():
    st.markdown("""
    <style>
        /* Global Animated Background - Premium Dark Theme */
        .stApp {
            background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            font-family: 'Inter', sans-serif;
        }
        
        @keyframes gradient {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
            color: #ffffff !important;
            text-shadow: 0px 0px 10px rgba(0,0,0,0.3);
            font-weight: 700;
        }
        
        p, li, label, .stMarkdown, .stText {
            color: #e0e0e0 !important;
            font-size: 1.05rem;
            line-height: 1.6;
        }
        
        /* HIDE SIDEBAR COMPLETELY */
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        
        /* Premium Glass Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 25px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            height: 100%;
            min-height: 280px; /* Enforce uniform height */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .glass-card:hover {
            transform: translateY(-10px) scale(1.02);
            border-color: #00d2ff;
            box-shadow: 0 15px 40px rgba(0, 210, 255, 0.2);
            background: rgba(255, 255, 255, 0.07);
        }
        
        .glass-card h3 {
            background: linear-gradient(to right, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }

        /* STATS CARD STYLING */
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
            transition: transform 0.3s ease;
            margin-bottom: 20px;
            min-height: 150px;
            justify-content: center;
        }
        .stat-card:hover {
            transform: scale(1.05);
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255,255,255,0.2);
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
        }
        .stat-val {
            font-size: 2.2rem;
            font-weight: 800;
            color: #fff;
            margin-bottom: 5px;
            background: linear-gradient(to right, #ffffff, #a8c0ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #bdc3c7;
        }
        .stat-delta {
            font-size: 0.8rem;
            color: #2ecc71;
            margin-top: 5px;
            font-weight: bold;
        }

        /* WORKFLOW STEP STYLING */
        .workflow-step {
            text-align: center;
            padding: 20px;
            position: relative;
        }
        .step-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            margin: 0 auto 15px auto;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
        }
        
        /* TESTIMONIAL CARD */
        .testimonial-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 20px;
            text-align: left;
            position: relative;
        }
        .testimonial-quote {
            font-style: italic;
            color: #e0e0e0;
            margin-bottom: 15px;
            font-size: 1rem;
        }
        .testimonial-author {
            font-weight: bold;
            color: #fff;
        }
        .testimonial-role {
            font-size: 0.8rem;
            color: #bdc3c7;
        }
        
        /* INFINITE TICKER */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background-color: rgba(0,0,0,0.3);
            padding-left: 100%; 
            box-sizing: content-box;
            border-top: 1px solid rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 20px;
            white-space: nowrap;
        }
        .ticker {
            display: inline-block;
            height: 40px;
            line-height: 40px;
            white-space: nowrap;
            padding-right: 100%;
            box-sizing: content-box;
            animation: ticker 30s linear infinite;
        }
        .ticker-item {
            display: inline-block;
            padding: 0 2rem;
            font-size: 1.1rem;
            color: #00d2ff;
            font-weight: 600;
        }
        @keyframes ticker {
            0% { transform: translate3d(0, 0, 0); }
            100% { transform: translate3d(-100%, 0, 0); }
        }

        /* Custom Streamlit Button Styling */
        .stButton button {
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            border: none;
            color: white;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3);
            width: 100%;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 210, 255, 0.5);
            background: linear-gradient(45deg, #3a7bd5, #00d2ff);
        }
        
        /* Page Link Styling */
        a[href*="_Milestone"], a[href="app.py"] {
            text-decoration: none;
        }

        div[data-testid="stPageLink-NavLink"] {
            background: #000000 !important;
            border: 2px solid #00fff2 !important;
            border-radius: 50px;
            padding: 15px 30px;
            color: #00fff2 !important;
            font-weight: 800;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            box-shadow: 0 0 10px rgba(0, 255, 242, 0.5), inset 0 0 10px rgba(0, 255, 242, 0.2);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 15px;
            display: flex;
            justify-content: center;
        }
        
        div[data-testid="stPageLink-NavLink"]:hover {
             box-shadow: 0 0 20px #00fff2, inset 0 0 15px #00fff2 !important;
             text-shadow: 0 0 5px #00fff2;
             transform: translateY(-2px);
             filter: brightness(1.1);
        }
        
        div[data-testid="stPageLink-NavLink"] p {
            font-size: 1.1rem;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        /* Status Elements */
        .stSuccess, .stInfo, .stWarning, .stError {
            background-color: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            color: white !important;
            border-radius: 10px;
        }
        
        /* STYLING FILE UPLOADER WIDGETS */
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 2px dashed rgba(255, 255, 255, 0.2) !important;
            border-radius: 15px !important;
            padding: 30px !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stFileUploaderDropzone"]:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: #00d2ff !important;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.3) !important;
        }
        
        [data-testid="stFileUploaderDropzone"] div {
            color: #d1d5db !important;
        }
        
        [data-testid="stFileUploaderDropzone"] button {
             border: 1px solid rgba(255,255,255,0.2) !important;
             background: linear-gradient(135deg, #1e293b, #0f172a) !important;
             color: white !important;
             transition: transform 0.2s !important;
        }
         [data-testid="stFileUploaderDropzone"] button:hover {
             border-color: #00d2ff !important;
             transform: scale(1.05) !important;
        }

        /* CUSTOM DOWNLOAD BUTTON STYLING */
        [data-testid="stDownloadButton"] button {
             background: linear-gradient(135deg, #00f260 0%, #0575e6 100%) !important;
             color: white !important;
             border: none !important;
             padding: 10px 24px !important;
             text-align: center !important;
             text-decoration: none !important;
             display: inline-block !important;
             font-size: 16px !important;
             font-weight: 600 !important;
             border-radius: 50px !important;
             transition: all 0.3s ease !important;
             box-shadow: 0 4px 15px rgba(5, 117, 230, 0.4) !important;
             text-transform: uppercase !important;
             letter-spacing: 1px !important;
             width: 100%;
        }
        
        [data-testid="stDownloadButton"] button:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(0, 242, 96, 0.6) !important;
            filter: brightness(1.2) !important;
        }

        hr {
            border-color: rgba(255,255,255,0.1);
        }
        
        /* SKILL UNIVERSE ANIMATIONS */
        @keyframes float {
            0% { transform: translateY(0px) translateX(0px) rotate(0deg); }
            33% { transform: translateY(-10px) translateX(5px) rotate(2deg); }
            66% { transform: translateY(5px) translateX(-5px) rotate(-1deg); }
            100% { transform: translateY(0px) translateX(0px) rotate(0deg); }
        }
        
        .skill-tag-floating {
            display: inline-block;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 0.9rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            animation: float 6s ease-in-out infinite;
            cursor: default;
            transition: all 0.3s ease;
        }
        
        .skill-tag-floating:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: #00d2ff;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
            transform: scale(1.1);
            z-index: 10;
            color: #00d2ff;
        }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION (Formerly src/navigation.py) ---
def render_top_nav():
    """
    Renders a top navigation bar with buttons for Home and all 4 Milestones.
    """
    st.markdown("""
    <style>
    div[data-testid="column"] {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    c_home, c1, c2, c3, c4, c5 = st.columns(6)
    
    with c_home:
        st.page_link("app.py", label="Home", icon="🏠", use_container_width=True)
    
    with c1:
        st.page_link("pages/1_📂_Milestone_1_Ingestion.py", label="Ingestion", icon="📂", use_container_width=True)
        
    with c2:
        st.page_link("pages/2_🧠_Milestone_2_Extraction.py", label="Extraction", icon="🧠", use_container_width=True)
        
    with c3:
        st.page_link("pages/3_📊_Milestone_3_Analysis.py", label="Analysis", icon="📊", use_container_width=True)
        
    with c4:
        st.page_link("pages/4_🎓_Milestone_4_Report.py", label="Report", icon="🎓", use_container_width=True)

    with c5:
        st.page_link("pages/5_📝_Resume_Creator.py", label="Creator", icon="📝", use_container_width=True)
        
    st.markdown("---")

# --- UTILS (Formerly src/utils.py) ---
def clean_text(text):
    """
    Cleans and normalizes text.
    """
    if not text:
        return ""
    
    # Replace multiple newlines/spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
