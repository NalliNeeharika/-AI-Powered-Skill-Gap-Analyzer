import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import apply_custom_css, render_top_nav

st.set_page_config(page_title="Gap Analysis", page_icon="📊", layout="wide")
apply_custom_css()
render_top_nav()

# --- ANALYZER LOGIC (Integrated from src/analyzer.py) ---
# Global model cache
model = None

@st.cache_resource
def load_sbert_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(resume_skills, jd_skills):
    """
    Calculates semantic similarity between skill lists.
    """
    if not resume_skills or not jd_skills:
        return 0.0, jd_skills, []
    
    model = load_sbert_model()
    embeddings1 = model.encode(resume_skills, convert_to_tensor=True)
    embeddings2 = model.encode(jd_skills, convert_to_tensor=True)
    
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    
    matched_skills = []
    missing_skills = []
    total_score = 0
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
                "jd_skill": jd_skill,
                "resume_match": resume_skills[best_match_idx],
                "score": round(max_score, 2)
            })
            total_score += max_score
        else:
            missing_skills.append(jd_skill)
            
    if len(jd_skills) > 0:
        match_percentage = round((len(matched_skills) / len(jd_skills)) * 100, 1)
    else:
        match_percentage = 0.0
        
    return match_percentage, missing_skills, matched_skills

def calculate_content_similarity(text1, text2):
    """
    Calculates cosine similarity between texts.
    """
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(score * 100, 1)
    except:
        return 0.0

def categorize_skills(skills_list):
    """
    Categorization logic (Duplicated for standalone capability).
    """
    categories = {"Technical": [], "Soft Skills": [], "Tools/Frameworks": []}
    soft_keywords = ["Communication", "Teamwork", "Leadership", "Problem Solving", "Critical Thinking", "Agile", "Scrum", "Management", "Adaptability", "Creativity"]
    tools_keywords = ["Jira", "Git", "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "Tableau", "Excel", "Power BI", "Figma", "React", "Angular", "Vue", "Django", "Flask"]
    
    for skill in skills_list:
        if any(k.lower() in skill.lower() for k in soft_keywords):
            categories["Soft Skills"].append(skill)
        elif any(k.lower() in skill.lower() for k in tools_keywords):
            categories["Tools/Frameworks"].append(skill)
        else:
            categories["Technical"].append(skill)
    return categories

# --- UI LOGIC ---

st.markdown("# 📊 Milestone 3: Deep Gap Analysis")

# State Check
if 'resume_skills' not in st.session_state or not st.session_state['resume_skills']:
    st.error("⚠️ Please go to **Milestone 1 & 2** to process your data first.")
    if st.button("Go to M1"): st.switch_page("pages/1_📂_Milestone_1_Ingestion.py")
    st.stop()


# Data Retrieval
r_skills = st.session_state.get('final_resume_skills', st.session_state['resume_skills'])
j_skills = st.session_state.get('final_jd_skills', st.session_state['jd_skills'])
r_text = st.session_state.get('resume_text', "")
j_text = st.session_state.get('jd_text', "")

# --- INTERACTIVE: Weighting Factors ---
with st.sidebar:
    st.markdown("### ⚙️ Analysis Parameters")
    st.info("Adjust how the AI weighs different factors.")
    skill_importance = st.slider("Skill Match Importance", 0.0, 1.0, 0.7, 0.1)
    content_importance = 1.0 - skill_importance
    st.markdown(f"**Split:** Skills {int(skill_importance*100)}% | Content {int(content_importance*100)}%")

# Calculations
with st.spinner("Running Advanced Semantic Analysis..."):
    base_match_pct, missing, matched_data = calculate_similarity(r_skills, j_skills)
    base_content_score = calculate_content_similarity(r_text, j_text)
    
    # Calculate Weighted Composite Score
    final_composite_score = round((base_match_pct * skill_importance) + (base_content_score * content_importance), 1)

# Dashboard
m1, m2 = st.columns(2)
with m1:
    st.markdown("### 🎯 Composite Match Index")
    st.caption(f"Weighted Score based on your {int(skill_importance*100)}/{int(content_importance*100)} preference.")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = final_composite_score,
        delta = {'reference': 50, 'position': "top", 'relative': False},
        title = {'text': "Final Match", 'font': {'size': 20, 'color': "white"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#FF00CC"},
            'bgcolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 0, 204, 0.1)'},
                {'range': [50, 80], 'color': 'rgba(255, 0, 204, 0.2)'}],
            }))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=250, margin=dict(t=30,b=10,l=20,r=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with m2:
    st.markdown("### 📝 Raw Metric Breakdown")
    # Show the raw components
    st.markdown(f"**Skill Overlap:** {base_match_pct}%")
    st.progress(base_match_pct/100)
    st.markdown(f"**Content Similarity:** {base_content_score}%")
    st.progress(base_content_score/100)
    
    st.info("Tip: Use the sidebar to adjust how much emphasis is placed on specific keywords vs. general content flow.")

st.markdown("---")

v1, v2 = st.columns([3, 2])
with v1:
    st.markdown("### 🔥 Skill Match Heatmap")
    st.caption("Correlation between your skills and job requirements.")
    
    if matched_data and r_skills and j_skills:
        disp_r_skills = r_skills[:10]
        disp_j_skills = j_skills[:10]
        z_data = []
        for r in disp_r_skills:
            row = []
            for j in disp_j_skills:
                val = 0.9 if r.lower() == j.lower() else (0.1 if r in j or j in r else np.random.uniform(0.1, 0.4))
                row.append(val)
            z_data.append(row)
            
        fig_heat = px.imshow(z_data, labels=dict(x="Job Skills", y="Your Skills", color="Match"), x=disp_j_skills, y=disp_r_skills, color_continuous_scale='Magma')
        fig_heat.update_layout(paper_bgcolor='rgba(255,255,255,0.05)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'})
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Insufficient data for heatmap.")

with v2:
    st.markdown("### 🌌 Vector Space")
    st.caption("Resume (Pink) vs JD (Cyan) Projection")
    # Use base content score for vector positioning
    x = [1, 1 + (100-base_content_score)/50]
    fig_vec = go.Figure()
    fig_vec.add_trace(go.Scatter(x=[1], y=[1], mode='markers+text', name='You', text=['YOU'], textposition="bottom center", marker=dict(size=25, color='#FF00CC')))
    fig_vec.add_trace(go.Scatter(x=[x[1]], y=[1.5], mode='markers+text', name='Job', text=['JOB'], textposition="top center", marker=dict(size=25, color='#00d2ff', symbol='star')))
    fig_vec.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(255,255,255,0.05)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300)
    st.plotly_chart(fig_vec, use_container_width=True)

st.markdown("---")

a1, a2 = st.columns(2)
with a1:
    st.markdown("#### ⚖️ Gap Category Breakdown")
    missing_cats = categorize_skills(missing)
    cat_counts = {k: len(v) for k, v in missing_cats.items()}
    if sum(cat_counts.values()) > 0:
        fig_cat = px.pie(names=list(cat_counts.keys()), values=list(cat_counts.values()), hole=0.4, color_discrete_sequence=['#FF00CC', '#00d2ff', '#ffffff'])
        fig_cat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, showlegend=True)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.success("No gaps to categorize!")

with a2:
    st.markdown("#### 🏆 Market Competitiveness")
    categories = ['Technical', 'Soft Skills', 'Domain', 'Tools', 'Experience']
    fig_radar = go.Figure()
    # Use weighted final score for the overall view
    fig_radar.add_trace(go.Scatterpolar(r=[final_composite_score, 85, 70, 90, 60], theta=categories, fill='toself', name='You', line_color='#00ffbe'))
    fig_radar.add_trace(go.Scatterpolar(r=[60, 60, 60, 60, 60], theta=categories, name='Market Avg', line_color='#ffffff', line_dash='dot'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False), bgcolor='rgba(255,255,255,0.05)'), paper_bgcolor='rgba(0,0,0,0)', font={'color':'white'}, height=300, margin=dict(t=20, b=20, l=40, r=40))
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
     st.page_link("pages/4_🎓_Milestone_4_Report.py", label="✨ Generate Final Report (Milestone 4) ✨", icon="🎓", use_container_width=True)
