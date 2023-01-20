from __future__ import unicode_literals
from os import name
#from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.template.defaultfilters import slugify
#from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
#import os
from django.db import models
#from account.models import Profile
from django.db.models.signals import post_save, pre_save
#from django.core.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User  # Required to assign User as a commenter
from django.contrib.auth.models import (UserManager, AbstractUser)
from django.core.mail import send_mail, send_mass_mail, BadHeaderError
"""
class Role(models.Model):
  '''
  The Role entries are managed by the system,
  automatically created via a Django data migration.
  '''
  STUDENT = 1
  TEACHER = 2
  CUSTOMER = 3
  SUPERVISOR = 4
  ADMIN = 5
  ROLE_CHOICES = (
      (STUDENT, 'student'),
      (TEACHER, 'teacher'),
      (CUSTOMER, 'customer'),
      (SUPERVISOR, 'supervisor'),
      (ADMIN, 'admin'),
  )
  id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)
  def __str__(self):
      return self.get_id_display()
"""
# UserManager and User Classes are just names not refering to UserManager or built-in User
# if you will use AbstractUser put here BaseUserManager instead of UserManager
class newUserManager(BaseUserManager):  # if wrong try in the second BaseUserManager below 
    def __init__(self, type=None):
        super(newUserManager, self).__init__()
        self.type = type
    def create_user(self, email,  password=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of birth and password.
        """
        user = self.create_user(email, password=password, **extra_fields)
        user.is_superuser = True
        user.save(using=self._db)
        return user

# or from blog how to extend custom user models
class myUserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

# or other form
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields): # any extra_fields as **kwargs
        """
        Create and save a User with the given email and password.
        """        
        if not email:
            raise ValueError(_('Users must have an email address'))
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUserManager(UserManager):
    def __init__(self, type=None):
        super(CustomUserManager, self).__init__()
        self.type = type
    def get_queryset(self):
        qs = super(CustomUserManager, self).get_queryset()
        if self.type:
            qs = qs.filter(type=self.type).order_by('first_name', 'last_name')
        return qs
    def get_this_types(self, types):
        qs = super(CustomUserManager, self).get_queryset()
        qs = qs.filter(type__in=types).order_by('first_name', 'last_name')
        return qs
    def get_all_excluding(self, types):
        qs = super(CustomUserManager, self).get_queryset()
        qs = qs.filter(~models.Q(type__in=types)).order_by('first_name', 'last_name')
        return qs

class User(AbstractUser): 
    # if you need any other information regarding any type of these following kinds of users make a model for them
    USER_TYPE_CHOICES = (
    (1, 'admin'),
    (2, 'supervisor'),
    (3, 'instructor'),
    (4, 'student'),
    (5, 'customer'),
    (6, 'employee'),
    (7, 'advertiser'),
  )
    # sys_id = models.AutoField(primary_key=True, blank=True) 
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True,)
    is_active = models.BooleanField(default=True)

    is_superuser = models.BooleanField(default=False) #is_admin = models.BooleanField(default=False) 
    objects = newUserManager()
    USERNAME_FIELD = 'email' # string describing the name of the field on
    # the User model that is used as the unique identifier
    REQUIRED_FIELDS = ["username"] # list of the field names that will be prompted
    # for when creating a user via thecreatesuperuser management command
    # roles = models.ManyToManyField(Role)
    # the next line has null=True to not having validation error when creating Superuser at the begining
    # django.db.utils.IntegrityError: null value in column "user_type" of relation "user_user" violates not-null constraint
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True, blank=True)
    class Meta:
        #app_label = "user" # or 'auth'
        #db_table = "users"
        #verbose_name = _('User')
        #verbose_name_plural = _('Users')
        permissions = [
            ("change_post_status", "Can change the status of posts"),
            ("close_discussions", "Can remove a post by setting its status as closed"),
            ('can_publish', 'Can Publish Posts'),
        ]
    def __str__(self):
        return self.email
    # this methods are require to login super user from admin panel
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, eturn True always or return self.is_superuser
        return True
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always or return self.
        return True
    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name
    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)
    def notification_approval(self, action, site):
        return True if self.is_active else 'postta@aol.com'

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

# another type of completely different  custom user model 
"""
class MyUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True,)
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']
    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
"""

# you can add permission programatically like the following
"""
from blog.models import Post
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
content_type = ContentType.objects.get_for_model(Post)
permission = Permission.objects.create(
    codename='can_publish',
    name='Can Publish Posts',
    content_type=content_type,
)
# but better add permission in meta class
"""
'''
def upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/apply/<title>/<filename>
    # return os.path.join("uploads", filename)
    path = settings.MEDIA_ROOT # /media/
    img_list = os.listdir(path + '/profiles') # in template {% for image in img_list %} <img src="/{{ img_list }}/" alt="{{image}}">
    return 'profiles/{0}/{1}'.format(instance.name, filename)
'''
def directory_path(instance, filename):
    imgName, extension = filename.split('.')
    imgName = instance.user
    return 'profiles/%s.%s' %(imgName, extension)

class City(models.Model):
    name = models.CharField(max_length=30, null= True, blank=True)
    class meta:
        verbose_name_plural = _('cities')
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile_users', on_delete=models.CASCADE, primary_key=True, unique=True, db_index=True) # settings.AUTH_USER_MODEL or get_user_model()
    city = models.ForeignKey(City, related_name='profile_cities', on_delete=models.SET_NULL, null=True, blank=True)
    # phone = PhoneNumberField()
    # fax_number = PhoneNumberField(blank=True)
    phone = models.CharField(max_length=15, default='', null=True) # phone = PhoneNumberField()
    photo = models.ImageField(upload_to=directory_path, null=False, blank=True)
    date_of_birth = models.DateField('Birth Date', null=True, blank=True, )
    #slug = models.SlugField(null=True, blank=True)
    about_me = models.TextField(null=False, blank=True)
    #signup_confirmation = models.BooleanField(default=False)
    def get_absolute_url(self):
        return reverse('accounts:user_profile', kwargs={'username' : self.username})
    """
    @property
    def followers(self):
        return Follow.objects.filter(follow_user=self.user).count()

    @property
    def following(self):
        return Follow.objects.filter(user=self.user).count()
    """
    def __str__(self):
        return str(self.user) # return f'{self.user.username} Profile'
    """
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        img = Image.open(self.photo.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.photo.path)
    
    """
# if we want to create signal callback function in the same model file instead of submodule signals
    """
    class Meta:
        # choose one of the following functions but this is an example but it's wrong to make signals to 
        # auth user that already been related to profile by user
        @receiver(post_save, sender=User)
        def create_profile_signal(sender, instance, created, **kwargs):
            if created:
                Profile.objects.create(user=instance)
            instance.profile.save()
        # or 
        def create_profile(sender, instance, created, **kwargs):
            if created:
                try:
                    profile = Profile()  # another form of profile class constructor 
                    profile.user = instance
                    profile.save()
                except:
                    pass
        post_save.connect(create_profile, sender=User)
    """
# or put it individually 
"""
@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            profile = Profile()  # another form of profile class constructor 
            profile.user = instance
            profile.save()
        except:
            pass
post_save.connect(create_profile, sender=User)
"""
# add a custom Group ModelForm. The second step is to unregister the
# original Group admin and register a new Group admin that displays our ModelForm: