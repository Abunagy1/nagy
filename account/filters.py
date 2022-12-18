from django import forms
import django_filters
from .models import User, Profile
from django.db import models
"""class UserFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = User
        fields = '__all__'
        fields = {
            'username': ['exact', 'contains'],
            'last_login': ['exact', 'year__gt'],
        }"""

class UserFilter(django_filters.FilterSet):
     class Meta:
         model = User
         fields = ['user_type', 'email', 'username', 'first_name', 'last_name']
         filter_overrides = {
             models.CharField: {
                 'filter_class': django_filters.CharFilter,
                 'extra': lambda f: {
                     'lookup_expr': 'icontains',
                 },
             },
             models.BooleanField: {
                 'filter_class': django_filters.BooleanFilter,
                 'extra': lambda f: {
                     'widget': forms.CheckboxInput,
                 },
             },
         }

'''class ProfileFilter(django_filters.FilterSet):
     class Meta:
         model = Profile
         fields = ['city', 'phone', 'date_of_birth', 'about_me']
         filter_overrides = {
             models.CharField: {
                 'filter_class': django_filters.CharFilter,
                 'extra': lambda f: {
                     'lookup_expr': 'icontains',
                 },
             },
             models.BooleanField: {
                 'filter_class': django_filters.BooleanFilter,
                 'extra': lambda f: {
                     'widget': forms.CheckboxInput,
                 },
             },
         }'''
"""
#override
class PostFilter(django_filters.FilterSet):
    @classmethod
    def methodName(cls, arg):
        super(PostFilter, cls).methodName(arg)
        ...
"""

