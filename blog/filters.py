from django import forms
import django_filters
from .models import Maintainer, Post
from django.db import models

class PostFilter(django_filters.FilterSet):
        class Meta:
            model = Post
            fields = ['title',]
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
class MaintainerFilter(django_filters.FilterSet):
     class Meta:
         model = Maintainer
         fields = ['user', 'first_name']
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
"""
#override
class PostFilter(django_filters.FilterSet):
    @classmethod
    def methodName(cls, arg):
        super(PostFilter, cls).methodName(arg)
        ...
"""

