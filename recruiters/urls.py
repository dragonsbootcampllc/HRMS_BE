from django.urls import path
from recruiters import views


urlpatterns = [
    path('',view=views.GetCreateRecruiters.as_view()),                                     # show all recruiters & create a new recruiter
    path('job',view=views.GetCreatePostJob.as_view()),                                     # show all jobs & post a job 
    path('job/<int:job_id>/interviews',view=views.GetJobInterviews.as_view()),             # show all jobs & post a job 
    
    path('job/<int:pk>/applicant',view=views.ShowApplicants.as_view()),                    # show all applicants for a job
    path('job/applied/<int:pk>/applicant',view=views.UpdateApplicantStats.as_view()),      # approve an applicant

    path('interview/schedule/<int:applied_id>',view=views.ScheduleInterview.as_view()),    # schedule an interview
    path('interview/<int:pk>',view=views.ShowInterviews.as_view()),                        # show Interviews with job_id
    path('interview/',view=views.GetAllInterviews.as_view()),                              # show Interviews with job_id

    path('category',view=views.GetCreateCategory.as_view()),                               # show all categories & create a new category
    path('question',view=views.ShowQuestions.as_view()),                                   # show all questions
    # path('user/<int:pk>',view=views.GetUesr.as_view()),
    # path('user/',view=views.GetUsers.as_view()),
    # path('createApplication/',view=views.CreateApplication.as_view()),
    # path('createQuestion/',view=views.CreateQuestion.as_view()),
]