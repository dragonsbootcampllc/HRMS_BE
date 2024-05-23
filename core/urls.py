from django.contrib import admin
from django.urls import path, include
from oauth2_provider.views import TokenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/recruiter/', include('recruiters.urls')),
    path('api/applicant/', include('applicants.urls')),
]
