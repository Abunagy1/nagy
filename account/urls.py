from django_registration.backends.activation.views import RegistrationView
from .forms import MyCustomUserForm
from django.urls import path
from .views import edit, sign_up, log_in, log_out, edit_profile, index, details, register, CustomUserLoginView, UsersListView, UserProfileView, user_details
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views # or import built in classes as follows
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView
)

"""
path('accounts/', include('django.contrib.auth.urls')),
accounts/login/ [name='login']
accounts/logout/ [name='logout']
accounts/password_change/ [name='password_change']
accounts/password_change/done/ [name='password_change_done']
accounts/password_reset/ [name='password_reset']
accounts/password_reset/done/ [name='password_reset_done']
accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
accounts/reset/done/ [name='password_reset_complete']
"""
app_name = 'account'
urlpatterns = [
    path('', index, name='index'), # <a href="/accounts/"> Home</a>  accounts/ need permission
    #path('<int:pk>', prof_edit, name='profile_edit'),  # <str:username>
    path('profile/', details, name='profile'), # The user redirected to this view to see his profile
    path('profile/<str:username>/', user_details, name='user_profile'), # when the user click on someones profile name redirect to this view
    path('profile/<str:username>/edit/', edit_profile, name='edit_profile'),
    #path('signup/', RegistrationView.as_view(form_class=MyCustomUserForm), name='signup',),
    path('signup/', sign_up, name='signup'),
    path('login/', CustomUserLoginView.as_view(), name='login'), # CustomUserLoginView.as_view()
    path('logout/', log_out, name='logout'),
    #path('login/', auth_views.LoginView.as_view(template_name='login.html', next_page='accounts/profile'), name= 'login'),
    #path('logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='/'), name= 'logout'),
    path('password_reset/', PasswordResetView.as_view(
        template_name='user/password_reset.html',
        email_template_name='user/password_reset_email.html',
        subject_template_name='user/password_reset_subject.txt',
        success_url='/user/password_reset/done/'),
        name='password_reset'
    ),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='user/password_reset_done.html'),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='user/password_reset_confirm.html',
        success_url='/user/reset/done/'),
        name='password_reset_confirm'
    ),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='user/password_reset_complete.html'),
        name='password_reset_complete'
    ),
    # the following password reset templates is the default ones, so you have to create them if you don't want to use default
    # ... some built-in auth-views & other customizable ones
    path('password_change/', PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url=reverse_lazy('accounts/password_change_done')),
        name='password_change'),
    #path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),), # use the builtin name='password_change'
    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'),
        name='password_change_done'),
]
"""
urlpatterns = [ 
    path('about/', login_required(TemplateView.as_view(template_name="secret.html"))), 
    path('vote/', permission_required('polls.can_vote')(VoteView.as_view())), 
]  
"""