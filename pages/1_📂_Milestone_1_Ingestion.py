import streamlit as st
import fitz  # PyMuPDF
import docx
import time
from utils import apply_custom_css, render_top_nav, clean_text

st.set_page_config(page_title="Data Ingestion", page_icon="📂", layout="wide")
apply_custom_css()
render_top_nav()

# --- PARSING LOGIC (Integrated from src/parser.py) ---
def parse_pdf(file_bytes):
    """
    Extracts text from a PDF file (provided as bytes).
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

def parse_docx(file):
    """
    Extracts text from a DOCX file.
    """
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error parsing DOCX: {str(e)}"

def parse_txt(file_bytes):
    """
    Extracts text from a TXT file (provided as bytes).
    """
    try:
        return file_bytes.decode("utf-8")
    except Exception as e:
        return f"Error parsing TXT: {str(e)}"

def parse_document(uploaded_file):
    """
    Main entry point to parse various file types.
    """
    if uploaded_file is None:
        return None
    
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    if file_type == "pdf":
        return parse_pdf(uploaded_file.read())
    elif file_type == "docx":
        return parse_docx(uploaded_file)
    elif file_type == "txt":
        return parse_txt(uploaded_file.read())
    else:
        return "Unsupported file format."

# --- PAGE UI ---

st.markdown("# 📂 Milestone 1: Data Ingestion")
st.markdown("### Upload your Resume and the Job Description")

# Initialize session state for text if not exists
if 'resume_text' not in st.session_state:
    st.session_state['resume_text'] = ""
if 'jd_text' not in st.session_state:
    st.session_state['jd_text'] = ""

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Candidate Resume")
    uploaded_resume = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="resume_uploader")
    
    if uploaded_resume:
        # Simulate processing time for "Dynamic" feel
        with st.status("Processing Resume...", expanded=True) as status:
            st.write("Reading file...")
            time.sleep(0.5)
            content = parse_document(uploaded_resume)
            st.write("Normalizing text...")
            time.sleep(0.3)
            cleaned_content = clean_text(content)
            st.session_state['resume_text'] = cleaned_content
            status.update(label="Resume Processed!", state="complete", expanded=False)
        
# ... (Processing Logic)

def analyze_resume_quality(text):
    """
    Analyzes resume content for structure and quality indicators.
    """
    score = 100
    issues = []
    
    # 1. Length Check
    words = len(text.split())
    if words < 200:
        score -= 20
        issues.append("Resume is too short (<200 words). Add more detail.")
    elif words > 2000:
        score -= 10
        issues.append("Resume might be too long (>2000 words). Consider summarizing.")
        
    # 2. Section Check (Simple keyword search)
    # We look for common headers. Case insensitive.
    text_lower = text.lower()
    required_sections = ["education", "experience", "skills", "projects"]
    for sec in required_sections:
        if sec not in text_lower:
            score -= 15
            issues.append(f"Missing section: '{sec.capitalize()}'.")
            
    # 3. Email Check
    if "@" not in text:
        score -= 10
        issues.append("No email address detected.")
        
    return max(0, score), issues

# ... inside the col1 (Resume) block ...
    if uploaded_resume:
        # Simulate processing time for "Dynamic" feel
        with st.status("Processing Resume...", expanded=True) as status:
            st.write("Reading file...")
            time.sleep(0.5)
            content = parse_document(uploaded_resume)
            st.write("Normalizing text...")
            time.sleep(0.3)
            cleaned_content = clean_text(content)
            st.session_state['resume_text'] = cleaned_content
            status.update(label="Resume Processed!", state="complete", expanded=False)
        
        st.success(f"Resume Loaded: {len(st.session_state['resume_text'].split())} words detected.")
        
        # --- NEW: QUALITY CHECK ---
        q_score, q_issues = analyze_resume_quality(st.session_state['resume_text'])
        
        # Display Health Meter
        st.markdown(f"**Resume Health Score: {q_score}/100**")
        st.progress(q_score / 100)
        
        if q_issues:
            with st.expander("⚠️ Improvement Suggestions"):
                for issue in q_issues:
                    st.warning(issue)
        else:
             st.caption("✅ Resume structure looks great!")
        # --------------------------

        with st.expander("Show Parsed Content"):
            st.text_area("Resume Text", st.session_state['resume_text'], height=200)

with col2:
    st.markdown("#### 💼 Job Description")
    uploaded_jd = st.file_uploader("Upload JS (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="jd_uploader")
    
    if uploaded_jd:
        with st.status("Processing JD...", expanded=True) as status:
            st.write("Reading file...")
            time.sleep(0.5)
            content = parse_document(uploaded_jd)
            st.write("Extracting requirements...")
            time.sleep(0.3)
            cleaned_content = clean_text(content)
            st.session_state['jd_text'] = cleaned_content
            status.update(label="JD Processed!", state="complete", expanded=False)
            
        st.success(f"JD Loaded: {len(st.session_state['jd_text'].split())} words detected.")
        with st.expander("Show Parsed Content"):
            st.text_area("JD Text", st.session_state['jd_text'], height=200)

# Check if both are ready
if st.session_state['resume_text'] and st.session_state['jd_text']:
    st.markdown("---")
    
    # Metrics Section
    st.markdown("### 📊 Upload Summary")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="glass-card stat-card">
            <div class="stat-val">{len(st.session_state['resume_text'].split())}</div>
            <div class="stat-label">Resume Words</div>
            <div class="stat-delta">Ready for Analysis</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="glass-card stat-card">
            <div class="stat-val">{len(st.session_state['jd_text'].split())}</div>
            <div class="stat-label">JD Words</div>
            <div class="stat-delta">Ready for Extraction</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download Section
    st.markdown("### 📥 Download Processed Data")
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="📄 Download Parsed Resume",
            data=st.session_state['resume_text'],
            file_name="parsed_resume.txt",
            mime="text/plain",
            use_container_width=True
        )
    with dl_col2:
        st.download_button(
            label="💼 Download Parsed JD",
            data=st.session_state['jd_text'],
            file_name="parsed_jd.txt",
            mime="text/plain",
            use_container_width=True
        )
            
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Centered 'Next Step' Button
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h3 style='text-align: center; color: #00d2ff;'>🚀 Ready for next step!</h3>", unsafe_allow_html=True)
        st.page_link("pages/2_🧠_Milestone_2_Extraction.py", label="Start Milestone 2: Extraction", icon="🧠", use_container_width=True)
else:
    st.warning("Please upload both documents to proceed.")
