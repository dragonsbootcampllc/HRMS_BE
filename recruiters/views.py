from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from recruiters.models import Recruiter, Question, Category, JobPost, Applied \
        ,Application, Interview,Application
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from recruiters import serializers
from applicants import serializers as aplicantSerializers
from rest_framework import generics
from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

import core.Utils as Utils

# Create your views here.

# post a job 
class GetCreatePostJob(generics.GenericAPIView, mixins.CreateModelMixin, mixins.ListModelMixin):
    serializer_class = serializers.JobPostSerializer

    def post(self, request, *args, **kwargs):
        # Extract recruiter_id from request data
        data = request.data.copy()

        recruiter_id = data['recruiter']

        try:
            # Check if the Recruiter with the given ID exists
            recruiter = get_object_or_404(Recruiter, pk=recruiter_id)
        except Recruiter.DoesNotExist:
            return Response({"recruiter_id": ["Recruiter with the given ID does not exist."]}, status=status.HTTP_400_BAD_REQUEST)

        if data['is_application'] :
            try:
                if data['application'] is None or data['application'] == []:
                    raise NotFound("ther is no applications")
            except KeyError as e:
                return Response({"application": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            
            app = Application.objects.create(recruiter=recruiter)

            for ques in data['application']:
                question = Question.objects.create(question=ques,application=app)

            data['application'] = app.id
        else:
            data['application'] = None
        
        data['recruiter'] = recruiter_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        recruiter = get_object_or_404(Recruiter, pk=self.request.data['recruiter_id'])
        return JobPost.objects.filter(recruiter=recruiter)

    def get(self, request):
        return self.list(request)
    
class GetJobInterviews(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.InterviewSerializer

    def get_queryset(self):
        recruiter_id = self.request.data.get('recruiter_id')
        job_id = self.kwargs['job_id']
        get_object_or_404(Recruiter, pk=recruiter_id)
        get_object_or_404(JobPost, pk=job_id)
        return Interview.objects.filter(applied__jobPost=job_id)

    def get(self, request,job_id):
        return self.list(request,job_id)
    
# show all the applicants for a job
class ShowApplicants(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = aplicantSerializers.ApplicantSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        job_post = get_object_or_404(JobPost, pk=pk)
        return Applied.objects.filter(jobPost=job_post)

    def get(self, request, pk):
        return self.list(request, pk)
    
    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        applicants = []
        for d in data:
            applicants.append(self.serializer_class(d.applicant).data)

        return Response(applicants, status=status.HTTP_200_OK)
    
# approve an applicant
class UpdateApplicantStats(generics.UpdateAPIView):
    serializer_class = serializers.AppliedSerializer
    queryset = Applied.objects.all()
    
    def partial_update(self, request, *args, **kwargs):
        applied = self.get_object()
        data = request.data.copy()
        if data.get('approved') is None:
            return Response({"approved": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        applied.approved = data['approved']
        serializer = self.get_serializer(applied, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        result = dict({
            'approved': applied.approved,
            'message': f"stats updated successfully to {data['approved']}",
        })
        return Response(result, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

# schedule an interview
class ScheduleInterview(generics.CreateAPIView,generics.UpdateAPIView):
    serializer_class = serializers.InterviewSerializer
    queryset = Interview.objects.all()

    def get_object(self):
        return Interview.objects.filter(applied=self.kwargs['applied_id']).first()

    def post(self, request, applied_id):
        recruiter = get_object_or_404(Recruiter, pk=self.request.data['recruiter_id'])
        applied_job = get_object_or_404(Applied, pk=applied_id)

        data = self.request.data.copy()
        if Interview.objects.filter(applied=applied_job).exists():
            return Response({"message": ["Interview already scheduled for this applicant"]}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if data['date'] is None:
                raise NotFound("This field is required.")
        except NotFound as e:
            return Response({"date": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        data['applied'] = applied_job.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        return self.create(serializer)
    
    def partial_update(self, request,applied_id):
        interview = self.get_object()
        data = request.data.copy()

        if not isinstance(interview, Interview):
            return Response({"message": ["Interview not found"]}, status=status.HTTP_404_NOT_FOUND)
        
        if data.get('date') is not None:
            if interview.date == Utils.parse_datetime_with_utc_timezone(data.get('date')):
                return Response({"message": ["Interview already scheduled for this date"]}, status=status.HTTP_400_BAD_REQUEST) 
            interview.date = data.get('date')

        if data.get('cancelled') is not None:
            interview.cancelled = data['cancelled']

        serializer = self.get_serializer(interview, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        result = dict({
            'message': [],
        })
        if data.get('date') is not None:
            result['date'] = interview.date
            result['message'].append(f"Interview scheduled successfully to {Utils.parse_datetime_with_utc_timezone(data.get('date'))}")

        if data.get('cancelled') is not None:
            result['cancelled'] = interview.cancelled
            result['message'].append(f"Interview cancelled successfully")

        # TODO: Handle no body fileds 
        return Response(result, status=status.HTTP_200_OK)
    def perform_update(self, serializer):
        instance = serializer.instance
        serializer.save()
        return instance
    
# show all the interviews of job applied to a recruiter
class ShowInterviews(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.InterviewSerializer
    queryset = Interview.objects.all()

    # get all interviews 
    def get(self, request):
        return self.list(request)

class GetAllInterviews(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.InterviewSerializer
    queryset = Interview.objects.all()

    # get all interviews 
    def get(self, request):
        return self.list(request)
    
# show all the questions
class ShowQuestions(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.QuestionSerializer
    queryset = Question.objects.all()
    def get(self, request):
        return self.list(request)
    def list(self, request, *args, **kwargs):
        data = Question.objects.all()
        showingData = [q.question for q in data]
        showingData = list(set(showingData))
        print(showingData)
        return Response(showingData,status=status.HTTP_200_OK)
    

# CRUD methods

# get all django users
class GetUsers(generics.ListAPIView):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    
class GetUesr(generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#get categories & add category
class GetCreateCategory(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return Category.objects.all()

    def get(self, request):
        return self.list(request)
    def post(self, request):
        return self.create(request)

    
# show all recruiters 
class GetCreateRecruiters(generics.GenericAPIView, mixins.CreateModelMixin, mixins.ListModelMixin ):
    serializer_class = serializers.RecruiterSerializer

    def get_queryset(self):
        return Recruiter.objects.all()

    def get(self, request):
        return self.list(request)
    
    def post(self, request):
        return self.create(request)