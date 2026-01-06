import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from fpdf import FPDF
import base64
import random
import io
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import apply_custom_css, render_top_nav

st.set_page_config(page_title="Skill Gap Dashboard", page_icon="🎓", layout="wide")
apply_custom_css()
render_top_nav()

# --- ANALYZER LOGIC ---
@st.cache_resource
def load_sbert_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(resume_skills, jd_skills):
    if not resume_skills or not jd_skills:
        return 0.0, jd_skills, []
    
    model = load_sbert_model()
    embeddings1 = model.encode(resume_skills, convert_to_tensor=True)
    embeddings2 = model.encode(jd_skills, convert_to_tensor=True)
    
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    
    matched_skills = []
    missing_skills = []
    threshold = 0.6 
    
    for j, jd_skill in enumerate(jd_skills):
        max_score = -1
        best_match_idx = -1
        for i, res_skill in enumerate(resume_skills):
            score = cosine_scores[i][j].item()
            if score > max_score:
                max_score = score
                best_match_idx = i
        
        if max_score >= threshold:
            matched_skills.append({
                "Skill": jd_skill, 
                "Your Match": resume_skills[best_match_idx], 
                "Score": round(max_score * 100, 1),
                "Status": "Match Found"
            })
        else:
            missing_skills.append(jd_skill)
            
    if len(jd_skills) > 0:
        match_percentage = round((len(matched_skills) / len(jd_skills)) * 100, 1)
    else:
        match_percentage = 0.0
        
    return match_percentage, missing_skills, matched_skills

def generate_recommendations(missing_skills):
    recs = []
    platforms = ["Coursera", "Udemy", "edX", "YouTube", "Pluralsight"]
    for skill in missing_skills:
        platform = random.choice(platforms)
        recs.append({
            "skill": skill,
            "action": f"Master {skill} with {platform}",
            "resource": f"https://www.google.com/search?q={skill}+course+{platform}",
            "platform": platform,
            "duration": f"{random.randint(4, 12)} weeks",
            "difficulty": random.choice(["Beginner", "Intermediate"])
        })
    return recs

# --- UI LOGIC ---
# --- UI LOGIC ---
st.markdown("""
<style>
    /* Dashboard Specific Styles */
    .dashboard-container {
        padding: 1rem;
    }
    
    .metric-card-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card-container:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
    }

    .metric-value-large {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }

    .metric-label-small {
        font-size: 1rem;
        color: #e2e8f0;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-top: 5px;
    }
    
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chart-container {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# DATA LOADING
if 'resume_skills' not in st.session_state:
    st.info("💡 To view the dashboard, please complete Milestone 1 & 2 first.")
    # Use mock data for preview if development/empty
    if True: # Force mock data for demonstration if empty, or just stop
       # st.stop()
       pass
    
# Mock data fallback for visualization purposes if real data is scant
r_skills = st.session_state.get('final_resume_skills', st.session_state.get('resume_skills', ["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics", "Communication"]))
j_skills = st.session_state.get('final_jd_skills', st.session_state.get('jd_skills', ["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics", "Communication", "AWS", "Project Mgmt"]))

match_pct, missing_skills, matched_skills = calculate_similarity(r_skills, j_skills)
recommendations = generate_recommendations(missing_skills)

# HEADER
st.markdown("<h2 style='color:#3b82f6; font-weight:700;'>Skill Gap Analysis Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# TOP ROW: METRICS
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card-container">
        <div class="metric-value-large">{match_pct}%</div>
        <div class="metric-label-small">Overall Match</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card-container">
        <div class="metric-value-large">{len(matched_skills)}</div>
        <div class="metric-label-small">Matched Skills</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card-container">
        <div class="metric-value-large">{len(missing_skills)}</div>
        <div class="metric-label-small">Missing Skills</div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("<br>", unsafe_allow_html=True)

# LAYOUT: CHAARTS & CONTENT
m_col1, m_col2 = st.columns([1.5, 1])

with m_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📉 Skill Match Overview</div>', unsafe_allow_html=True)
    
    # --- BAR CHART ---
    res_scores = []
    jd_scores = []
    
    # Mock data generation for visual fidelity since we only have binary match
    for skill in j_skills:
        # If matched, give a high score (80-95), else low (20-40)
        is_matched = any(isinstance(m, dict) and m['Skill'] == skill for m in matched_skills)
        if is_matched:
            res_scores.append(random.randint(85, 98))
        else:
            res_scores.append(random.randint(10, 40))
        # Job requirement is always high
        jd_scores.append(random.randint(75, 95))
        
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=j_skills,
        y=res_scores,
        name='Resume Skills',
        marker_color='#3b82f6',
        width=0.3
    ))
    fig.add_trace(go.Bar(
        x=j_skills,
        y=jd_scores,
        name='Job Requirements',
        marker_color='#4ade80',
        width=0.3
    ))
    
    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(showgrid=False, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#e2e8f0')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 100], title=dict(text="Match Percentage", font=dict(color='#e2e8f0')), tickfont=dict(color='#94a3b8')),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#e2e8f0'))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- GAUGES ROW (Top 4 Skills) ---
    st.markdown("<br>", unsafe_allow_html=True)
    g_cols = st.columns(4)
    # Pick top 4 skills to display gauges for
    top_skills = matched_skills[:4] if len(matched_skills) >= 4 else (matched_skills + [{'Skill': s, 'Score': 0} for s in missing_skills])[:4]
    
    colors = ['#22c55e', '#22c55e', '#f59e0b', '#ef4444'] # Green, Green, Orange, Red
    
    for i, col in enumerate(g_cols):
        skill_name = top_skills[i]['Skill'] if isinstance(top_skills[i], dict) else top_skills[i]
        score = top_skills[i]['Score'] if isinstance(top_skills[i], dict) else 10 # Default low if missing
        color = colors[i] if i < 4 else '#3b82f6'
        
        with col:
            # HTML/CSS Circular Gauge Simulation (Targeting Dark Mode)
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="
                    width: 60px; height: 60px; 
                    border-radius: 50%; 
                    background: conic-gradient({color} {score}%, rgba(255,255,255,0.1) 0); 
                    margin: 0 auto; 
                    display: flex; align-items: center; justify-content: center;
                    box-shadow: 0 0 10px {color}40;
                ">
                    <div style="
                        width: 48px; height: 48px; 
                        background: #0f172a; 
                        border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center;
                        font-weight: 800; color: {color}; font-size: 0.9rem;
                    ">
                        {int(score)}%
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 0.8rem; font-weight: 600; color: #cbd5e1;">{skill_name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End Chart Container

    # --- SKILL COMPARISON (Progress Bars) ---
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚖️ Skill Comparison</div>', unsafe_allow_html=True)
    
    for skill in j_skills[:3]: # Show first 3
        # Random logic for demo visual
        val = 90 if any(isinstance(m, dict) and m['Skill'] == skill for m in matched_skills) else 40
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:0.9rem; font-weight:600; color:#e2e8f0;">{skill}</span>
            </div>
            <div style="width:100%; background-color:rgba(255,255,255,0.1); border-radius:10px; height: 10px;">
                <div style="width:{val}%; background: linear-gradient(90deg, #3b82f6, #06b6d4); height:10px; border-radius:10px; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)


with m_col2:
    # --- RADAR CHART (Role View) ---
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">👤 Role View</div>', unsafe_allow_html=True)
    
    # Buttons visual
    st.markdown("""
    <div style="display:flex; gap:10px; margin-bottom:15px;">
        <button style="background:linear-gradient(135deg, #3b82f6, #2563eb); color:white; border:none; padding:6px 16px; border-radius:6px; font-weight:600; font-size:0.85rem; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);">Job Seeker</button>
        <button style="background:rgba(255,255,255,0.05); color:#94a3b8; border:1px solid rgba(255,255,255,0.1); padding:6px 16px; border-radius:6px; font-weight:600; font-size:0.85rem;">Recruiter</button>
    </div>
    """, unsafe_allow_html=True)
    
    categories = ['Technical Skills', 'Soft Skills', 'Experience', 'Education', 'Certifications']
    # Mock data for radar
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[match_pct, 70, 60, 90, 50],
        theta=categories,
        fill='toself',
        name='Current Profile',
        line_color='#3b82f6'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[90, 85, 80, 80, 80],
        theta=categories,
        fill='toself',
        name='Job Requirements',
        line_color='#4ade80',
        fillcolor='rgba(74, 222, 128, 0.1)'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(tickfont=dict(color='#e2e8f0', size=10))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        margin=dict(t=20, b=20, l=35, r=35),
        height=300,
        legend=dict(orientation="h", y=-0.15, font=dict(color='#e2e8f0')) # Moved legend down
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- UPSKILLING RECOMMENDATIONS ---
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">💡 Upskilling Recommendations</div>', unsafe_allow_html=True)
    
    for rec in recommendations[:3]:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:12px; margin-bottom:10px; border-left: 4px solid #3b82f6; border: 1px solid rgba(255,255,255,0.05); transition: all 0.2s;">
            <div style="font-weight:600; color:#e2e8f0; font-size:0.95rem;">{rec['skill']} <span style="font-weight:400; font-size:0.8rem; color:#94a3b8;">({rec['platform']})</span></div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:4px;">{rec['action']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# 4. EXPORT & RESET
st.markdown("<br>", unsafe_allow_html=True)

# PDF Logic (Clean & Formal)
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "Skill Analysis & Roadmap Report", ln=True, align='C')
    pdf.set_font("Arial", "I", 12)
    pdf.cell(0, 10, f"Generated readiness score: {match_pct}%", ln=True, align='C')
    pdf.ln(15)
    
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "1. Core Strengths (Matched)", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    for s in matched_skills:
        pdf.cell(0, 8, f"- {s['Skill']} (Validation Score: {s['Score']}%)", ln=True)
    
    pdf.ln(8)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "2. Priority Gaps (Unmatched)", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    for s in missing_skills:
        pdf.cell(0, 8, f"- {s} (Action Required)", ln=True)
        
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "3. Recommended Learning Roadmap", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    for r in recommendations[:10]:
        # Use '-' instead of '•' to avoid encoding issues with latin-1
        pdf.cell(0, 7, f"- {r['skill']} -> {r['action']} on {r['platform']}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# CSV Logic
def generate_csv():
    data = []
    for s in matched_skills: data.append({"Analytic Area": s["Skill"], "Readiness": "Qualified", "Certainty": f"{s['Score']}%", "Action": "Active Enhancement"})
    for s in missing_skills: data.append({"Analytic Area": s, "Readiness": "Gap Identified", "Certainty": "0%", "Action": "Immediate Learning"})
    return pd.DataFrame(data).to_csv(index=False).encode('utf-8')

e1, e2 = st.columns(2)
with e1:
    st.download_button("📄 Download PDF Assessment", data=generate_pdf(), file_name="Skill_Dashboard_Report.pdf", mime="application/pdf", use_container_width=True)
with e2:
    st.download_button("📊 Download Integrated CSV", data=generate_csv(), file_name="Skill_Analysis_Data.csv", mime="text/csv", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Start New Assessment", use_container_width=True):
    st.session_state.clear()
    st.switch_page("pages/1_📂_Milestone_1_Ingestion.py")
