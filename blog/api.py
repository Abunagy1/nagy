from rest_framework import mixins
from decimal import Context
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from rest_framework.response import Response
from django.http.response import Http404, HttpResponse, JsonResponse # from django.http import Http404
from django.template.defaultfilters import title
from rest_framework.views import APIView
from rest_framework import generics
from blog.filters import PostFilter
from rest_framework import serializers, status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User, Group
from account.models import User
from rest_framework import permissions, renderers, viewsets
from blog.permissions import IsOwnerOrReadOnly # from .permissions import IsOwnerOrReadOnly
from rest_framework.reverse import reverse
from .serializers import SnippetSerializer, UserSerializer, GroupSerializer, PostSerializer # from blog.serializers import 
from blog.models import Snippet
from .models import Post
@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def postViewSet(request, format=None):
    posts = Post.objects.all()
    if request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE', ])
@permission_classes((permissions.AllowAny,))
def postDetailViewSet(request, slug, format=None): # pk is used
    try:
        post = Post.objects.get(slug=slug) # (pk=pk) is used
    except Post.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PostList(generics.ListCreateAPIView):  # or ListAPIView
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostDetial(generics.RetrieveUpdateDestroyAPIView):  # RetrieveAPIView
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug' # pk
    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        posts = self.get_object()
        return Response(posts.highlighted)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('users-list', request=request, format=format),
        'jobs': reverse('jobs-list', request=request, format=format)
    })

class PostHighlight(generics.GenericAPIView):
    queryset = Post.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]
    def get(self, request, *args, **kwargs):
        posts = self.get_object()
        return Response(posts.highlighted)

"""
1.	The @api_view decorator for working with function based views.
2.	The APIView class for working with class-based views.
"""
# The root of our API is going to be a view that supports listing all the existing snippets, 
# or creating a new snippet.

@api_view(['GET', 'POST'])
def snippet_list(request, format=None): # format keyword to add support for format suffixes to our API endpoints
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# to retrieve, update or delete the snippet.
@api_view(['GET', 'PUT', 'DELETE'])
def snippet_detail(request, pk, format=None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# or class based views

class SnippetList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SnippetDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)
    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# using the mixin classes

class SnippetList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class SnippetDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# or much more better way
from blog.models import Snippet
from blog.serializers import SnippetSerializer
from rest_framework import generics
class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

# You can replace both SnippetList & SnippetDetail by just one single SnippetViewset class views
# REST framework includes an abstraction for dealing with ViewSets, that 
# allows the developer to concentrate on modeling the state and interactions of the API,
# and leave the URL construction to be handled automatically, based on common conventions
# You can replace both SnippetList & SnippetDetail by just one single SnippetViewSet class views
class SnippetViewSet(viewsets.ModelViewSet): # we've used the ModelViewSet class in order to 
    # get the complete set of default read and write operations
    """
    This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    # We're still setting the queryset and serializer_class attributes exactly as we did
    # when we were using regular views, but we no longer need to provide the same information to two separate classes
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    # IsOwnerOrReadOnly is a special permission class written in permission file to give only the owner ability
    # to edit or delete the object rather than the general class for only looged in users IsAuthenticatedOrReadOnly
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
    # IsAuthenticatedOrReadOnly permission class ensure that authenticated requests get read-write access,
    # and unauthenticated requests get read-only access.
    # We also use @action decorator to create a custom action, named highlight
    # This action decorator can be used to add any custom endpoints
    # that don't fit into the standard create/update/delete style
    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs): # in urls.py you can bind directly binding the http methods to the required action method name EX:
        # snippet_highlight = SnippetViewSet.as_view({'get': 'highlight'}, renderer_classes=[renderers.StaticHTMLRenderer])
        # and in the same file below path('snippets/<int:pk>/highlight/', snippet_highlight, name='snippet-highlight'), just var_name
        # instead of views.SnippetHighlight.as_view, but rather than designing urls conf. ourselves, becuase we using ViewSet rather than View Classes
        # it's better to wiring up resources into views and urls can be handled automatically, using a Router ==> EX:
        # router.register(r'users', views.UserViewSet)
        snippet = self.get_object() # Custom actions will respond to GET requests by default
        return Response(snippet.highlighted) # We can use the methods argument if we wanted an action that responded to POST requests
        # The URLs for custom actions by default depend on the method name itself.
    # Passing additonal information 'owner' field to The create() method of our serializer,
    # along with the validated data from the request. By overriding it using perform_(create) method
    def perform_create(self, serializer): # allows us to modify how the instance save is managed
        serializer.save(owner=self.request.user) # to get the snippet creator owner in models.py
# if relationships within API are represented by using primary keys
# You have to improve the cohesion and discoverability of API, by instead using hyperlinking for relationships.
# So we have endpoints for 'snippets', posts and 'users', but we don't have a single entry point to our API.
# To create one, we'll use a regular function-based view and the @api_view decorator

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format), # reverse to return fully-qualified URLs
        'snippets': reverse('snippet-list', request=request, format=format),
        'comments': reverse('comment-list', request=request, format=format),
        'posts': reverse('post-list', request=request, format=format)
    }) # URL patterns are identified by convenience names that we will declare later on in our blog/urls.py
    
# to view the code highlighting endpoints we don't want to use JSON, but instead just present an HTML representation
# There are two styles of HTML renderer provided by REST framework, one for dealing with HTML rendered using templates,
# the other for dealing with pre-rendered HTML. The second renderer is the one we'd like to use for this endpoint.
# we'll use the base class for representing instances, and create our own .get() method.
# Because We're not returning an object instance, but instead a property of an object instance.
class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]
    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


"""
# with regard to the user we can use the following :
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

"""

# REST framework includes an abstraction for dealing with ViewSets, that 
# allows the developer to concentrate on modeling the state and interactions of the API,
# and leave the URL construction to be handled automatically, based on common conventions
# You can replace both UserList & UserDetails by just one single UserViewset class views
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list`, retrieve and `detail` actions.
    We've used the ReadOnlyModelViewSet class to automatically provide the default 'read-only' operations
    API endpoint that allows users to be viewed or edited.
    """
    #permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
# We're still setting the queryset and serializer_class attributes exactly as we did
# when we were using regular views, but we no longer need to provide the same information to two separate classes
# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """

    """
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]