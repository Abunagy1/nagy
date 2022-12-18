import datetime
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .forms import Apply, PostJob
from django.shortcuts import render
from .models import Job
from .filters import JobFilter
from django.core.paginator import Paginator
def index(request):
    jobs = Job.objects.all()
    return render(request, 'job/index.html', {'jobs': jobs})

def job_list(request):
    jobs_list = Job.objects.all()
    filter = JobFilter(request.GET, queryset=jobs_list)
    jobs_list = filter.qs
    paginator = Paginator(jobs_list, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'jobs': page_obj, 'filter': filter, 'jobs_list':jobs_list}  # jobs is the key name to use in template
    return render(request, 'job/jobs.html', context)

def job_details(request, slug):
    job_details = Job.objects.get(slug=slug)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Apply(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            apply = form.save(commit=False)
            apply.job = job_details  # apply is the related_name in applicant model to job model
            apply.save()
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/jobs/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = Apply()
    context = {'job': job_details, 'form': form}
    return render(request, 'job/job_details.html', context)
@login_required
def job_post(request):
    if request.method == 'POST':
        form = PostJob(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.employer = request.user
            post.save()
            return redirect(reverse('jobs:job_list'))
            #return HttpResponseRedirect('/success/url/')
    else:
        form = PostJob()
    return render(request, 'job/add_job.html', {'form': form})