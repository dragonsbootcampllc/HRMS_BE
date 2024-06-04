from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from applicants.models import Applicant
from recruiters.models import JobPost, Application, Applied , Answer,Question

from recruiters import serializers as Recruiter_serializers
from applicants import serializers as Applicant_serializers

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions

from django.db import transaction
# Create your views here.



# create Applicant 
class GetCreateApplicant(generics.CreateAPIView,generics.ListAPIView):
    queryset = Applicant.objects.all()
    serializer_class = Applicant_serializers.ApplicantSerializer

# apply for a posted job
class ApplyJob(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        applicant = get_object_or_404(Applicant,pk=data['user_id'])

        job_id = self.kwargs.get('job_id')
        try:
            job = get_object_or_404(JobPost,id=job_id)
        except JobPost.DoesNotExist:
            raise Http404("Job does not exist")
        
        applied = Applied.objects.filter(applicant=applicant, jobPost=job)
        if applied.exists():
            return Response({"message": "You have already applied for this job"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if job.is_application:
                application = data.get('application')
                
                if application is not None:
                    # questions for the application 
                    questions = Question.objects.filter(application=job.application)
                    ids = list(questions.values_list('id', flat=True))
                    with transaction.atomic():
                        applied = Applied.objects.create(applicant=applicant, jobPost=job)
                        for question_id, answer in application.items():
                            if int(question_id) in ids:
                                question = get_object_or_404(Question, id=question_id)
                                answer = Answer.objects.create(question=question,answer=answer,applied=applied)
                            else:
                                return Response({"message": "An error has oocured"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Application is required"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                data['application'] = None
            return Response({"message": "Applied successfully"}, status=status.HTTP_201_CREATED)
    

# show all the jobs
class ShowJobs(generics.ListAPIView, mixins.RetrieveModelMixin):
    queryset = JobPost.objects.all()
    serializer_class = Recruiter_serializers.JobPostSerializer


# show all applied jobs
class ShowAppliedJobs(generics.ListAPIView, mixins.RetrieveModelMixin):
    queryset = Applied.objects.all()
    serializer_class = Recruiter_serializers.AppliedSerializer

    def get(self, request, *args, **kwargs):
        applicant = get_object_or_404(Applicant,pk=request.data.get('user_id'))
        applied_jobs = self.filter_queryset(self.get_queryset().filter(applicant=applicant))
        serializer = self.get_serializer(applied_jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
