from __future__ import unicode_literals
from os import name
from django import forms
from django.contrib.auth.models import User
from django.db.models.fields import TextField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.forms import widgets
from django.forms.widgets import Textarea
from django.template.defaultfilters import slugify
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.urls import reverse
#import os
from django.utils.translation import gettext_lazy as _
class Contact(models.Model):
    phone = models.CharField(max_length=15, default='')
    place = models.CharField(max_length=50, default='')
    email = models.EmailField(max_length=50, default='')
    class Meta:
        verbose_name = _('Info')
        verbose_name_plural = _('Infos')
    def __str__(self):
        return self.email