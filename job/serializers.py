from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Job, Applicant
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    #jobs = serializers.HyperlinkedRelatedField(many=True, view_name='job-detail', read_only=True)
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'groups', 'is_staff', ]
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
class JobSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='job-highlight', format='html')
    class Meta:
        model = Job
        fields = ['url', 'user', 'title', 'job_type', 'description', 'published_at', 'Vacancy',
                  'title', 'code', 'linenos', 'language', 'style','salary', 'experience', 'category', 'job_icon', 'slug', 'highlight']
class ApplicantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Applicant
        fields = ['name', 'email', 'website', 'cv', 'cover_letter', 'date_of_application']
