from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .import api
from .views import (add_vote, create_maint, edit_post, index, likePost, maint_details, maintainers_list, post_details, PostDetailView, add_post, PostCreateView, PostUpdateView, PostDeleteView,
PostedByUserListView, remove_vote, renew_post_admin, RenewedAllListView, MaintainerListView, MaintainerDetailView, MaintainerCreate,
MaintainerUpdate, MaintainerDelete, search_titles, vote )
"""
<a href="{% url 'url_name_in_urlpatterns' argument_needed %}"> {{ context_var_name.field_name }}</a>
<li><a href="{% url 'posts:details' post.id %}">{{ post.title }}</a></li>  
"""
# application namespace to use in {% url blog:details post.id %} because there are so many apps in the site that has same name details
app_name='blog' # To let Django knows which app view to create for a url when using the {% url %} template tag
# Create a router and register our API viewsets with it.
router = DefaultRouter()
# Registering the viewsets with the router is similar to providing a urlpattern
# We include two arguments - the URL prefix for the views, and the viewset itself
# The DefaultRouter class we're using also automatically creates the API root view for us,
# so we can now delete the api_root method from our views module, don't forget to do so.
# The API URLs are now determined automatically by the router.
router.register(r'posts', api.PostViewSet) # api views blog/api/posts
router.register(r'snippets', api.SnippetViewSet) # api views
#router.register(r'users', api.UserViewSet) # will conflict with the same users of job urls.py
# The Normal views routing.
urlpatterns = [ # you can use the URL name to map the link in template <a href="{% url 'name' %}">URLText</a>
    path('api', include(router.urls)), # OR re_path(r'^', include(router.urls)) => this only for api routing using default router
    #path('', views.IndexView.as_view(), name='home'),
    path('', index, name='index'), # <a href="/blog/">Home</a>  for normal function based views 127.0.0.1:8000/blog
    #path('posts/', views.PostListView.as_view(), name='posts'), # <a href="/blog/posts/">Home</a>  use name better blog/posts
    path('posts/add/', add_post, name='add'),  # 127.0.0.1:8000/blog/posts/add/
    path('posts/', search_titles, name='search'),  # 127.0.0.1:8000/blog/posts/add/
    path('posts/vote', add_vote, name='vote'),  # 127.0.0.1:8000/blog/posts/add/
    path('posts/remove-vote', remove_vote, name='vote'),  # 127.0.0.1:8000/blog/posts/add/
    #path('posts/create/', PostCreateView.as_view(), name='create'),
    path('posts/<uuid:pk>/', post_details, name='details'), # 127.0.0.1:8000/blog/posts/slug/
    #re_path('/posts/(?P<pk>[0-9]+)/\\Z', post_details, name='details'), # /(?<slug>[\w-])+/
    #path('posts/<uuid:pk>/', PostDetailView.as_view(), name='post-detail'),
    #path('posts/<int:pk>/<str:slug>/', PostDetailView.as_view(), name='post-detail'), # <a href="{% url 'post-detail' %}">URLText</a> or
    #re_path(r'^post/(?P<pk>\d+)$', views.PostDetailView.as_view(), name='post-details'), # re_path == regular exp path
    path('posts/<uuid:pk>/update/', edit_post, name='post-update'),
    #path('posts/<uuid:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    #path('posts/<int:pk>/highlight/', api.PostHighlight.as_view()),
    path('posts/like/', likePost, name='likepost'),
    #path('posts/<int:pk>/delete/', views.PostDelete.as_view(), name='post-delete'),
    path('posts/<uuid:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('posts/myposts/', PostedByUserListView.as_view(), name='my-posts'),    
    # Add URLConf for admin to renew a post. /blog/post/<postinstance_id>/renew/1
    path('posts/<uuid:pk>/renew/', renew_post_admin, name='renew-post-admin'),
    path(r'renewed/', RenewedAllListView.as_view(), name='all-renewed'),
    #path('posts/snippets/', SnippetListView.as_view(), name='snippet-list'),
    #path('posts/snippets/create', SnippetAdd, name='snippet-create'),
    #path('posts/snippets/<int:pk>', SnippetDetailView.as_view(), name='snippet-details'),
    # The pattern only matches if pk is a correctly formatted uuid
    path('maintainers/', maintainers_list, name='maintainers'), # <a href="{% url 'maintainers' %}">URLText</a>
    path('maintainers/<int:pk>', maint_details, name='maintainer-detail'),# <a href="{% url 'auth-det' %}">URLText</a>
    path('maintainers/create/', create_maint, name='maintainer-create'),
    path('maintainers/<int:pk>/update/', MaintainerUpdate.as_view(), name='maintainer-update'),
    path('maintainers/<int:pk>/delete/', MaintainerDelete.as_view(), name='maintainer-delete'),
    
] # <int/str/slug/uuid/path:pk/...>
# urlpatterns = format_suffix_patterns(urlpatterns)
# to append a set of format_suffix_patterns in addition to the existing URLs (support for format suffixes to our API endpoints)
# Using format suffixes gives us URLs that explicitly refer to a given format, not necessarily needed but,
# means our API will be able to handle URLs such as http://example.com/api/items/4.json.
'''
pip install httpie
http http://127.0.0.1:8000/snippets/
http http://127.0.0.1:8000/snippets/2/
We can control the format of the response that we get back, either by using the Accept header:
http http://127.0.0.1:8000/snippets/ Accept:application/json  # Request JSON
http http://127.0.0.1:8000/snippets/ Accept:text/html         # Request HTML
Or by appending a format suffix:
http http://127.0.0.1:8000/snippets.json  # JSON suffix
http http://127.0.0.1:8000/snippets.api   # Browsable API suffix
Similarly, we can control the format of the request that we send, using the Content-Type header.
# POST using form data
http --form POST http://127.0.0.1:8000/snippets/ code="print(123)"
{
  "id": 3,
  "snippet_title": "",
  "code": "print(123)",
  "linenos": false,
  "language": "python",
  "style": "friendly"
}
# POST using JSON
http --json POST http://127.0.0.1:8000/snippets/ code="print(456)"
{
    "id": 4,
    "snippet_title": "",
    "code": "print(456)",
    "linenos": false,
    "language": "python",
    "style": "friendly"
}
If you add a --debug switch to the http requests above, you will be able to see the request type in request headers.
'''
'''
path('users/', api.UserList.as_view(), name='users-list'),
path('users/<int:pk>/', api.UserDetail.as_view(), name='user-detail'),
path('api', api.api_root, name='api-root'), # Where api_root is a function in api.py if you are not using router for api viewset but better use next line 
path('api-list/', postViewSet, name='jobs-list'), 
path('api-list/', postList.as_view(), name='joblistApi'),
path('api-list/<int:id>/', postDetailViewSet, name='job-detail'),
path('api-list/<int:pk>/', postDetial.as_view(), name='jobdetailApi'),
path('api-list/<int:pk>/highlight/', api.JobHighlight.as_view(),name='job-highlight' ),
path('snippets/', views.SnippetList.as_view(), name='snippet-list'),
path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name='snippet-detail'),
path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view(), name='snippet-highlight'),
'''