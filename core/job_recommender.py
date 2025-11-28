# core/job_recommender.py
from sentence_transformers import SentenceTransformer, util
import numpy as np

# load model once
MODEL = None
def get_model(name="all-MiniLM-L6-v2"):
    global MODEL
    if MODEL is None:
        MODEL = SentenceTransformer(name)
    return MODEL

# job database (example). In production store in DB.
JOBS = [
    {"id":1, "title":"Python Backend Developer", "desc":"python django flask backend aws docker sql"},
    {"id":2, "title":"Frontend React Developer", "desc":"javascript react html css redux"},
    {"id":3, "title":"Data Scientist (NLP)", "desc":"python pandas numpy sklearn transformers nlp"},
    {"id":4, "title":"DevOps Engineer", "desc":"docker kubernetes aws terraform ci/cd monitoring"}
]

def bert_recommend_jobs(skills_list, top_k=5):
    model = get_model()
    if not skills_list:
        user_emb = model.encode([""], convert_to_tensor=True)
    else:
        user_text = " ".join(skills_list)
        user_emb = model.encode([user_text], convert_to_tensor=True)

    results = []
    for j in JOBS:
        job_emb = model.encode([j["desc"]], convert_to_tensor=True)
        score = float(util.cos_sim(user_emb, job_emb)[0][0])
        results.append({"id": j["id"], "title": j["title"], "score": round(score*100,2)})
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]
