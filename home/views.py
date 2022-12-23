
from datetime import timezone
from django.utils import timezone
from datetime import datetime as dt
from django.shortcuts import render
from .models import Home
from django.db import models
from blog.models import Post, Maintainer, Comment, Snippet, Vote, PostInstance
from account.models import Profile
from django.views import generic # Class Based Views, Context Var == object_list/detail... OR model_name_list/detail...
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.views.generic.edit import CreateView, UpdateView, DeleteView

class HomeView(generic.ListView): # path('', HomeView.as_view(), name='home'),
    template_name = 'home/home.html'   # address or path for template
    #queryset = Post.objects.all() # You can specifiy what you want using get_queryset as bellow if you don't want to list all posts
    #context_object_name = 'posts'  # trmplate context variable name
    #paginate_by = 2
    def get_queryset(self):
        """
        Return the last five published posts (not including those set to be published in the future).
        """
        return Post.objects.filter(created_at__lte=timezone.now()).order_by('-created_at')[:5]
        # created_at__lte=timezone.now() returns a queryset containing Posts whose created_at is
        # less than or equal to now - that is, earlier than or equal to - timezone.now, not in future.

# or using function based view
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    home = Home.objects.all().count()
    num_posts = Post.objects.all().count() # get all post instances counts
    num_instances = PostInstance.objects.all().count() # get all commented Post instances count
    # Available posts
    num_instances_new = PostInstance.objects.filter(status__exact='N').count() # if available book/job will be 'a'
    num_maintainers = Maintainer.objects.count()  # The 'all()' is implied by default.
    # Number of visits to this view, as counted in the session variable. 
    num_visits = request.session.get('num_visits', 1) # get value of 'num_visits' session key in session attr. dict. obj
    request.session['num_visits'] = num_visits+1 # Sessions allow you to store/get/update/del...arbitrary data per browser
    # Render the HTML template index.html with the data in the context variable.
    return render(request, 'home/index.html',
        context={'home': home, 'num_posts': num_posts, 'num_instances': num_instances,
                 'num_instances_new': num_instances_new, 'num_maintainers': num_maintainers,
                 'num_visits': num_visits}, # 
)
