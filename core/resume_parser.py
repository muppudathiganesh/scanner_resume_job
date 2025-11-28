import PyPDF2
import docx
import io

SKILLS = [
    "python","java","javascript","django","flask","react","node",
    "html","css","sql","mysql","postgres","aws","docker",
    "git","pandas","numpy","sklearn"
]

def extract_text(file_obj):
    filename = file_obj.name.lower()
    content = file_obj.read()

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        txt = ""
        for page in reader.pages:
            if page.extract_text():
                txt += page.extract_text()
        return txt.lower()

    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs).lower()

    return content.decode("utf-8", errors="ignore").lower()


def extract_skills(text):
    return [s for s in SKILLS if s in text]

# Main function to analyze a resume file
def analyze_resume(file_obj):
    text = extract_text(file_obj)
    skills = extract_skills(text)
    return text, skills