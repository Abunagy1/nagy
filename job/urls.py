from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from job.models import Job
from . import views
from django.urls import  path, include
from rest_framework import routers, renderers
from rest_framework.routers import DefaultRouter
from .serializers import JobSerializer
from rest_framework.urlpatterns import format_suffix_patterns
#from .api import JobDetial, JobList, JobViewSet, UserViewSet, jobDetailViewSet, jobViewSet
from . import api
app_name='job'
# Create a router and register our viewsets with it.
# Routers provide an easy way of automatically determining the URL conf.
router = DefaultRouter() # router = router.DefaultRouter() 
router.register(r'users', api.UserViewSet)
router.register(r'groups', api.GroupViewSet)
router.register(r'jobs', api.JobViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('index/', views.index, name='index'),
    path('', views.job_list, name='job_list'),
    path('add/', views.job_post, name='add'),
    path('<str:slug>/', views.job_details, name='details'),             
]
# or 
#urlpatterns = format_suffix_patterns(urlpatterns)
#urlpatterns += [path('api/', include(router.urls)),]