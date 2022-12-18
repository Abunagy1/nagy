import debug_toolbar
from django import urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from django.urls import include, path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
#import blog.api, job.api
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
#Add URL maps to redirect the base URL to our application
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView 
# Add Django site authentication urls (for login, logout, password management)
# Use static() to add url mapping to serve static files during development (only)
API_TITLE = 'Site API'
API_DESCRIPTION = 'A Web API for creating and viewing highlighted code snippets.'
schema_view = get_schema_view(title=API_TITLE)
urlpatterns = [
    path('admin', admin.site.urls),
    #re_path(r'^schema/$', schema_view), # old deprecated
    #re_path(r'^docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)), # old deprecated
    path('openapi', get_schema_view(title="My Project", description="API for all things …"), name='openapi-schema'), # the newest one
    # to get the built-in authinticatuion views login/logout/change_password/etc...
    #path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('account.urls', namespace='accounts')),
    path('contacts/', include('contact.urls', namespace='contacts')),
    path('jobs/', include('job.urls', namespace='jobs')), 
    #re_path(r'^blog/', include('blog.urls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('', include('home.urls', namespace='home')),
    #re_path(r"^messages/", include("messages.urls", namespace="messages")), it was pinax.message but i took it outside the pinax abn made it free
    path('messages/', include('postman.urls', namespace='postman')), # just alternated by pinax.messages
    path("chat/", include("chat.urls", namespace='chat')),
    re_path(r'chat2/', include('django_private_chat2.urls', namespace='django_private_chat2')),
    #re_path(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), # has no relation with others blog urls only for login to api
    path('__debug__/', include(debug_toolbar.urls)), # after install django-debug-toolbar
] + staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# ...
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''
django_private_chat2 doesn't provide any endpoint to fetch users (required to start new chat,
for example) It's up to you to do so.
The example app does it in urls.py so feel free to copy the handler from there if you wish.
'''