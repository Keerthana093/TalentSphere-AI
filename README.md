# ⚡ TalentSphere AI - Smart Resume Parser & Hiring Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![Spacy](https://img.shields.io/badge/NLP-Spacy-green.svg)

**TalentSphere AI** is a full-stack automated recruitment system designed to streamline the hiring process. It uses Natural Language Processing (NLP) to parse resumes, match skills against job descriptions, and rank candidates efficiently.

## 🚀 Features

### 🏢 For Recruiters
* **Batch Ranking:** Upload multiple resumes at once and get a ranked leaderboard based on skill match and experience.
* **Smart Parsing:** Automatically extracts Contact Info (Email/Phone), Technical Skills, and Years of Experience.
* **Interview Assistant:** Generates custom technical interview questions based on the candidate's specific stack (e.g., if they know React, it asks about `useEffect`).
* **Data Export:** Download ranking results as CSV for Excel analysis.

### 👤 For Job Seekers
* **Resume Diagnostics:** Get an instant "ATS Match Score" against a target Job Description.
* **Skill Gap Analysis:** Identifies exactly which keywords are missing from your resume.
* **Structure Audit:** Checks for "Action Verbs" and essential sections (Education, Projects).
* **Learning Roadmap:** Provides direct links to Coursera courses for missing skills.

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python-based Web UI)
* **Backend Logic:** Python, Regex
* **NLP Engine:** Spacy (`en_core_web_sm`)
* **Data Processing:** Pandas
* **Database:** SQLite (for User Auth & History)
* **PDF Handling:** PyMuPDF / PDFMiner

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/TalentSphere-AI.git](https://github.com/yourusername/TalentSphere-AI.git)
    cd TalentSphere-AI
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download Spacy NLP Model**
    You must download the English language model for the parser to work:
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Run the App**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure
TalentSphere-AI/ ├── app.py # Main Streamlit Dashboard application ├── parser_engine.py # Core logic for extracting text & skills ├── resume_loader.py # PDF text extraction utility ├── db_handler.py # SQLite database operations (Login/Register) ├── skills_db.py # Database of 500+ technical keywords ├── requirements.txt # List of python dependencies └── README.md # Project documentation


## 🔮 Future Enhancements
* Integration with OpenAI GPT-4 for deeper semantic analysis.
* Support for image-based resumes using OCR (Tesseract).
* Direct email integration for scheduling interviews.

---
*Developed by Keerthana S*
