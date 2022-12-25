import datetime
#from tkinter import Image
from PIL import Image
from django import forms
from django.conf import settings
from django.utils import timezone
#from django.contrib.auth.models import User  # Required to assign User as a commenter
from account.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
import os, uuid # uuid Required for unique post instances
from django.forms import ModelForm, Textarea
from datetime import date
from pygments.lexers import get_all_lexers  # get all lexical resources
from pygments.styles import get_all_styles  # get all styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.urls import reverse  # To generate URLS by reversing URL patterns
'''
Primary_key At the side of one user or thing Primary key=True
Foreign_Key At any Table(many side) refer to the original primary_key table refer to one
'''
# a permission to allow employees to create a post & Maintainers by define a nested tuple containing permission name, permission display value.
# The current user's permissions are stored in a template variable {{ perms }} e.g. {% if perms.catalog(appName).can_edit %} True/False
LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

def video_directory_path(instance, folder):
    return os.path.join('video', str(instance.user.id), str(instance.video_id))

def photo_directory_path(instance, folder):
    return os.path.join('image', str(instance.user.id), str(instance.photo_id))

def upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/posts/<user_name>/<filename>
    # return os.path.join("uploads", filename)
    return 'posts/{0}/{1}'.format(instance.name, filename)

def directory_path(instance, filename):
    imgName, extension = filename.split('.')
    imgName = instance.title
    return 'posts/%s.%s' %(imgName, extension)

class Snippet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    snippet_title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField(blank=True)
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    highlighted = models.TextField(blank=True)
    class Meta:
        ordering = ('created', )
    def __str__(self):
        return self.snippet_title
    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = self.linenos and 'table' or False
        options = self.snippet_title and {'snippet_title': self.snippet_title} or {}
        formatter = HtmlFormatter(
            style=self.style, linenos=linenos, full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)

class PostViews(models.Model):
    IPAddres= models.GenericIPAddressField(default="45.243.82.169")
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    def __str__(self):
        return '{0} in {1} post'.format(self.IPAddres,self.post.title)
# you can create model/class for Comment here or go to forms.py

class Comment(models.Model):
    # id = models.AutoField(primary_key=True) # the same field in post model for multi-inheritance (comment_id)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # name = models.CharField(max_length=50) # i can get them from thecommenter field
    # email = models.EmailField(max_length=100)
    content = models.TextField()
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    created_on = models.DateTimeField(auto_now_add=True)
    #votes = models.ForeignKey('Vote', on_delete=models.CASCADE, related_name="comment_votes")
    commenter = models.ForeignKey(User, related_name='commenters', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    # votes = GenericRelation('PostInstance', related_query_name='comment_votes')
    # if we want to make a comment replies you have to add self relationship to comment model
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True) # now we can make sub-comment of another comment
    class Meta:
        ordering = ('-created_on',)
    def __str__(self): # self.content[0:13] + "..." + "by" + " " + self.user.username
        return 'Comment {} by {}'.format(self.content, self.commenter.username)  # 

class Maintainer(models.Model):
    """Model representing Maintainer."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    #date_of_birth = models.DateField(null=True, blank=True) # if you want them put them in account profile model
    #date_of_death = models.DateField('Died', null=True, blank=True) # if died, django will capitalize it for you to be Died
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='maintainers')
    class Meta:
        ordering = ['last_name', 'first_name'] # # must be exist if you are gonna use pagination or modelName_set.all() method in template
    def get_absolute_url(self):
        """Returns the url to access a particular Maintainer instance."""
        return reverse('blog:maintainer-detail', kwargs={"pk": str(self.id)})
    def __str__(self) -> str:
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.last_name, self.first_name)
class Genre(models.Model):
    POST_GENRE = ( # we define a tuple containing tuples of key-value pairs
        ('AI', 'Arteficial Intelligence'),
        ('WEB', 'Web Developing'),
        ('ELEC', 'Electrical Engineering'),
        ('MECH', 'Mechanical Engineering'),)
    """Model representing a post genre (e.g. Science Fiction, Non Fiction).""" 
    genre = models.CharField(max_length=10, choices=POST_GENRE, blank=True, default='A', help_text='Enter a Post genre (A(AI), W(WEB), E(Electrical), M(Mechanical))')
    def __str__(self):  # No verbose name has been defined, so the field will be called Name in forms.
        """String for representing the Model object (in Admin site etc.)"""
        return self.genre

class Tag(models.Model):
    name = models.CharField(max_length=40)
    def __str__(self) -> str:
      return self.name

STATUS = (
    (0, "Draft"),
    (1, "Publish")
)
TYPES_CHOICE = (
    ('img', 'Image'),
    ('vid', 'Video'),
    ('txt', 'Text'),
    ('lnk', 'Link'),
)

POST_LANG = ( # we define a tuple containing tuples of key-value pairs
    ('AR', 'Arabic'),
    ('ENG', 'English'),
    ('Ger', 'Germany'),
    ('Fr', 'French'),)
# related_name attribute allows us to name the attribute that we use for the relation from the related object back to this one
class Post(models.Model):
    """Model representing a post (but not a specific copy of a post)."""
    # id = models.AutoField(primary_key=True) # the same field in comment model for multi-inheritance (post_id)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.CharField(max_length=200, db_index=True, blank=False, default='')
    slug = models.SlugField(max_length=200, db_index=True, unique=True, blank=True, editable=True) # add unique=True in slug (never repeat) if editable=False it will not shown in admin page
    tag = models.ManyToManyField(Tag, blank=True, help_text="Select a tag for this post", related_name='post_tags')
    post_type = models.CharField(max_length=5, choices=TYPES_CHOICE, default='txt')
    created_at = models.DateTimeField('publish_date', auto_now_add=True) # 'publish_date' is verbose_name
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_creators") # show creator of the post(admin or employee user)
    # votes = GenericRelation('Vote', related_query_name='post_votes') # enables filtering, ordering, and other query operations on Vote from Post
    post_img = models.ImageField(upload_to=directory_path, null=False, blank=True, default ="img.png") # upload_to ="/media/post_images"
    maintainer = models.ForeignKey(Maintainer, on_delete=models.SET_NULL, blank=True, null=True, related_name='post_maintainers')
    # Foreign Key used because post can only have one maintainer, but maintainers can have multiple posts
    # 'Maintainer' as a string rather than object if it hasn't been declared yet in file & declared below. SET_NULL/CASCADE/PROTECT/RESTRICT...
    content = models.TextField(max_length=1000, help_text="Enter descriptive subject")
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this post", related_name='post_genres')
    urls = models.URLField(max_length=300, blank=True, default="")
    video = models.FileField(upload_to=upload_path, null=True, blank=True)
    snippet = models.OneToOneField(Snippet, on_delete=models.CASCADE, related_name='post_snippets', blank=True, null=True)
    views = models.IntegerField(default=0)
    # ManyToManyField used because a genre can contain many posts and a Post can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    post_language = models.CharField(max_length=10, blank=True, choices=POST_LANG, default='ENG', help_text="Select the post's language (e.g. Arabic, English, German etc.)",) # Languages is a verbose/Class_name that is binded to post class
    # To keep draft and published posts separated when we render them out with templates use this status field
    status = models.IntegerField(choices=STATUS, default=0)
    score = models.IntegerField(default=0)
    userUpVotes = models.ManyToManyField(User, blank=True, related_name='posrUpVotes')
    userDownVotes = models.ManyToManyField(User, blank=True, related_name='postDownVotes')
    @property
    def is_old(self):
        '''
        # created_at can't be null when first creat a post
        elif self.created_at == NULL:
            return 'Doesn\'t Exist'
        '''
        if date.today() - self.created_at  > 60:
            return True
        elif self.created_at == date.today:
            return False
        return 'Current'
    @property
    def number_of_comments(self):
        return Comment.objects.filter(post=self).count()  # get the post object of connected post using post variable in Comment model
    @property
    def views_count(self):
        return PostViews.objects.filter(post=self).count()

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created_at <= now
    """
    @property
    def views_count(self):
        return PostViews.objects.filter(post=self).count()  
    """
    class Meta:
        ordering = ['title', 'maintainer', '-created_at']
        verbose_name_plural = 'Posts'

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin.""" 
        return ', '.join([genre.genre for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular post instance."""
        return reverse('blog:details', kwargs={"pk": str(self.id)})  # kwargs={ "slug": self.slug }) /  kwargs={"id": str(self.id)}
        # return reverse('post-detail', kwargs={'pk': self.pk})
    def __str__(self) -> str:
        """String for representing the Model object. self.title + " by " + self.author"""
        #template = '{0.creator.username} {0.title}'
        return f'{self.creator.username}\'s Post- {self.title}' # return self.creator.username + ', ' + self.title[:40]
        #return '{} {}'.format(self.creator.username, self.title)
        #return self.title # template.format(self)
    # we made save function only wen we want to make any changes before save and must use Super
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        img = Image.open(self.post_img.path) # specify path, pip install PILLOW, from PIL import Image
        if img.height > 400 or img.width > 400:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.post_img.path)
        return super(Post, self).save(*args, **kwargs)

class Vote(models.Model):  # or multi-inherit Vote(Comment, Post):
    """
    FAVORITE = 'F'
    LIKE = 'L'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (LIKE, 'Like'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    """
    DOWN_VOTE = -1
    UP_VOTE = 1
    NO_VOTE = 0
    VOTE_TYPES = ((DOWN_VOTE, "Downvote"), (UP_VOTE, "Upvote"), (NO_VOTE, "Unvote"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    vote_type = models.IntegerField(choices=VOTE_TYPES, default=NO_VOTE)
    score = models.IntegerField(default=0)
    voters = models.ManyToManyField(User,  related_name='voters')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    #content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    #object_id = models.PositiveIntegerField() # a field that can store primary key values from the models you’ll be relating to
    # object_id = models.UUIDField(default=uuid.uuid4) # not neccesary to be same type as post pk
    #content_object = GenericForeignKey
    def __str__(self):
        return (self.vote, self.score)
    """
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
    """
# this model for the library books instances that's been borrowed to students and have due date, tweaked to adapt post insyances but useless here
class PostInstance(models.Model): # Represenrt a Many To Many relation btn both post and users
    """Model representing a specific copy of a post (i.e. that's been commented from the blog)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, help_text="Unique ID for this particular post across whole blog")
    post = models.ForeignKey(Post, on_delete=models.RESTRICT, null=True)
    renew_on = models.DateField(null=True, blank=True, default=datetime.date.today)
    imprint = models.CharField(max_length=200) # UUIDField is used for the id field to set it as the primary_key for this model allocates a globally 
    commenter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="commenter") # commenter on post/borrower for book
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField() # a field that can store primary key values from the models you’ll be relating to
    # object_id = models.UUIDField(default=uuid.uuid4) # not neccesary to be same type as post pk
    # content_object = GenericForeignKey
    @property 
    def is_overdue(self):
        if self.renew_on and date.today() > self.renew_on:
            return True
        return False
    POST_STATUS = ( # we define a tuple containing tuples of key-value pairs
        ('N', 'New'),
        ('O', 'Old'),
        ('C', 'Current'),
        ('R', 'Renewed'),
    )
    status = models.CharField(max_length=1, choices=POST_STATUS, blank=True, default='N', help_text='Post status')
    class Meta:
        ordering = ['renew_on']
        permissions = (("can_renew", "Set post new date"), ("can_edit", "Edit post details"))
        #unique_together=('post', 'content_type', 'object_id') # Solve the unique per page
        #indexes = [models.Index(fields=["content_type", "object_id"]),]
    def __str__(self):
        """String for representing the Model object."""  # we use old(format)/new(f'' string interpolation syntax
        return '{0} ({1})'.format(self.id, self.post.title) # or better use f'{self.id} ({self.post.title})'  f == format f' ' (new feature)
"""
class PostViews(models.Model):
    IP = models.GenericIPAddressField(default="45.243.82.169")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    def __str__(self):
        return '{0} in {1} post'.format(self.IP, self.post.title)
"""
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name="likes")


