from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)   # extracted experience
    education = models.TextField(null=True, blank=True)    # extracted education
    parsed_json = models.JSONField(null=True, blank=True)  # structured parse output
    created_at = models.DateTimeField(auto_now_add=True)

      # 👉 ADD THIS METHOD HERE
    def highlighted_preview(self):
        if not self.extracted_text:
            return ""
        words = self.extracted_text.split()[:20]
        return " ".join(words) + "..."

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

# New model for Applications
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} applied for resume {self.resume.file.name}"
    
    from django.db import models
from django.contrib.auth.models import User

class OptimizationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Optimization Request #{self.id}"

from django.db import models
from django.contrib.auth.models import User

class ResumeBuilder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    summary = models.TextField()
    skills = models.TextField()
    experience = models.TextField()
    education = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume - {self.user.username}"

class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cover Letter - {self.user.username}"
