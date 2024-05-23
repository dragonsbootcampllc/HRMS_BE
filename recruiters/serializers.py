from rest_framework import serializers
from django.contrib.auth.models import Group, User

from recruiters.models import Recruiter, Question, Application, Category, JobPost, Applied, Interview
from recruiters.models import JobPost, Application
from .models import UserProfile
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_address', 'user_role', 'user_dob']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_address', 'user_role', 'user_dob']

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'userprofile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile')
        user = super().update(instance, validated_data)
        profile = user.userprofile
        profile.user_address = profile_data.get('user_address', profile.user_address)
        profile.user_role = profile_data.get('user_role', profile.user_role)
        profile.user_dob = profile_data.get('user_dob', profile.user_dob)
        profile.save()
        return user
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")
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

