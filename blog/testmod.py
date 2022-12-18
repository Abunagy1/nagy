from cgitb import html
from html.entities import html5
from pydoc import HTMLDoc
from django.db import models
import os, uuid
"""
There doesn't seem to be a class named ImagePerson in that file
which is what you are setting the through (the through table) to be in the M2M on Person.
So normally you omit the through declaration like you did on your other ManyToMany definitions. 
You only usually pass a custom one if there is some additional data you want to store on that model. 
Django allows the passing of a model or a string in most places...I'm rambling, not sure what your question is.
you dont normally need to declare a through table unless you want additional information (such as date added or something). 
Django will create the through table by itself and manage it for you. However you may also declare 
a through field if you are operating on a legacy database that already has existing through tables django should use instead of 
creating it's own. You will get this error if you neglect to import the model to the file referencing it, or forget to define it.
"""
def video_directory_path(instance, folder):
    return os.path.join('video', str(instance.person.id), str(instance.video_id))

def photo_directory_path(instance, folder):
    return os.path.join('image', str(instance.person.id), str(instance.photo_id))

class Person(models.Model):
    bio = models.TextField()
    filmography = models.ManyToManyField('Filmography')
    photos = models.ManyToManyField('Image', through='ImagePerson', through_fields=('person', 'photo'))
    class Meta:
        abstract = True
    def __str__(self):
        return '[{0}-{1}]'.format(self.__class__.__name__, self.id)
    def __repr__(self):
        return self.__str__()

class Profile(Person):
    first_name = models.CharField(max_length=128, verbose_name="first name")
    last_name = models.CharField(max_length=128, verbose_name="last name")
    dob = models.DateField()
    class Meta:
        index_together = ["first_name", "last_name"]
        db_table = 'Profile'

class Image(models.Model):
    name = models.CharField(max_length=128)
    photo_id = models.UUIDField(verbose_name='photo id', default=uuid.uuid4, editable=False, unique=True)
    photo = models.ImageField(upload_to=photo_directory_path)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    class Meta:
        db_table = 'Image'
    def __str__(self):
        return '[{0}- {1}]'.format(self.__class__.__name__, self.id)
    def __repr__(self):
        return self.__str__()

class Video(models.Model):
    name = models.CharField(max_length=128)
    video_id = models.UUIDField(verbose_name='video id', default=uuid.uuid4, editable=False, unique=True)
    video = models.FileField(upload_to=video_directory_path)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    class Meta:
        db_table = 'Video'
    def __str__(self):
        return '[{0}-{1}]'.format(self.__class__.__name__, self.id)
    def __repr__(self):
        return self.__str__()

class Filmography(models.Model):
    filmography = models.CharField(max_length=128, db_index=True)
    class Meta:
        db_table = 'Filmography'
    def __str__(self):
        return '[{0}-{1}]'.format(self.__class__.__name__, self.id)
    def __repr__(self):
        return self.__str__()

class Character(Person):
    name = models.CharField(max_length=128)
    class Meta:
        db_table = 'Character'

class Crew(models.Model):
    name = models.CharField(max_length=256)
    members = models.ManyToManyField(
        'Profile',
        through='MovieCrew',
        through_fields=('crew', 'profile'),
    )
    class Meta:
        db_table = 'Crew'
        def __str__(self):
            return '{0}: {1}'.format(self.__class__.__name__, self.name)
    def __repr__(self):
        return self.__str__()

class MovieCrew(models.Model):
    crew = models.ForeignKey(
        'Crew',
        on_delete=models.CASCADE,
    )
    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=256)
    class Meta:
        db_table = 'MovieCrew'

class Genre(models.Model):
    genre = models.CharField(max_length=128, db_index=True)
    class Meta:
        db_table = 'Genre'

class Movie(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    summary = models.CharField(max_length=256)
    story = models.CharField(max_length=256)
    release_date = models.DateField()
    crew = models.OneToOneField(
        'Crew',
        on_delete=models.CASCADE,
    )
    genre = models.ManyToManyField('Genre')
    photos = models.ManyToManyField('Image')
    videos = models.ManyToManyField('Video')
    class Meta:
        db_table = 'Movie'
        get_latest_by = 'release_date'
    def __str__(self):
        return '[{0}-{1}]'.format(self.__class__.__name__, self.name)
    def __repr__(self):
        return self.__str__()






"""
pip install django-crispy-forms
INSTALLED_APPS = [
    ...
    'crispy_forms',
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'
{% load crispy_forms_tags %}
<html>
  <head>
  <title></title>
  </head>
<body> 
...
<form method="POST" style="margin-top: 1.3em;">
          {{ comment_form | crispy }}
          {% csrf_token %}
          {{comment_form.as_p}}
          <button type="submit" class="btn btn-primary  btn-lg">Submit</button>
 </form>
</body>
"""









