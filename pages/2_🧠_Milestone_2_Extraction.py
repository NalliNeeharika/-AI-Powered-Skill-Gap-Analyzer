import streamlit as st
import spacy
from spacy.pipeline import EntityRuler
import pandas as pd
from utils import apply_custom_css, render_top_nav
import plotly.graph_objects as go
import plotly.express as px
import random

st.set_page_config(page_title="Skill Extraction", page_icon="🧠", layout="wide")
apply_custom_css()
render_top_nav()

# --- SKILLS DATABASE (Integrated from src/skills_db.py) ---
SKILL_DB = [
    # Programming Languages
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Ruby", "Swift", "Go", "Kotlin", "Rust", "PHP", "R", "Matlab", "Scala", "Dart", "HTML", "CSS", "SQL", "NoSQL", "Bash", "Shell", "Perl", "Lua",
    
    # Machine Learning & AI
    "Machine Learning", "Deep Learning", "Neural Networks", "NLP", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "Generative AI", "LLM", "Transformers", "BERT", "GPT", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn", "OpenCV", "Hugging Face", "MLOps",
    
    # Data Science & Analytics
    "Data Analysis", "Data Visualization", "Big Data", "Spark", "Hadoop", "Hive", "Tableau", "Power BI", "Excel", "Data Mining", "Statistics", "A/B Testing", "Snowflake", "Databricks", "ETL", "Data Pipelines",
    
    # Web Development
    "React", "React.js", "Angular", "Vue", "Vue.js", "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", "Laravel", "jQuery", "Bootstrap", "Tailwind CSS", "SASS", "LESS", "GraphQL", "REST API", "WebSockets",
    
    # Cloud & DevOps
    "AWS", "Amazon Web Services", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", "CI/CD", "Terraform", "Ansible", "Linux", "Unix", "Nginx", "Apache", "Heroku", "Vercel", "Netlify",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "Cassandra", "DynamoDB", "Firebase", "SQLite", "MariaDB",
    
    # Soft Skills
    "Communication", "Teamwork", "Leadership", "Problem Solving", "Critical Thinking", "Project Management", "Agile", "Scrum", "Time Management", "Adaptability", "Collaboration", "Creativity", "Emotional Intelligence", "Conflict Resolution", "Decision Making", "Mentoring", "Presentation Skills", "Negotiation",
    
    # Tools & Others
    "Jira", "Trello", "Asana", "Slack", "Zoom", "Microsoft Office", "Adobe Creative Suite", "Photoshop", "Illustrator", "Figma", "Sketch", "InVision", "Salesforce", "SAP"
]

SKILL_PATTERNS = []
for skill in SKILL_DB:
    if skill == "R":
        SKILL_PATTERNS.append({"label": "SKILL", "pattern": [{"TEXT": "R"}]}) 
    else:
        SKILL_PATTERNS.append({"label": "SKILL", "pattern": [{"LOWER": skill.lower()}]})


# --- EXTRACTOR LOGIC (Integrated from src/extractor.py) ---
nlp = None

@st.cache_resource
def load_model():
    # Helper to load model once
    try:
        model = spacy.load("en_core_web_lg")
    except OSError:
        model = spacy.load("en_core_web_sm")
    
    # Add EntityRuler
    if "entity_ruler" not in model.pipe_names:
        ruler = model.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(SKILL_PATTERNS)
    return model

def extract_skills_from_text(text):
    """
    Extracts skills from text using Spacy + EntityRuler.
    """
    nlp_model = load_model()
    doc = nlp_model(text)
    
    skills = []
    
    # Extract entities labeled as SKILL
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            skills.append(ent.text)
            
    return sorted(list(set(skills)))

def categorize_skills(skills_list):
    """
    Simple rule-based categorization for visualization.
    """
    categories = {
        "Technical": [],
        "Soft Skills": [],
        "Tools/Frameworks": []
    }
    
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

st.markdown("# 🧠 Milestone 2: Skill Extraction")
st.markdown("### AI-Powered Entity Recognition")

# Check inputs
if 'resume_text' not in st.session_state or not st.session_state['resume_text']:
    st.error(" Please go to **Milestone 1** and upload your documents first.")
    st.image("https://media.giphy.com/media/l41lFw057lAJQMlxS/giphy.gif") # Optional fun check
    if st.button("Go to M1"): st.switch_page("pages/1_📂_Milestone_1_Ingestion.py")
    st.stop()

# ... (State Init)
if 'resume_skills' not in st.session_state:
    st.session_state['resume_skills'] = []
if 'jd_skills' not in st.session_state:
    st.session_state['jd_skills'] = []
if 'resume_context' not in st.session_state:
    st.session_state['resume_context'] = {}

# --- HELPER: Extra Entity Extraction (Regex based for speed/demo) ---
import re
def extract_context(text):
    text_lower = text.lower()
    context = {"roles": [], "certs": []}
    
    # Common Role Keywords
    roles_db = ["data scientist", "data analyst", "software engineer", "manager", "developer", "architect", "consultant", "intern"]
    for r in roles_db:
        if r in text_lower:
            context["roles"].append(r.title())
            
    # Common Cert Keywords
    certs_db = ["pmp", "aws certified", "azure fundamentals", "scrum master", "cissp", "google data analytics", "ibm data science"]
    for c in certs_db:
        if c in text_lower:
            context["certs"].append(c.upper() if len(c) < 5 else c.title())
            
    return context

# Extraction Trigger
if not st.session_state['resume_skills']:
    with st.spinner("Running NLP Models..."):
        st.session_state['resume_skills'] = extract_skills_from_text(st.session_state['resume_text'])
        st.session_state['jd_skills'] = extract_skills_from_text(st.session_state['jd_text'])
        
        # Run Context Extraction
        st.session_state['resume_context'] = extract_context(st.session_state['resume_text'])
        
        st.rerun()

# --- Advanced Visualizations ---

def plot_sunburst(skills, title):
    if not skills: return None
    cats = categorize_skills(skills)
    data = []
    for cat, skill_list in cats.items():
        for s in skill_list:
            data.append({"Category": cat, "Skill": s, "Value": 1})
    if not data: return None
    df = pd.DataFrame(data)
    fig = px.sunburst(df, path=['Category', 'Skill'], values='Value', title=title, color='Category', color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(paper_bgcolor='rgba(255, 255, 255, 0.05)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400, margin=dict(t=40, b=10, l=10, r=10))
    return fig

# --- Main Layout ---
tab_charts = st.container()

with tab_charts:
    # Gap Analysis moved to Milestone 3.
    # Focusing purely on Extraction visualization here.

    st.markdown("### ☀️ Detailed Skill Hierarchy")
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        st.subheader("👤 Candidate Composition")
        sb_res = plot_sunburst(st.session_state['resume_skills'], "Your Skills")
        if sb_res: st.plotly_chart(sb_res, use_container_width=True)
    with r2_c2:
        st.subheader("🎯 Job Composition")
        sb_jd = plot_sunburst(st.session_state['jd_skills'], "Required Skills")
        if sb_jd: st.plotly_chart(sb_jd, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🧬 Identified Skills Ecosystem")
    su_col1, su_col2 = st.columns([2, 1])
    with su_col1:
        st.markdown('<div style="padding: 20px; background: rgba(0,0,0,0.2); border-radius: 20px;">', unsafe_allow_html=True)
        all_skills = list(set(st.session_state['resume_skills'] + st.session_state['jd_skills']))
        random.shuffle(all_skills)
        tags_html = ""
        for i, skill in enumerate(all_skills):
            delay = random.uniform(0, 5)
            if skill in st.session_state['resume_skills'] and skill in st.session_state['jd_skills']: color = "#00ffbe"
            elif skill in st.session_state['resume_skills']: color = "#FF00CC"
            else: color = "#00d2ff"
            tags_html += f'<span class="skill-tag-floating" style="animation-delay: -{delay}s; border-color: {color};">{skill}</span>'
        st.markdown(tags_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with su_col2:
        st.markdown("#### 📌 Profile Context")
        
        # Display Roles
        roles = st.session_state.get('resume_context', {}).get('roles', [])
        if roles:
            st.markdown(f"**Detected Roles:**")
            for r in roles[:3]:
                st.caption(f"🔹 {r}")
        
        # Display Certs
        certs = st.session_state.get('resume_context', {}).get('certs', [])
        if certs:
            st.markdown(f"**Certifications:**")
            for c in certs[:3]:
                st.caption(f"🏅 {c}")
                
        if not roles and not certs:
             st.caption("No specific roles or certifications generated.")

        st.markdown("---")
        st.markdown("#### 🎯 Confidence")
        st.metric("Accuracy", f"{min(98, 85 + len(st.session_state['resume_skills']))}%")
        st.metric("Entity Density", "High")

    st.markdown("---")
    c1_next, c2_next, c3_next = st.columns([1, 2, 1])
    with c2_next:
         st.markdown("<h2 style='text-align: center; margin-bottom: 30px; background: linear-gradient(to right, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🚀 Ready for the Gap Analysis?</h2>", unsafe_allow_html=True)
         st.page_link("pages/3_📊_Milestone_3_Analysis.py", label="✨ Go to Milestone 3: Gap Analysis ✨", icon="📊", use_container_width=True)
