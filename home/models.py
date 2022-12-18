from __future__ import unicode_literals
from os import name
from django import forms
#from django.contrib.auth.models import User
from django.db.models.fields import TextField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.forms import widgets
from blog.models import Post, Maintainer, Comment, Snippet, Vote, PostInstance
from job.models import Job, Applicant
from account.models import User, Profile
from contact.models import Contact
from django.forms.widgets import Textarea
from django.template.defaultfilters import slugify
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.urls import reverse
#import os
from django.utils.translation import gettext_lazy as _
class Home(models.Model):
    post = models.OneToOneField(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_posts', default='')
    job = models.OneToOneField(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_jobs', default='')
    class Meta:
        verbose_name = _('Home')
        verbose_name_plural = _('Home')
    def __str__(self):
        return 'Posts titles {} Jobs Available {}'.format(self.post.title, self.job.title)  # 
        return '{0}, {1}'.format(self.posts, self.jobs) # return (self.posts, self.users, self.jobs)
        return f'{self.users.username}\'s Post- {self.posts.title}' # return self.creator.username + ',
