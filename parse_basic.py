import re
import json
from typing import List, Dict, Union
from resume_loader import extract_text_from_pdf

class ResumeParser:
    """
    The Core Engine. 
    It takes raw text and user inputs (Keywords, Job Description) 
    to extract insights and score the resume.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_text = ""
        self.parsed_data = {
            "contact_info": {},
            "skills_found": [],
            "missing_keywords": [],
            "match_score": 0,
            "summary": ""
        }
        
        # Load text immediately upon creation
        self._load_content()

    def _load_content(self):
        """Internal method to load text using our Phase 1 tool."""
        try:
            # We reuse the robust loader we built in Phase 1
            self.raw_text = extract_text_from_pdf(self.file_path)
            # Basic cleaning to make regex easier (remove multiple spaces)
            self.raw_text = " ".join(self.raw_text.split()) 
        except Exception as e:
            print(f"Error initializing parser: {e}")

    def extract_contact_details(self):
        """Robust Regex for Email and Phone."""
        text = self.raw_text
        
        # 1. Email: Standard Pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email = re.search(email_pattern, text)
        
        # 2. Phone: Broad pattern to catch +91, dashes, spaces
        # Looks for 10-15 digits mixed with common separators
        phone_pattern = r'(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        
        # Phone Filter: Remove false positives (like dates "2023-2024")
        valid_phone = None
        for p in phones:
            digits_only = re.sub(r'\D', '', p) # Remove non-digits
            if 10 <= len(digits_only) <= 15:
                valid_phone = p
                break

        self.parsed_data["contact_info"] = {
            "email": email.group() if email else "Not Found",
            "phone": valid_phone if valid_phone else "Not Found"
        }

    def match_keywords(self, target_keywords: List[str]):
        """
        The Feature you requested: 
        Analyze resume based on User Inputs (Keywords).
        """
        text_lower = self.raw_text.lower()
        found = []
        missing = []

        for keyword in target_keywords:
            # We look for the keyword as a distinct word (boundaried)
            # This prevents finding "Java" inside "JavaScript"
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found.append(keyword)
            else:
                missing.append(keyword)

        self.parsed_data["skills_found"] = found
        self.parsed_data["missing_keywords"] = missing
        
        # Calculate a simple Score
        if target_keywords:
            score = (len(found) / len(target_keywords)) * 100
            self.parsed_data["match_score"] = round(score, 2)

    def get_json_output(self):
        """Returns the final structured data for the frontend."""
        return json.dumps(self.parsed_data, indent=4)

# --- PROFESSIONAL TESTING BLOCK ---
if __name__ == "__main__":
    # 1. Simulate User Input (In the future, this comes from the Website UI)
    user_file = "KeerthanaS_resume.pdf"
    user_required_skills = ["Python", "SQL", "Machine Learning", "Communication", "React"] # The user wants to hire for these
    
    print(f"--- Processing: {user_file} ---")
    
    # 2. Initialize the Engine
    parser = ResumeParser(user_file)
    
    if parser.raw_text:
        # 3. Run the Extractions
        parser.extract_contact_details()
        parser.match_keywords(user_required_skills)
        
        # 4. View Results
        print("--- FINAL ANALYSIS ---")
        print(parser.get_json_output())
    else:
        print("Failed to read the resume text.")