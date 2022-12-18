from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views
app_name = 'home'
urlpatterns = [ # you can use the URL name to map the link in template <a href="{% url 'name' %}">URLText</a>
    #path('', views.HomeView.as_view(), name='index'),
    path('', views.index, name='index'), # <a href="/blog/">Home</a>  blog/
] # <int/str/slug/uuid/path:pk/...>
urlpatterns = format_suffix_patterns(urlpatterns)