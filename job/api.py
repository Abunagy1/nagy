from rest_framework import renderers
from rest_framework import mixins
from decimal import Context
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http.response import Http404, HttpResponse, JsonResponse
from django.template.defaultfilters import title
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework import generics
from job.filters import JobFilter
from rest_framework import serializers, status
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.response import Response
from .models import Job, Applicant
from account.models import User
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
from rest_framework.reverse import reverse
from .serializers import UserSerializer, GroupSerializer, JobSerializer, ApplicantSerializer
# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def jobViewSet(request, format=None):
    jobs = Job.objects.all()
    if request.method == 'POST':
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
@api_view(['GET', 'PUT', 'DELETE', ])
@permission_classes((permissions.AllowAny,))
def jobDetailViewSet(request, slug, format=None):
    try:
        job = Job.objects.get(slug=slug)
    except Job.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'PUT':
        serializer = JobSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = JobSerializer(job)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class JobList(generics.ListCreateAPIView):  # or ListAPIView
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class JobDetial(generics.RetrieveUpdateDestroyAPIView):  # RetrieveAPIView
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)
class JobViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        jobs = self.get_object()
        return Response(jobs.highlighted)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('users-list', request=request, format=format),
        'jobs': reverse('jobs-list', request=request, format=format)
    })
class JobHighlight(generics.GenericAPIView):
    queryset = Job.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]
    def get(self, request, *args, **kwargs):
        jobs = self.get_object()
        return Response(jobs.highlighted)