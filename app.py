import streamlit as st
import pandas as pd
import os
import tempfile
from db_handler import login_user, add_user, save_scan_result
from parser_engine import ResumeParser
from report_generator import generate_report

# --- UI CONFIG (Dark/Teal Theme) ---
st.set_page_config(page_title="TalentSphere AI", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stTextInput>div>div>input { background-color: #262730; color: white; border: 1px solid #4A4A4A; }
    .stButton>button { background-color: #00ADB5; color: white; border: none; font-weight: bold; }
    h1, h2, h3 { color: #00ADB5 !important; }
    .stAlert { color: black; }
    </style>
    
""", unsafe_allow_html=True)

# --- CLOUD-SAFE FILE SAVING ---
def save_uploaded_file(uploaded_file):
    # Use tempfile to handle file safely without hardcoded paths
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        return tmp_file.name

# --- LOGIN SCREEN ---
def login_screen():
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.title("TalentSphere AI")
        st.markdown("### ⚡ Enterprise Hiring Platform")
        st.info("Log in to access Resume Diagnostics or Candidate Ranking.")
    with c2:
        tab1, tab2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])
        with tab1:
            user = st.text_input("Username", key="l_u")
            pw = st.text_input("Password", type="password", key="l_p")
            if st.button("LOGIN", use_container_width=True):
                data = login_user(user, pw)
                if data:
                    st.session_state.update({'logged_in': True, 'user': data, 'username': user})
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
        with tab2:
            new_role = st.radio("Register As:", ["Job Seeker", "Recruiter"], horizontal=True)
            n_user = st.text_input("New Username", key="r_u")
            n_pw = st.text_input("New Password", type="password", key="r_p")
            c_name = st.text_input("Company Name (Recruiters Only)") if new_role == "Recruiter" else "Individual"
            
            if st.button("CREATE ACCOUNT", use_container_width=True):
                if not n_user or not n_pw: st.error("⚠️ Missing details")
                elif new_role == "Recruiter" and not c_name: st.error("⚠️ Company Name Required")
                else:
                    if add_user(n_user, n_pw, new_role, c_name, "General"):
                        st.success("✅ Account Created. Please Login.")
                    else: st.error("❌ Username Taken")

# --- JOB SEEKER DASHBOARD ---
def job_seeker_dashboard():
    st.sidebar.markdown(f"## 👤 {st.session_state['username']}")
    if st.sidebar.button("LOGOUT"): st.session_state['logged_in'] = False; st.rerun()
        
    st.title("🚀 Resume Diagnostics")
    
    c1, c2 = st.columns(2)
    with c1:
        skills = st.text_area("Paste Job Description Keywords", "Python, SQL, React")
    with c2:
        file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    
    if file and st.button("ANALYZE RESUME", use_container_width=True):
        if not skills.strip():
            st.error("⚠️ Please enter Job Description keywords.")
        else:
            path = save_uploaded_file(file)
            parser = ResumeParser(path)
            parser.extract_contact_details()
            parser.auto_extract_skills()
            parser.match_keywords([s.strip() for s in skills.split(",") if s.strip()])
            parser.audit_resume()
            parser.generate_roadmap()
            data = parser.parsed_data
            os.remove(path)
            
            # RESULTS
            st.divider()
            c_a, c_b = st.columns(2)
            c_a.metric("ATS Match Score", f"{data['match_score']}%")
            c_b.metric("Structure Audit Score", f"{data['audit_report']['score']}/100")
            
            t1, t2, t3, t4 = st.tabs(["🚦 FEEDBACK", "📝 STRUCTURE AUDIT", "🗺️ ROADMAP", "📄 TEMPLATES"])
            
            with t1:
                if data['missing_keywords']: st.error(f"MISSING: {', '.join(data['missing_keywords'])}")
                else: st.success("✅ Perfect Skill Match!")
                
            with t2:
                if not data['audit_report']['suggestions']: st.success("✅ Structure looks great!")
                for tip in data['audit_report']['suggestions']: st.warning(tip)
                
            with t3:
                for step in data['learning_roadmap']: st.info(step)
                
            with t4:
                st.markdown("### 🏆 Recommended Resume Templates")
                st.markdown("* **Harvard Template:** [Download PDF](https://careerservices.fas.harvard.edu/resources/bullet-point-resume-template/)")
                st.markdown("* **Overleaf (For Developers):** [View Gallery](https://www.overleaf.com/gallery/tagged/cv)")
            
            try:
                pdf = generate_report(file.name, st.session_state['username'], data['match_score'], data['missing_keywords'], data['learning_roadmap'])
                with open(pdf, "rb") as f:
                    st.download_button("📥 DOWNLOAD ANALYSIS PDF", f, file_name=pdf)
            except:
                st.warning("PDF Report generation failed (check report_generator.py)")

# --- RECRUITER DASHBOARD ---
def recruiter_dashboard():
    st.sidebar.markdown(f"## 🏢 {st.session_state['user']['company_name']}")
    if st.sidebar.button("LOGOUT"): st.session_state['logged_in'] = False; st.rerun()
        
    st.title("🏆 Candidate Analysis")
    
    mode = st.radio("Select Mode:", ["👤 Single Profile Analysis", "👥 Batch Ranking"], horizontal=True)
    target_skills = st.text_area("Required Skills (comma-separated)", "Python, React, AWS")
    req_skills = [s.strip() for s in target_skills.split(",") if s.strip()]

    if mode == "👤 Single Profile Analysis":
        file = st.file_uploader("Upload Candidate Resume", type=["pdf"])
        if file and st.button("ANALYZE CANDIDATE"):
            path = save_uploaded_file(file)
            parser = ResumeParser(path)
            parser.extract_contact_details()
            parser.extract_experience()
            parser.auto_extract_skills()
            parser.match_keywords(req_skills)
            parser.generate_interview_questions()
            data = parser.parsed_data
            os.remove(path)
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Match Score", f"{data['match_score']}%")
            c2.metric("Experience", f"{data['years_experience']} Years")
            c3.write(f"**Email:** {data['contact_info']['email']}\n\n**Phone:** {data['contact_info']['phone']}")
            
            st.subheader("🤖 Interview Questions")
            for q in data['interview_questions']: st.info(q)
            
            # --- NEW: EMAIL DRAFTER ---
            st.subheader("✉️ Automated Email Draft")
            with st.expander("Click to View Draft Email"):
                candidate_email = data['contact_info']['email']
                if data['match_score'] >= 75:
                    email_body = f"""
                    Subject: Interview Invitation - {st.session_state['user']['company_name']}
                    
                    Hi Candidate,
                    
                    We reviewed your profile and were impressed by your experience with {', '.join(data['skills_found'][:3])}.
                    We would like to invite you for an interview.
                    
                    Best,
                    {st.session_state['user']['company_name']} Recruiting Team
                    """
                    st.success("✅ **Recommendation: INTERVIEW**")
                    st.text_area("Draft", email_body, height=200)
                else:
                    email_body = f"""
                    Subject: Update on your application - {st.session_state['user']['company_name']}
                    
                    Hi Candidate,
                    
                    Thank you for applying. Unfortunately, we are looking for candidates with stronger experience in: {', '.join(data['missing_keywords'][:3])}.
                    We will keep your resume on file.
                    
                    Best,
                    {st.session_state['user']['company_name']} Recruiting Team
                    """
                    st.error("❌ **Recommendation: REJECT**")
                    st.text_area("Draft", email_body, height=200)

            # PDF Report
            try:
                pdf = generate_report(file.name, data['contact_info']['email'], data['match_score'], data['missing_keywords'], [])
                with open(pdf, "rb") as f:
                    st.download_button("📥 Download Report PDF", f, file_name=pdf)
            except:
                st.warning("Report generation skipped.")

    elif mode == "👥 Batch Ranking":
        files = st.file_uploader("Upload Multiple Resumes", type=["pdf"], accept_multiple_files=True)
        if files and st.button("RANK CANDIDATES"):
            results = []
            progress = st.progress(0)
            
            for i, file in enumerate(files):
                path = save_uploaded_file(file)
                parser = ResumeParser(path)
                parser.extract_contact_details()
                parser.extract_experience()
                parser.auto_extract_skills()
                parser.match_keywords(req_skills)
                data = parser.parsed_data
                
                results.append({
                    "Name": file.name,
                    "Score": data['match_score'],
                    "Experience (Yrs)": data['years_experience'],
                    "Email": data['contact_info']['email'],
                    "Phone": data['contact_info']['phone'],
                    "Skills": ", ".join(data['skills_found'])
                })
                os.remove(path)
                progress.progress((i+1)/len(files))
            
            # 1. Sort Data
            df = pd.DataFrame(results).sort_values(by=["Score", "Experience (Yrs)"], ascending=False)
            
            # 2. Add a 'Rank' column starting at 1
            df.insert(0, 'Rank', range(1, 1 + len(df)))
            
            st.success("✅ Analysis Complete")
            st.subheader("🏆 Leaderboard")
            
            # 3. Display with 'Rank' as the index (hides the 0, 1, 2... default index)
            st.dataframe(df.set_index('Rank'))
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Ranking CSV", csv, "ranking.csv", "text/csv")

# --- MAIN ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_screen()
else:
    if st.session_state['user']['role'] == "Job Seeker":
        job_seeker_dashboard()
    else:
        recruiter_dashboard()