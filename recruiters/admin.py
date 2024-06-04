from django.contrib import admin

from recruiters.models import Recruiter, Question, Category, JobPost, Applied \
        ,Application, Interview,Answer

# Register your models here.

admin.site.register(Recruiter)
admin.site.register(Question)
admin.site.register(Category)
admin.site.register(JobPost)
admin.site.register(Applied)
admin.site.register(Application)
admin.site.register(Interview)
admin.site.register(Answer)
