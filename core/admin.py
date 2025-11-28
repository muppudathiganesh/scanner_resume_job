from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file", "created_at")
    search_fields = ("user__username", "file", "skills")
    readonly_fields = ("extracted_text","skills","experience","education","parsed_json")
    list_filter = ("created_at",)
