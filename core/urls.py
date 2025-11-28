from django.urls import path
from . import views

urlpatterns = [
    # path("", views.dashboard, name="home"),  # User dashboard as homepage
    path("register/", views.register, name="register"),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("upload/", views.upload_resume, name="upload"),
    path("resume/<int:pk>/", views.resume_detail, name="resume_detail"),
    path("resume/<int:pk>/download/", views.resume_download, name="resume_download"),
    path("resume/<int:resume_id>/apply/", views.apply_resume, name="apply_resume"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path('export/<int:resume_id>/', views.export_pdf, name='export_pdf'),

    path('optimize/', views.optimize_resume, name='optimize_resume'),
    path('optimize-review/', views.optimize_review, name='optimize_review'),

    path("resume-builder/", views.resume_builder, name="resume_builder"),
    path("cover-letter-builder/", views.cover_letter_builder, name="cover_letter_builder"),
    path("resume-preview/<int:id>/", views.resume_preview, name="resume_preview"),
    path("cover-letter-preview/<int:id>/", views.cover_letter_preview, name="cover_letter_preview"),

  

path("download-resume/<int:id>/", views.download_resume_pdf, name="download_resume"),



]
