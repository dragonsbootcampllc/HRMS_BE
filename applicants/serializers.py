from rest_framework import serializers

from applicants.models import Applicant
from recruiters import serializers as Recruiter_serializers

class ApplicantSerializer(serializers.ModelSerializer):
    user = serializers.DictField(write_only=True)
    class Meta:
        model = Applicant
        fields = ['id','user','date_of_birth']
    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = Recruiter_serializers.UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            validated_data['user'] = user
        return super().create(validated_data)