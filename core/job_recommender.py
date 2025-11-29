# core/job_recommender.py
# --------------------------------------------------------
# Render-SAFE Job Recommendation (No PyTorch / Transformers)
# --------------------------------------------------------

import numpy as np

# Tiny job database (same as before)
JOBS = [
    {"id": 1, "title": "Python Backend Developer", 
     "desc": "python django flask backend aws docker sql"},

    {"id": 2, "title": "Frontend React Developer", 
     "desc": "javascript react html css redux"},

    {"id": 3, "title": "Data Scientist (NLP)", 
     "desc": "python pandas numpy sklearn transformers nlp"},

    {"id": 4, "title": "DevOps Engineer", 
     "desc": "docker kubernetes aws terraform ci/cd monitoring"},
]


# Very lightweight similarity scoring (Jaccard index)
def simple_similarity(user_skills, job_desc):
    user = set(s.lower() for s in user_skills)
    job = set(job_desc.lower().split())

    if not user:
        return 0.0

    # Jaccard similarity
    intersection = len(user & job)
    union = len(user | job)
    return intersection / union if union > 0 else 0


# MAIN FUNCTION — same signature as before
def bert_recommend_jobs(skills_list, top_k=5):
    results = []

    for job in JOBS:
        score = simple_similarity(skills_list, job["desc"])
        results.append({
            "id": job["id"],
            "title": job["title"],
            "desc": job["desc"],
            "score": round(score * 100, 2)
        })

    # sort high → low
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:top_k]
