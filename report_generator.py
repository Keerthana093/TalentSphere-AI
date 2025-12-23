from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'TalentSphere AI - Analysis Report', 0, 1, 'C')
        self.ln(10)

def generate_report(filename, name, score, missing, roadmap):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, f"Candidate: {name}", ln=True)
    pdf.cell(0, 10, f"File: {filename}", ln=True)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Match Score: {score}%", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, "Missing Skills:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    
    if missing:
        for m in missing: pdf.cell(0, 8, f"- {m}", ln=True)
    else:
        pdf.cell(0, 8, "None - Perfect Match!", ln=True)
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Learning Roadmap:", ln=True)
    pdf.set_font("Arial", size=11)
    for r in roadmap:
        clean = r.split("]")[0].replace("[", "").replace("**", "") 
        pdf.cell(0, 8, f"- {clean}", ln=True)

    outfile = f"Report_{name.split('@')[0] if '@' in name else 'User'}.pdf"
    pdf.output(outfile)
    return outfile