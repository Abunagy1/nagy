from .import views
from django.urls import path
app_name = 'contact'
urlpatterns = [path('', views.contact, name='contact_me'),
                path('thanks/', views.thanks, name='thanks'),
]