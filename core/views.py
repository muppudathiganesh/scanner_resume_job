from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm, UploadForm
from .models import Resume

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect("admin_dashboard")
            else:
                return redirect("dashboard")  # ✅ user goes to dashboard
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


# Registration
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})



# Logout
def logout_view(request):
    logout(request)
    return redirect("login")

# User dashboard (resume history)
@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user).order_by("-created_at")
    
    # Prepare skills list for each resume
    for r in resumes:
        r.skills_list = r.skills.split(",") if r.skills else []
    
    return render(request, "dashboard.html", {"resumes": resumes})

# Upload resume (user)
@login_required
def upload_resume(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            return redirect("dashboard")
    else:
        form = UploadForm()
    return render(request, "upload.html", {"form": form})

# Admin dashboard (view all resumes)
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    resumes = Resume.objects.all().order_by("-created_at")
    return render(request, "admin_dashboard.html", {"resumes": resumes})




from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from .models import Resume

def resume_download(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    if resume.user != request.user and not request.user.is_staff:
        return HttpResponse("Access denied", status=403)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    # ... your PDF generation code ...
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"parsed_{resume.id}.pdf")
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Resume

def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    if resume.user != request.user and not request.user.is_staff:
        return HttpResponse("Access denied", status=403)

    # Split the skills into a list
    skills_list = resume.skills.split(",") if resume.skills else []

    return render(request, "resume_detail.html", {
        "resume": resume,
        "skills_list": skills_list
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Resume, Application
from .forms import ApplyForm
from django.core.mail import send_mail
from django.conf import settings

@login_required
def apply_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == "POST":
        form = ApplyForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.resume = resume
            application.save()

            # Send email to admin
            send_mail(
                subject=f"New Application from {request.user.username}",
                message=f"Resume: {resume.file.url}\nName: {application.full_name}\nEmail: {application.email}\nPhone: {application.phone}\nCover Letter:\n{application.cover_letter}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            return redirect("dashboard")
    else:
        form = ApplyForm(initial={
            "full_name": request.user.get_full_name(),
            "email": request.user.email,
        })

    return render(request, "apply_resume.html", {"form": form, "resume": resume})


# from core.job_recommender import bert_recommend_jobs
# from .resume_parser import analyze_resume

# @login_required
# def upload_resume(request):
#     if request.method == "POST":
#         form = UploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             resume = form.save(commit=False)
#             resume.user = request.user
#             resume.save()

#             # 1️⃣ Parse resume text + skills
#             extracted_text, skills = analyze_resume(resume.file)

#             # 2️⃣ Save the extracted data
#             resume.extracted_text = extracted_text
#             resume.skills = ",".join(skills)
#             resume.save()

#             # 3️⃣ Calculate Match Rate (Simple: skills found / total known skills)
#             TOTAL_SKILLS = 50  # replace with your actual list count
#             found = len(skills)
#             match_rate = int((found / TOTAL_SKILLS) * 100) if TOTAL_SKILLS > 0 else 0
#             match_rate = max(0, min(match_rate, 100))

#             # 4️⃣ AI Job Recommendations
#             jobs = bert_recommend_jobs(skills)

#             # 5️⃣ Send everything to template
#             return render(request, "result.html", {
#                 "skills": skills,
#                 "jobs": jobs,
#                 "match_rate": match_rate,
#             })
#     else:
#         form = UploadForm()

#     return render(request, "upload.html", {"form": form})
# imports at top of views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UploadForm
from .models import Resume
from .resume_parser import analyze_resume, SKILLS as MASTER_SKILLS
from core.job_recommender import bert_recommend_jobs
from django.http import HttpResponse

# simple helper: create an AI summary (placeholder)
def summarize_text(text, max_chars=600):
    if not text:
        return "No text extracted to summarize."
    # simple heuristic: return first 600 chars + ellipsis
    return (text.strip()[:max_chars] + '...') if len(text) > max_chars else text.strip()

# strengths/weaknesses detection (very basic heuristic)
def detect_strengths_weaknesses(skills_list):
    strengths = []
    weaknesses = []
    # mark strong if key infra skills present
    infra = {"aws","docker","kubernetes","terraform","ci/cd"}
    ml = {"pandas","numpy","sklearn","transformers"}
    if any(s in skills_list for s in infra):
        strengths.append("Has infrastructure / DevOps skills")
    if any(s in skills_list for s in ml):
        strengths.append("Has data / ML related skills")
    # weaknesses: if few skills present or missing core languages
    core = {"python","javascript","java"}
    if not any(s in skills_list for s in core):
        weaknesses.append("Missing core programming language (python/javascript/java)")
    if len(skills_list) < 3:
        weaknesses.append("Very few skills detected; consider adding more details")
    return strengths, weaknesses

# missing skills suggestion from a job set (compare recommended job desc)
def suggest_missing_skills(skills_list, job_recs, max_suggestions=6):
    # collect all skills from top job descriptions (JOBS descriptions in recommender)
    required = set()
    for j in job_recs:
        # job desc text likely in jobs from recommender as job description string or pre-specified keys
        # if your recommender returns desc, use it. Else use a static list fallback.
        desc = j.get("desc", "")
        required.update(desc.split())
    # filter required for simple SKILLS master list
    required = {r for r in required if r in MASTER_SKILLS}
    missing = list(required - set(skills_list))
    return missing[:max_suggestions]

# ATS breakdown: very simple heuristic
def compute_ats_breakdown(text, skills_list):
    # score out of 100 each category
    # Education: check for keywords
    edu_keywords = ["bachelor", "master", "mba", "phd", "university", "college"]
    edu = 60 if any(k in (text or "").lower() for k in edu_keywords) else 30
    exp = 40 + min(40, len(skills_list) * 4)  # more skills -> more experience score
    skills_score = min(100, len(skills_list) * 8)
    formatting = 80 if len((text or "").splitlines()) > 5 else 50
    return {
        "Education": int(edu),
        "Experience": int(min(100, exp)),
        "Skills": int(skills_score),
        "Formatting": int(formatting)
    }

# helper to build chart data: e.g. present vs missing counts or category values
def build_chart_from_ats(ats_breakdown):
    labels = list(ats_breakdown.keys())
    values = [ats_breakdown[k] for k in labels]
    return labels, values

# main upload view
@login_required
def upload_resume(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            # analyze
            extracted_text, skills = analyze_resume(resume.file)  # skills = list
            resume.extracted_text = extracted_text
            resume.skills = ",".join(skills)
            resume.save()

            # job recommendations
            jobs = bert_recommend_jobs(skills)
            # ensure jobs have 'score' numeric and optional 'desc'
            for j in jobs:
                j.setdefault("score", 0)
                j.setdefault("desc", "")

            # AI summary
            ai_summary = summarize_text(extracted_text)

            # strengths/weaknesses
            strengths, weaknesses = detect_strengths_weaknesses(skills)

            # missing skills suggestion
            missing = suggest_missing_skills(skills, jobs)

            # ATS breakdown
            ats = compute_ats_breakdown(extracted_text, skills)

            # match rate = simple avg of ATS categories or skills coverage
            match_rate = int(sum(ats.values()) / max(1, len(ats)))

            # chart data
            chart_labels, chart_values = build_chart_from_ats(ats)

            return render(request, "result.html", {
                "resume_id": resume.id,
                "skills": skills,
                "jobs": jobs,
                "ai_summary": ai_summary,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "missing_skills": missing,
                "ats_breakdown": ats,
                "match_rate": match_rate,
                "chart_labels": chart_labels,
                "chart_values": chart_values,
            })
    else:
        form = UploadForm()
    return render(request, "upload.html", {"form": form})
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@login_required
def export_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.user != request.user and not request.user.is_staff:
        return HttpResponse("Access denied", status=403)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, h-60, f"Resume Analysis - {resume.user.username}")

    # Match rate
    mr = request.GET.get("match_rate")
    p.setFont("Helvetica", 12)
    p.drawString(40, h-90, f"Match Rate: {mr if mr else 'N/A'}%")

    # Skills (first 200 chars of text)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, h-120, "Skills:")
    p.setFont("Helvetica", 10)
    skills = resume.skills or ""
    p.drawString(90, h-120, skills[:200])

    # Summary (extracted_text snippet)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, h-150, "Summary:")
    p.setFont("Helvetica", 10)
    text = (resume.extracted_text or "")[:600]
    # draw wrapped text
    x = 40
    y = h - 170
    max_width = w - 80
    for line in text.splitlines():
        # naive wrap
        while line:
            chunk = line[:100]
            p.drawString(x, y, chunk)
            line = line[100:]
            y -= 12
            if y < 50:
                p.showPage()
                y = h - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"analysis_{resume.id}.pdf")



from django.shortcuts import render

def optimize_resume(request):
    return render(request, "optimize_resume.html")

from django.shortcuts import render, redirect
from .models import Resume   # if you already store resumes

def optimize_review(request):
    # Resume stored after upload?
    uploaded_resume = Resume.objects.last()  # or fetch by user

    tips = [
        "Use action words like 'Developed', 'Implemented', 'Improved'.",
        "Keep your resume to one page if experience is less than 5 years.",
        "Highlight measurable achievements (numbers speak louder).",
        "Customize resume for each job using specific keywords.",
        "Avoid long paragraphs — recruiters scan resumes in 6 seconds."
    ]

    motivation = [
        "You’re closer than you think — a few improvements can boost your chances massively!",
        "Every successful career begins with a polished resume — you're on the right track.",
        "Small changes create big opportunities. Keep improving!",
        "Your skills are valuable — let's present them in the best possible way."
    ]

    import random
    return render(request, "optimize_review.html", {
        "resume": uploaded_resume,
        "tips": tips,
        "motivation": random.choice(motivation)
    })
   


from django.shortcuts import render, redirect, get_object_or_404
from .models import ResumeBuilder, CoverLetter
from django.contrib.auth.decorators import login_required

@login_required
def resume_builder(request):
    if request.method == "POST":
        resume = ResumeBuilder.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            summary=request.POST.get("summary"),
            skills=request.POST.get("skills"),
            experience=request.POST.get("experience"),
            education=request.POST.get("education"),
        )
        return redirect("resume_preview", id=resume.id)

    return render(request, "resume_builder.html")


@login_required
def cover_letter_builder(request):
    if request.method == "POST":
        letter = CoverLetter.objects.create(
            user=request.user,
            job_role=request.POST.get("job_role"),
            company_name=request.POST.get("company_name"),
            content=request.POST.get("content"),
        )
        return redirect("cover_letter_preview", id=letter.id)

    return render(request, "cover_letter_builder.html")


@login_required
def resume_preview(request, id):
    resume = get_object_or_404(ResumeBuilder, id=id)
    return render(request, "resume_preview.html", {"resume": resume})


@login_required
def cover_letter_preview(request, id):
    letter = get_object_or_404(CoverLetter, id=id)
    return render(request, "cover_letter_preview.html", {"letter": letter})



from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from .models import ResumeBuilder  # assuming you have this model



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ResumeBuilder

from django.conf import settings








def download_resume_pdf(request, id):
    resume = ResumeBuilder.objects.get(id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_resume.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph(f"<b>{resume.full_name}</b>", styles["Title"]),
        Paragraph(f"Email: {resume.email}", styles["Normal"]),
        Paragraph(f"Phone: {resume.phone}", styles["Normal"]),
        Paragraph("<br/><b>Summary</b>", styles["Heading2"]),
        Paragraph(resume.summary, styles["Normal"]),
        Paragraph("<br/><b>Skills</b>", styles["Heading2"]),
        Paragraph(resume.skills, styles["Normal"]),
        Paragraph("<br/><b>Experience</b>", styles["Heading2"]),
        Paragraph(resume.experience, styles["Normal"]),
        Paragraph("<br/><b>Education</b>", styles["Heading2"]),
        Paragraph(resume.education, styles["Normal"]),
    ]

    doc.build(elements)
    return response

