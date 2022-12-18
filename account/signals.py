#from django.contrib.auth.models import User
from .models import User
from django.db.models.signals import post_save 
from django.core.signals import setting_changed
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import Profile
from django.conf import settings
from django import apps
from django.db import models
# this signal could be put in custome user models user app signals becaue you have Custom
# user creation form there
@receiver(post_save, sender=User) # receiver() decorator / sender=User to insure no duplicate in action by any other app save
def create_user_profile(sender, instance, created, **kwargs): # this reciever called from apps.py
    if created:
        Profile.objects.create(user=instance)
def create_profile(sender, instance, created, **kwargs): # this reviever called here immediately after definition
    if created:
        try:
            profile = Profile()  # another form of profile class constructor 
            profile.user = instance
            profile.save()
        except:
                pass
post_save.connect(create_profile, sender=User, weak=False, dispatch_uid='Profile') 
"""
# the next line can be put in apps.py or here 
# post_save.connect(signals.create_user_profile, sender=settings.AUTH_USER_MODEL, weak=False, dispatch_uid='Profile')
@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = Profile(user=user)
        user_profile.save()

# if you have many user models and you may need to override settings. AUTH_USER_MODEL
# from django.apps import apps
@receiver(setting_changed)   # setting_changed is a signal exist in lib/py3.10/site-packages/django/core...
def user_model_swapped(**kwargs):
    if kwargs['setting'] == 'AUTH_USER_MODEL':
        apps.clear_cache()
        from account import Profile
        Profile.UserModel = get_user_model()
"""