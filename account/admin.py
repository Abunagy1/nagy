from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Profile, City # you can use get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin # for Normal auth.User
#from django.contrib.auth.admin import UserAdmin as AuthUserAdmin # for AbstractUser just a name to discriminate 
#from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # for AbstractBaseUser
from django.contrib.auth import get_user_model
# -*- coding: utf-8 -*-
from .forms import CustomUserCreationForm, CustomUserChangeForm, GroupAdminForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
class CityAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    # wrong inlines = [PostsInline] # that mean only one Tag can have many Posts (it has many to many not foreign key relation to post)
    # blog.admin.PostsInline': 'blog.Post' has no ForeignKey to 'blog.Tag'.
admin.site.register(City, CityAdmin)
class ProfileInline(admin.StackedInline):
    model = Profile
    #can_delete = False
    verbose_name_plural = 'profiles'

# Define a new User admin
class myUserAdmin(UserAdmin):
    # The forms to add and change user instances
    inlines = (ProfileInline, )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = User
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'email', 'date_joined', 'user_type')
    #list_display = ('username', 'email', 'is_active', 'is_superuser', 'last_login',)
    list_filter = ('user_type',)
    #list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    """
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('custom_field',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('custom_field',)}),
    )
    """
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
# Now register the new UserAdmin...
admin.site.register(User, myUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)

# or simpler
"""
class UserAdmin(AuthUserAdmin):
    add_form = CustomUserCreationForm
    update_form_class = UserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Permissions', {'fields': ('is_superuser',)}),
    )
# use just next line if you have just class User(AbstractUser): => pass (no customization yet)
admin.site.register(User, UserAdmin)
"""

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
"""
class ProfileInline(admin.StackedInline):
    model = Profile
    #can_delete = False
    verbose_name_plural = 'profiles'
# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
# Re-register UserAdmin
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)
"""

'''# Unregister the original Group admin.
admin.site.unregister(Group)
# and 
# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']

# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)'''