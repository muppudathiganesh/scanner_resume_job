# core/parse_utils.py
import re
import spacy
nlp = spacy.load("en_core_web_sm")

EDU_KEYWORDS = [
    "bachelor", "master", "b.sc", "btech", "b.e.", "mba", "phd", "msc", "bs", "ms", "degree", "college", "university"
]

EXP_KEYWORDS = [
    "experience", "worked", "responsibilities", "projects", "intern", "engineer", "developer", "manager", "lead"
]

def split_sections(text):
    # naive split by common headings
    headings = re.split(r'\n{2,}', text)
    return [h.strip() for h in headings if h.strip()]

def extract_education(text):
    matches = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        l = line.lower()
        if any(k in l for k in EDU_KEYWORDS) or re.search(r'\b\d{4}\b', l) and ("university" in l or "college" in l):
            context = " ".join(lines[max(0,i-2):i+3])
            matches.append(context.strip())
    return list(dict.fromkeys(matches))  # uniq preserve order

def extract_experience(text):
    # Use spaCy to find ORG, DATE, and VERB-derived sentences
    doc = nlp(text)
    experiences = []
    sentences = list(doc.sents)
    for sent in sentences:
        s = sent.text.strip()
        low = s.lower()
        if any(k in low for k in EXP_KEYWORDS) or len(s.split()) > 8 and any(ent.label_ == "ORG" for ent in sent.ents):
            experiences.append(s)
    # fallback: search paragraphs with years
    if not experiences:
        paragraphs = split_sections(text)
        for p in paragraphs:
            if re.search(r'\b(19|20)\d{2}\b', p):
                experiences.append(p.strip())
    return list(dict.fromkeys(experiences))

def extract_skills_list(text, skill_vocab):
    text_l = text.lower()
    found = [s for s in skill_vocab if s in text_l]
    return found

def full_parse(text, skill_vocab):
    skills = extract_skills_list(text, skill_vocab)
    experience = extract_experience(text)
    education = extract_education(text)
    return {
        "skills": skills,
        "experience": experience,
        "education": education
    }
