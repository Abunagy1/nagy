from django.urls import include, path, re_path
from . import views

app_name = "pinax_messages"

urlpatterns = [
    re_path(r"^inbox/$", views.InboxView.as_view(),
        name="inbox"),
    re_path(r"^create/$", views.MessageCreateView.as_view(),
        name="message_create"),
    re_path(r"^create/(?P<user_id>\d+)/$", views.MessageCreateView.as_view(),
        name="message_user_create"),
    re_path(r"^thread/(?P<pk>\d+)/$", views.ThreadView.as_view(),
        name="thread_detail"),
    re_path(r"^thread/(?P<pk>\d+)/delete/$", views.ThreadDeleteView.as_view(),
        name="thread_delete"),
]
