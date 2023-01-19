import datetime
import os
import profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import CustomUserCreationForm, LoginForm, EditProfileForm, UserForm, ProForm, MyCustomUserForm, SignUpForm, CustomUserChangeForm
from .models import User, Profile
from blog.models import Post
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
# from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as _
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail, send_mass_mail, BadHeaderError
# search on how to use these next built-in forms to authinticate normal built in auth.users
from django.contrib.auth.forms import (AdminPasswordChangeForm, AuthenticationForm, PasswordChangeForm,
PasswordResetForm) # password reset form used to send one-time use link to reset a user’s password via send_mail()
# userCreationForm uses the built-in User so need to tell django that we have our custom user & import it's creation form
# should be in account app
# if you have  custome user models in user app import user form from there
# Create your views here.
from datetime import timezone
from .filters import UserFilter
# userCreationForm uses the built-in User so need to tell django that we have our custom user & import it's creation form
# should be in account app
"""
def index(request):
    users = User.objects.all()
    return render(request,'index.html',{'users':users})
"""
@login_required
def index(request):
    users_num = get_user_model().objects.all().count()
    users = get_user_model().objects.all() # 
    profiles = Profile.objects.all()
    filter = UserFilter(request.GET, queryset=users)
    has_filter = any(field in request.GET for field in set(filter.get_fields()))
    f = filter.qs
    paginator = Paginator(f, 10)  # Paginator object Show filtered 3 posts per page.
    page_obj = request.GET.get('page') # page object on the request
    page = paginator.get_page(page_obj) # give filtered page to Paginator to be Paginated float page numbers or (page() for int. doesn't matter)
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path + '/profiles')
    if request.method == 'GET':
        try:
            usersList = paginator.page(page_obj) # give filtered page to Paginator to be Paginated for for integer page numbers
        except PageNotAnInteger:
                # If page is not an integer deliver the first page
            usersList = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            usersList = paginator.page(paginator.num_pages)
        context = {'users': page, 'profiles': profiles, 'filter': filter, 'has_filter':has_filter, 'users_num': users_num, 'usersList': usersList, 'img_list' : img_list} # posts is the key name to use in template
        return render(request, 'index.html', context)
    else:
        return redirect(reverse('/'))
# to show all users
class UsersListView(ListView):
    model = User
    template_name = 'index.html'
    context_object_name = 'users'
    paginate_by = 3 # {% for user in users %} {{ post.author.first_name }} {% endfor %}
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Profile.objects.filter(user=user).order_by('-date_posted')
        
# to show user profile by pagination to 1
class UserProfileView(ListView):
    model = Profile
    template_name = 'account/profile.html'
    context_object_name = 'profile'
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Profile.objects.filter(user=user).order_by('-user_id')

def notification_approval(user, action, site):
    return '{}@domain.tld'.format(user.username)


@login_required
def details(request, username=None):
    if username:
        user = get_object_or_404(get_user_model(), username=username)
        profile = get_object_or_404(Profile, user=user)
        #prof = Profile.objects.get(pk=self.kwargs['pk'])
    else:
        profile = get_object_or_404(Profile, user=request.user)
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path + '/profiles/') # if you have different folders in the same media folder you should do this
    #profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'account/profile.html', {'profile': profile, 'img_list' : img_list})

@login_required
def user_details(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    profile = get_object_or_404(Profile, user=user)
    #prof = Profile.objects.get(pk=self.kwargs['pk'])
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path + '/profiles/') # if you have different folders in the same media folder you should do this
    #profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'account/user_profile.html', {'profile': profile, 'img_list' : img_list})
# if you wanted to specify the user instance before saving the form so give the username or id
# to the function and just save poth prof1 & prof@ after valid not commit = false cause you already specify user
# if you wanted to use just the user already logged in the request without having to take username as above
# you should remove any user.id or user.username from the templates <a href="{% url 'accounts:edit_profile' user.username/id %}"
@login_required
def edit_profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    profile = get_object_or_404(Profile, user=user)
    #profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        prof1 = CustomUserChangeForm(request.POST, instance=user) # just username, email and password
        # create a form instance and populate it with data from the request:
        prof2 = ProForm(request.POST, request.FILES, instance=profile) # all profile fields except FK fields
        # check whether it's valid:
        if prof1.is_valid() and prof2.is_valid():
            # process the data in form.cleaned_data as required
            prof1.save(), prof2.save() # prof2.save(commit=False)
            #prof2.user = request.user
            # ...
            #prof2.save()
            # redirect to a new URL:
            messages.success(request, _('Your profile has been successfully updated!'))
            return redirect('/accounts')
            #return HttpResponseRedirect('/accounts/')
        else:
            messages.error(request, _('Please correct the following error.'))
    # if a GET (or any other method) we'll create a blank form
    else:
        prof1 = CustomUserChangeForm(instance=user)
        prof2 = ProForm(instance=profile)
    context = {'prof1': prof1, 'prof2': prof2}
    return render(request, 'account/profile_edit.html', context)
# if you wanted to specify just only some fields that could be edited or check something in them use the following
@login_required
def edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        # request.user.username is the original username, here is just one form
        form = EditProfileForm(user.username, request.POST, request.FILES)
        if form.is_valid():
            about_me = form.cleaned_data["about_me"]
            username = form.cleaned_data["username"]
            photo = form.cleaned_data["photo"]
            user = User.objects.get(username=request.user.username)
            profile = Profile.objects.get(user=user)
            user.username = username
            user.save()
            profile.about_me = about_me
            if photo:
                profile.photo = photo
            profile.save()
            return redirect("accounts:profile", username=user.username)
    else:
        form = EditProfileForm(user.username)   # <-- add also here 
    return render(request, "account/profile_edit.html", {'form': form})
@login_required(login_url='login_user')
def profiles(request):
    # logged in user
    user = request.user
    # instance id of current logged in user
    instance_id = request.user.profile.id
    # Profile is a instance of NewUser class
    form = ProForm(instance=user)
    if request.method == 'POST':
        # form data + Profile instance
        form = ProForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # the picture that is currently uploaded by user
            uploaded_file = request.FILES['avatar']
            # django file system storage, we call it, so we can save the file on disk
            #fs = FileSystemStorage()  # uncomment this line i commented it because it's not installed yet
            # we save the file. We need the name and the content of the file.
            #fs.save(uploaded_file.name, uploaded_file) # uncomment this line 
            # new picture cleaned data from form post
            avatar = form.cleaned_data.get('avatar')
            #name_extension = avatar.name
            #name, extension = name_extension.split(".")
            #raise ValueError(avatar)
            # title cleaned data from form post
            title = form.cleaned_data.get('title')
            # we update the database with the name of the picture we want to display
            Profile.objects.filter(id=instance_id).update(avatar=avatar, title=title)
        else:
            messages.success(request, "Invalid File.")
    context = {'form': form}
    return render(request, "profiles/profiles.html", context)
########################################################################################
################################ Sign_up & Login views #################################
########################################################################################
def sign_up(request):
    # redirect a user to the home page if he is already logged in
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    if request.method == 'POST':
        # replace UserCreationForm with SignUpForm for user acc. creation
        form = CustomUserCreationForm(request.POST) # instead of form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            #user.set_password(password)
            #user.save()
            # Profile.objects.create(user=new_user) #that line already been created by the signal
            login(request, user)
            # display a nice message when a new user is registered
            messages.success(request, _('Your profile was successfully created!')) # messages.info(request,"Successfully Register ...")
            return redirect('/accounts/profile')
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()   # replace UserCreationForm with SignUpForm == form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
def register(request):
    if request.method == 'POST':
        form = MyCustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            subject, from_email, to = 'Welcome', 'gabernagy@gmail.com', email
            html_content = render('regiteration/email.html', { 'username': username })
            msg = send_mail(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, f'Your account has been created ! You are now able to log in')
            return redirect('accounts:login')
    else:
        form = MyCustomUserForm()
    return render(request, 'registration/register.html', {'form':form})
# or
def sign(request):
    form = UserForm(request.POST or None, request.FILES or None )
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        Profile.objects.create(user=new_user)
        login(request, new_user)
        messages.info(request,"Successfully Register ...")
        return redirect("/")
    context = {
            "form" : form
        }
    return render(request,"registration/signup.html",context)

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm # SignUpForm
    template_name = 'user/signup_form.html'
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('accounts:profile')
#####################################################################################
#####################################################################################
# all the next views already built in in django.contrib.auth.urls,
# but you can pass them in your own views like here, Note that you have to make their templates
# cause no default templates for these views
# login view
def log_in(self, request, *args, **kwargs):
    if request.user.is_authenticated:
        #profile = Profile(user=request.user)
        #return render(request, 'account/profile.html', {'profile': profile})
        return redirect('accounts:profile', username=request.user.username) # return render(request, 'homepage.html')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        print('yes')
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist!')
            # We check if the data is correct
            user = authenticate(request, username=username, password=password)
            if user:  # If the returned object is not None
                login(request, user)  # we connect the user
                #profile = Profile.objects.get(userername=user.username)
                return redirect('accounts:profile', username=user.username) # return redirect('/')
            else:  # otherwise an error will be displayed
                messages.error(request, 'Invalid email or password')
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def thankyou(request):
    return render(request,'thanks.html')

# or
from django.views.generic.edit import FormView
class CustomUserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = '/accounts/username'
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form':form})
    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(self.success_url)
                else:
                    return HttpResponse('User is not active') # TEMP
            else:
                return HttpResponse('User does not exist') # TEMP
        else:
            return HttpResponse('Form is not valid') # TEMP

# or class based views using built in forms
# for custom users models use custom authintication forms
# to allow only some active auth.users to log in (from using authentications docs)
class UsersAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        if user.username.startswith('b'):
            raise ValidationError(
                _("Sorry, accounts starting with 'b' aren't welcome here."),
                code='no_b_users',
            )
# to allow all users to log in regardless of active status
class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        pass

# to customize authentication for custom users model example or see customize authenticathion in docs

class SettingsBackend(BaseBackend):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.
    Use the login name and a hash of the password. For example:
    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """
    def authenticate(self, request, username=None, password=None):
        login_valid = (settings.ADMIN_LOGIN == username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = User(username=username)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
# ...
def log_out(request):
    logout(request)
    #return render(request, "registration/logged_out.html")

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name='posts'
    paginate_by = 15

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['postuser'] = Post.objects.filter(author=user).order_by('-date_posted')[:1]
        context['posts'] = Post.objects.filter(author=user).order_by('-date_posted')
        return context
"""
<div class="col-auto"><img class="img-profile-st" src="{{ post.author.profile.image.url }}"></div>
<h1 class="mb-3" style="text-align: center;">Posted by {{ view.kwargs.username }} ({{ page_obj.paginator.count }})</h1>
"""