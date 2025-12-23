import re
import spacy
from spacy.matcher import PhraseMatcher
from resume_loader import extract_text_from_pdf
from skills_db import SKILLS_DB

# --- CONFIG ---
ACTION_VERBS = ["developed", "led", "analyzed", "architected", "created", "designed", "implemented", "optimized", "managed", "deployed", "spearheaded"]

class ResumeParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_text = ""
        self.parsed_data = {
            "contact_info": {}, "skills_found": [], "missing_keywords": [],
            "auto_extracted_skills": [], "match_score": 0, 
            "years_experience": 0,
            "audit_report": {}, "interview_questions": [], "learning_roadmap": []
        }
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.matcher = PhraseMatcher(self.nlp.vocab)
            patterns = [self.nlp.make_doc(text) for text in SKILLS_DB]
            self.matcher.add("TECH_SKILLS", patterns)
        except:
            pass
            
        self._load_content()

    def _load_content(self):
        try:
            self.raw_text = extract_text_from_pdf(self.file_path)
            self.raw_text = " ".join(self.raw_text.split()) 
        except:
            self.raw_text = ""

    def extract_contact_details(self):
        text = self.raw_text
        
        # 1. Email Extraction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email = re.search(email_pattern, text)
        
        # 2. Phone Extraction (Integrated from parse_basic.py)
        # Matches: +91 9876543210, 987-654-3210, (123) 456-7890
        phone_pattern = r'(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        
        valid_phone = "Not Found"
        for p in phones:
            digits = re.sub(r'\D', '', p) # Clean non-digits
            if 10 <= len(digits) <= 15:   # Standard validation
                valid_phone = p
                break

        self.parsed_data["contact_info"] = {
            "email": email.group() if email else "Not Found",
            "phone": valid_phone
        }

    def extract_experience(self):
        text = self.raw_text.lower()
        pattern = r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)'
        matches = re.findall(pattern, text)
        if matches:
            try:
                exp = max([float(x) for x in matches])
                self.parsed_data["years_experience"] = exp
            except:
                self.parsed_data["years_experience"] = 0

    def auto_extract_skills(self):
        if not self.raw_text: return
        doc = self.nlp(self.raw_text)
        matches = self.matcher(doc)
        found = set()
        for match_id, start, end in matches:
            found.add(doc[start:end].text)
        self.parsed_data["auto_extracted_skills"] = list(found)

    def match_keywords(self, target_keywords):
        text_lower = self.raw_text.lower()
        found = []
        missing = []
        for kw in target_keywords:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_lower):
                found.append(kw)
            else:
                missing.append(kw)

        self.parsed_data["skills_found"] = found
        self.parsed_data["missing_keywords"] = missing
        
        if target_keywords:
            self.parsed_data["match_score"] = round((len(found) / len(target_keywords)) * 100, 2)
        else:
            self.parsed_data["match_score"] = 0

    def audit_resume(self):
        text_lower = self.raw_text.lower()
        audit = {"suggestions": [], "score": 100}
        
        action_count = len([v for v in ACTION_VERBS if v in text_lower])
        if action_count < 3:
            audit["suggestions"].append("⚠️ **Weak Impact:** Your resume lacks strong action verbs (e.g., Led, Developed).")
            audit["score"] -= 15
        
        if "education" not in text_lower:
            audit["suggestions"].append("⚠️ **Structure:** 'Education' section not clearly detected.")
            audit["score"] -= 10
        if "experience" not in text_lower and "projects" not in text_lower:
            audit["suggestions"].append("⚠️ **Structure:** 'Experience' or 'Projects' section missing.")
            audit["score"] -= 10
            
        if "linkedin.com" not in text_lower:
            audit["suggestions"].append("⚠️ **Credibility:** Add a LinkedIn profile link.")
            audit["score"] -= 5
            
        self.parsed_data["audit_report"] = audit

    def generate_interview_questions(self):
        q_bank = {
            "Python": "Explain the Global Interpreter Lock (GIL).",
            "SQL": "Difference between TRUNCATE and DELETE?",
            "React": "Explain 'Lifting State Up' and useEffect.",
            "AWS": "Difference between S3, EBS, and EFS?",
            "Docker": "Difference between Image and Container?"
        }
        questions = []
        for skill in self.parsed_data["skills_found"]:
            if skill in q_bank:
                questions.append(f"**{skill}:** {q_bank[skill]}")
        
        if len(questions) < 5: 
            questions.append("Describe a challenging technical bug you solved.")
            questions.append("How do you handle tight deadlines?")
            
        self.parsed_data["interview_questions"] = questions[:5]

    def generate_roadmap(self):
        roadmap = []
        for skill in self.parsed_data["missing_keywords"]:
            link = f"https://www.coursera.org/search?query={skill}"
            roadmap.append(f"**Learn {skill}:** [View Courses]({link})")
        self.parsed_data["learning_roadmap"] = roadmap