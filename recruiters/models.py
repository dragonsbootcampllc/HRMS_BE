from django.db import models
from django.conf import settings

from applicants.models import Applicant

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_role_id = models.IntegerField()
    user_dob = models.DateField()
    user_address = models.TextField()
    user_role = models.CharField(max_length=50)

# Automatically handle signals to create or update user profiles
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

class Recruiter(models.Model):
    user = models.OneToOneField(User, related_name='recruiter', on_delete=models.CASCADE)
    date_of_birth = models.DateField()


class Application(models.Model):
    recruiter = models.ForeignKey(Recruiter, related_name='applications', on_delete=models.CASCADE)

class Question(models.Model):
    question = models.TextField()
    application = models.ForeignKey(Application, related_name='questions',on_delete=models.CASCADE)
    q_type = models.CharField(max_length=100, null=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class JobPost(models.Model):
    recruiter = models.ForeignKey(Recruiter, related_name='posts', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    candidates_number = models.IntegerField(default=0)
    is_application = models.BooleanField(default=False)
    application = models.OneToOneField(Application, related_name='application', on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)


class Applied(models.Model):
    applicant = models.ForeignKey(Applicant, related_name='applied_for', on_delete=models.CASCADE)
    jobPost = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)


class Interview(models.Model):
    applied = models.ForeignKey(Applied, related_name='interviews', on_delete=models.CASCADE)
    date = models.DateTimeField()
    attended = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

class Answer(models.Model):
    question = models.OneToOneField(Question, related_name='answers', on_delete=models.CASCADE)
    answer = models.CharField(max_length=250)
    applied = models.ForeignKey(Applied, related_name='applicant_answer', on_delete=models.CASCADE)