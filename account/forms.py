from django import forms
from django.db.models import fields
from django.shortcuts import get_object_or_404
from .models import Profile
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from gettext import translation
from .models import User #you can use get_user_model
# -*- coding: utf-8 -*-
from django import forms
#from django.utils.translation import gettext_lazy as _
from account.models import Profile
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django_registration.forms import RegistrationForm
from account.models import User
# the simplest one if you didn't creat a custom user model
# in user app you can put User Creation Form here
# for user creation w/o custom model you need only username and passwod

class UserForm(UserCreationForm): # SignUp or register Form
    # if you added any field here will override the built-in field, so we just want to
    # use some of the built in fields(username, email, password)  and not changes it as follows
    class Meta:
        model = User
        fields = ['username', 'email',]
class DateInput(forms.DateInput):
    input_type = 'date'
# Edit Profile form
class ProForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'date_of_birth': DateInput(),
        }
        exclude = ('user',)
# or establish new form fields here, if a new form ==> class take (forms.Form)

class LoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(label = "Password", widget = forms.PasswordInput)

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password")

class EditProfileForm(forms.Form):
    username = forms.CharField()
    about_me = forms.CharField(widget=forms.Textarea())
    photo = forms.ImageField(required=False)
    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
    def clean_username(self):
        """
        This function throws an exception if the username has already been taken by another user
        """
        username = self.cleaned_data['username']
        if username != self.original_username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    'A user with that username already exists.')
        return username
        
class MyCustomUserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
        fields = {'username', 'email', 'password1', 'password2'}

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = {'username', 'email', 'password1', 'password2'}
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.name = self.cleaned_data['name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# Next form if you extend Both AbstractBaseUser / if AbstractUser that already has the same auth.User model, there is no need
# for this form at all just use the 1st simlest one above all as it's the same as the above one but used for auth user
class CustomUserCreationForm(UserCreationForm): # as we have a odel but has only username as emails
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput) # You can remove those two fields as they are already been existed
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta(UserCreationForm.Meta): # UserCreationForm has already all default fields, so you just need to add the additional fields to it
        model = User
        #fields = UserCreationForm.Meta.fields + ('user_type',)  # birth date's been removed and added to profile model
        fields = ('username', 'email', ) # if you have any other special field add it here
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM.
        username = self.cleaned_data["username"]
        try:
            #User.objects.get(username=username)
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()
    group = Group()
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password',)

# to allow only some active users to log in
"""
from django.contrib.auth.forms import AuthenticationForm
class PickyAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        if user.username.startswith('b'):
            raise forms.ValidationError(
                _("Sorry, accounts starting with 'b' aren't welcome here."),
                code='no_b_users',
            )
"""
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple    
User = get_user_model()
# Create ModelForm based on the Group model.
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []
    # Add the users field.
    users = forms.ModelMultipleChoiceField(
         queryset=User.objects.all(), 
         required=False,
         # Use the pretty 'filter_horizontal widget'.
         widget=FilteredSelectMultiple('users', False)
    )
    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance