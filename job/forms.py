from django import forms
from django.db.models import fields
from .models import Applicant, Job
class Apply(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['name', 'email', 'cover_letter',
                  'website', 'cv']  # or ==> fields = '__all__'
class PostJob(forms.ModelForm):
    class Meta:
        model = Job
        fields = '__all__'
        exclude = ('employer','slug')