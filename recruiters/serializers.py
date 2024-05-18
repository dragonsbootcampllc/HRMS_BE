from rest_framework import serializers
from django.contrib.auth.models import Group, User

from recruiters.models import Recruiter, Question, Application, Category, JobPost, Applied, Interview
from recruiters.models import JobPost, Application

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'user_role_id', 'user_dob', 'user_address', 'user_role']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        instance.user_role_id = validated_data.get('user_role_id', instance.user_role_id)
        instance.user_dob = validated_data.get('user_dob', instance.user_dob)
        instance.user_address = validated_data.get('user_address', instance.user_address)
        instance.user_role = validated_data.get('user_role', instance.user_role)
        instance.save()

        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
        password = user_data.get('password')
        if password:
            user.set_password(password)
        user.save()

        return instance
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id','username', 'email']

# serialize all the modles
class RecruiterSerializer(serializers.ModelSerializer):
    user = serializers.DictField(write_only=True)
    
    class Meta:
        model = Recruiter
        fields = ['id','user', 'date_of_birth']

    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            validated_data['user'] = user
        return super().create(validated_data)

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question','q_type','application']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class ApplicationSerializer(serializers.ModelSerializer):
    # recruiter = serializers.PrimaryKeyRelatedField(queryset=Recruiter.objects.all())
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Application
        fields = ['id', 'recruiter', 'questions'] 


class JobPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobPost
        fields = ['id', 'recruiter', 'category', 'name', 'description', 'candidates_number', 'application', 'active','is_application']

    
class AppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applied
        fields = ['applicant','approved','jobPost']

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['applied','date','attended','cancelled']

