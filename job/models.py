#from django.contrib.auth.models import User
from account.models import User
from django.db import models
from django.template.defaultfilters import slugify # from django.utils.text import slugify
from django.urls import reverse
#import os

def upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/apply/<title>/<filename>
    # return os.path.join("uploads", filename)
    return 'apply/{0}/{1}'.format(instance.name, filename)
def directory_path(instance, filename):
    imgName, extension = filename.split('.')
    imgName = instance.title
    return 'jobs/%s.%s' %(imgName, extension)
JOB_TYPE = (
    ('Full Time', 'Full Time'),
    ('Part Time', 'Part Time'),
)
class Job(models.Model):
    employer = models.OneToOneField(User, related_name='recruiter', on_delete=models.CASCADE,)
    #owner = models.ForeignKey('auth.User', related_name='job_owner', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True, default='')
    job_type = models.CharField(max_length=15, choices=JOB_TYPE, default='Full Time',)
    description = models.TextField(max_length=1000)
    published_at = models.DateTimeField(auto_now_add=True)
    Vacancy = models.IntegerField(default=1)
    salary = models.IntegerField(default=0)
    experience = models.IntegerField(default=1)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)  # relations
    job_icon = models.ImageField(upload_to=directory_path, null=False, blank=True)
    slug = models.SlugField(null=True, blank=True)
    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Job, self).save(*args, **kwargs)
    def get_absolute_url(self):
        # or ==>  kwargs={ "slug": str(self.slug] })
        return reverse('details', kwargs={'slug': self.slug})
    class Meta:
        ordering = ['title']
    def __str__(self) -> str:
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=25)
    def __str__(self) -> str:
        return self.name
    class Meta:
        verbose_name_plural = 'Categories'

class Applicant(models.Model):
    name = models.CharField(max_length=100)
    applicant = models.OneToOneField(User, related_name='applicant', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='apply', on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    website = models.URLField()
    cv = models.FileField(upload_to=upload_path, null=True, blank=True)
    cover_letter = models.TextField(max_length=500)
    date_of_application = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.name