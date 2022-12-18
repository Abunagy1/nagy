import os
import uuid
from django.conf import settings
from django.forms import modelformset_factory, inlineformset_factory
from django.utils import timezone
from .models import Post, Maintainer, PostInstance, Genre, Comment, PostViews, Vote, Snippet, Like
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic # Class Based Views, Context Var == object_list/detail... OR model_name_list/detail...
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import datetime
from django.core.exceptions import PermissionDenied
from account.models import User, Profile
from django.http import HttpResponse, HttpResponseRedirect
from .filters import PostFilter, MaintainerFilter
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.urls import reverse, reverse_lazy
from .forms import CommentForm, SnippetForm, SnippetUpdateForm, VoteForm, PostForm, PostUpdateForm, MaintainerForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# ... index view is for home view only 
################################################
# ---------- Start home/List View ------------ #
################################################
# generic based view for list all posts 
# this class used to show home page alternative to index function to list all posts like ==> PostList(listView)
# you can ovveride context var. name & queryset method to customize the list of all posts
class PostListView(generic.ListView): # path('', PostListView.as_view(), name='home'),
    """Generic class-based view for a list of posts."""
    model = Post # HTML Ctx Var == post_list/object_list or write your own here uing context_object_name = 'my_post_list'   
    paginate_by = 5
    context_object_name = 'posts' # your own name for the list as a template variable 
#   queryset = Post.objects.filter(title__icontains='war')[:5] # Get 5 posts containing title war instead of all posts
    template_name = 'blog/index.html' # my_arbitrary_template_name_list.html' # Specify your own template name/location
# You can Override the get_queryset() method rather than using queryset attribute above as shown below
# You Can for Ex add a variable named "some_data" to the context (it would then be available as a template variable).
    # if you don't want to list all posts w/o filtering
    def get_queryset(self): # to override get_queryset method 
        """
        Return the last five published posts (not including those set to be published in the future).
        """
        return Post.objects.filter(created_at__lte=timezone.now()).order_by('-created_at')[:5]
        # created_at__lte=timezone.now() returns a queryset containing Posts whose created_at is
        # less than or equal to now - that is, earlier than or equal to - timezone.now, not in future.
    """
    def get_context_data(self, **kwargs): # to override get_context_data method
        # Call the base implementation first to get the context
        context = super(PostListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context
    """
# to show all posts of one user
class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 3
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(creator=user).order_by('-created_at')

# next is the total function with all options of paginations
@login_required
def index(request):
    # to get only new pupluished posts (not drafts posts)  use queryset = Post.objects.filter().order_by('-created_at')
    # object_list = Post.objects.filter(status=1).order_by('-created_at')
    #posts_list = Post.objects.filter(created_at__lte=timezone.now(), status=1).order_by('-created_at')[:5] # 
    posts = Post.objects.all()
    filter = PostFilter(request.GET, queryset=posts)
    has_filter = any(field in request.GET for field in set(filter.get_fields()))
    f = filter.qs
    paginator = Paginator(f, 3)  # Paginator object Show filtered 3 posts per page.
    page_obj = request.GET.get('page') # page object on the request
    page = paginator.get_page(page_obj) # give filtered page to Paginator to be Paginated float page numbers or (page() for int. doesn't matter)
    # Generate counts of some of the main objects
    num_posts = Post.objects.all().count() # get all post instances counts
    num_instances = PostInstance.objects.all().count() # get all commented Post instances count
    num_instances_new = PostInstance.objects.filter(status__exact='N').count() # if available book/job will be 'a'
    num_maintainers = Maintainer.objects.count()  # The 'all()' is implied by default.
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1) # get value of 'num_visitss' session key in session attr. dict. obj
    request.session['num_visits'] = num_visits+1 # Sessions allow you to store/get/update/del...arbitrary data per browser
    # Render the HTML template index.html with the data in the context variable.
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path + '/posts')
    if request.method == 'GET':
        try:
            postsList = paginator.page(page_obj) # give filtered page to Paginator to be Paginated for for integer page numbers
        except PageNotAnInteger:
                # If page is not an integer deliver the first page
            postsList = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            postsList = paginator.page(paginator.num_pages)
        context = {'num_posts': num_posts, 'num_instances': num_instances, 'img_list': img_list,
                 'num_instances_new': num_instances_new, 'num_maintainers': num_maintainers,
                 'num_visits': num_visits, 'posts': page, 'postsList': postsList, 'filter': filter, 'has_filter':has_filter} # posts is the key name to use in template
        return render(request, 'blog/index.html', context) # you can just write only posts.html to refer to templates/blog/posts.html
    else:
        return redirect(reverse('/'))
##########################################
#------------- Create View --------------#
##########################################
# Classes created for the forms challenge # this class is for one Model but i didn't know how to get snippet too
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'maintainer', 'content', 'snippet', 'genre', 'post_language', 'video', 'post_type', 'post_img', 'status' ]
    template_name = 'blog/add_post.html'
    permission_required = ''
    def get_success_url(self):
        messages.success(self.request, 'Your post has been created successfully.')
        return reverse_lazy("blog:index")
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.slug = slugify(form.cleaned_data['title'])
        obj.save()
        return super().form_valid(form)

# or using function using form from the existing model
@login_required
def add_post(request):
    if request.method == 'POST':
        #creator=request.user
        # post model instance need other related models instances to be created
        # (creator & snippet => OneToOne relation, maintainer => ForeignKey and Tag & Genre => ManyToMany)
        # while creator set to be not null but as maintainer null & blank is true and snippet too
        # snippet needed if i check the add_code check box so need to be asigned to the same post instances but
        # maintainer is not asigned by the same post creator, it must be assigned by admin only
        # as well tag & genre too has ManyToMany but will be selected from multi choice drop menus
        post_form = PostForm(request.POST, request.FILES)
        snippet_form = SnippetForm(request.POST)
        if post_form.is_valid() and snippet_form.is_valid():
            post = post_form.save(commit=False)
            snpt = snippet_form.save()
            post.creator = request.user
            post.snippet = snpt
            post.save(),
            snpt.save()
            return redirect('blog:details',  post.pk) # post.get_absolute_url()  /   'blog:details', post.id args={'pk': post.pk}
    else:
        post_form = PostForm()
        snippet_form = SnippetForm()
    return render(request, 'blog/add_post.html', {'post': post_form, 'snpt': snippet_form})

# Same add_post method but to accomply with conditional field add_code cleaned_data get(both methods works fne)
@login_required
def add_(request, **kwargs):
    #snpt = Snippet.objects.create(post = request.post, snippet_id = request.post.id)
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        snippet_form = SnippetForm(request.POST)
        if post_form.is_valid():
            add_code = post_form.cleaned_data['add_code']
            if add_code:
                if snippet_form.is_valid():
                    post = post_form.save(commit=False)
                    snpt = snippet_form.save()
                    post.creator=request.user
                    post.snippet = snpt
                    #post.slug = slugify(post_form.cleaned_data['title'])
                    post.save()
                    return redirect('blog:details')
                else:
                    return redirect('blog:add')
            else:
                post = post_form.save(commit=False)
                post.creator=request.user
                post.save()
                return redirect('blog:details')
        else:
            messages.error(request, _('Please correct the following error.'))
    else:
        post_form = PostForm()
        snippet_form = SnippetForm()
    return render(request, 'blog/add_post.html', {'post': post_form, 'snpt': snippet_form})

##########################################
# --------- Start Update View ---------- #
##########################################
# this class is for one form but i didn't know how to make it get the snippert too for edit
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'slug', 'tag', 'content', 'genre', 'post_language', 'urls', 'video', 'post_type', 'post_img', 'status', 'snippet', ]
    permission_required = ''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        update = True
        context['update'] = update
        return context
    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been updated successfully.')
        return reverse_lazy("blog:index")
    def get_queryset(self):
        return self.model.objects.filter(creator=self.request.user)

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post_form = PostUpdateForm(request.POST, request.FILES, instance=post)
        if post.snippet.code:
            snippet_form = SnippetUpdateForm(request.POST, instance=post.snippet)
            if post_form.is_valid() and snippet_form.is_valid():
                snippet_form.save(), post_form.save()
                messages.success(request, _('Your post has been successfully updated!'))
                return redirect('blog:details',  post.pk)
            else:
                messages.error(request, _('Please correct the following error.'))
                return redirect('blog:post-update', pk=post.pk)
        elif post_form.is_valid():
                post_form.save()
                messages.success(request, _('Your post has been successfully updated!'))
                return redirect('blog:details', post.pk)
        else:
            messages.error(request, _('Please correct the following error.'))
    else:
        post_form = PostUpdateForm(instance=post)
        context = {'post': post_form}
        if post.snippet.code:
            snippet_form = SnippetUpdateForm(instance=post.snippet)
            context = {'post': post_form, 'snpt': snippet_form}
    return render(request, 'blog/post_form.html', context)
##########################################
# --------- Start Detail View ---------- #
##########################################
"""
# To use related_name => syntax: instance.realated_name.methods() to get many instances w.r.t one (posts w.r.t user / comments w.r.t post)

first_user = User.objects.first()
first_user.post_creators.all() # (related_name = post_creators) in Post model(Many-Side) to relate User model(One-Side) to get all user posts
first_user.recruiter.all()  # (related_name = recruiter) in Job model to relate User model to get all user created jobs
first_user.voters.all() # (related_name = voters) to Vote model to get all user votes

first_post = Post.objects.first()
first_post.comments.all() # related_name = comments in Comment Model(Many-Side) to relate Post model(One-Side) to get all post comments
first_post.commenters.all() # related_name='commenters' in Comment Model(Many-Side) to relate User model(One-Side) to get all commenters

"""
@login_required
def post_details(request, pk):
    #template_name = 'post_details.html' # Show that we can use attributes in fn. based rather than render(req.,blog/post_dwtails.html, contxt)
    post = get_object_or_404(Post, id=pk) # or the usual post = Post.objects.get(slug=slug)
    # using related_name = comments in Comment Model (Many-Side) we can get all post comments that's active=True only
    comments = post.comments.filter(active=True) # This queryset retrieves all the approved comments from the database instead of comment_set.filter
    post.views += 1
    post.save()
    '''
    this function ensures that if THE IPAdress has seen this post it will do
    nothing if he sees the post for the first time it will create an object in the database and count it as a view.
    Don't forget to make migrations, migrate and register PostViews class in admin.py
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    PostViews.objects.get_or_create(user=request.user, post=post_details).save()
    '''
    comnt = None
    replyDict={} # we will put the reply comments in dictionary (objects)
    if request.method == 'POST':
        # if a POST request is made, then form variable will hold the data of user input
        # create a form instance and populate it with data from the request:
        # request.POST is a dictionary-like object that lets you access submitted data by key name (template context field var)
        comments= Comment.objects.filter(post=post, parent=None) # get the first comment on the same post (parent comment)
        replies= Comment.objects.filter(post=post).exclude(parent=None) # get the other comments other than parent one (self-relationship)  
        for reply in replies:
            if reply.parent.id not in replyDict.keys(): # if parent comment id is not in the dictionary keys
                replyDict[reply.parent.id]=[reply]
            else:
                replyDict[reply.parent.id].append(reply)
        form = CommentForm(request.POST or None, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            comnt = form.save(commit=False)
            comnt.post = post # post field in comment model => related_name = comments related to post model
            comnt.commenter = request.user
            comnt.save()
            # Always return an HttpResponseRedirect after successfully dealing with Post request
            # redirect to a new URL:
            return HttpResponseRedirect(f'/blog/posts/{pk}')
            #return redirect(post.get_absolute_url())
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CommentForm()
    context = {'post': post, 'comnt': comnt, 'comments': comments, 'form': form, 'user': request.user, 'replyDict': replyDict}
    return render(request, 'blog/post_details.html', context)

def PostDetails(request, slug, uuid):
    post=Post.objects.filter(slug=slug, id=uuid).first()
    post.views= post.views +1
    post.save()
    comments= Comment.objects.filter(post=post, parent=None) # get the first comment on the same post (parent comment)
    replies= Comment.objects.filter(post=post).exclude(parent=None) # get the other comments other than parent one (self-relationship)
    replyDict={} # we will put the replies comment in dictionary (objects)
    for reply in replies:
        if reply.parent.id not in replyDict.keys(): # if parent comment id is not in the dictionary keys
            replyDict[reply.parent.id]=[reply]
        else:
            replyDict[reply.parent.id].append(reply)
    if request.method == "POST":
            content = request.POST.get('content') # getthe vontent field in the comment model (no model CommentForm) jus a Comment model
            post_id = request.POST.get('post_id') # get the id of the post related to the comment
            post = Post.objects.get(id=post_id) # get the4 post itself of this comment(already been existed from fist line above)
            parent_id = request.POST.get('parent_id') # comment id field name in the details.html template 
            if parent_id == "":
                comment=Comment(content=content, user=request.user, post=post) # construct a comment instance
                comment.save()
                messages.success(request, "Your comment has been posted successfully")
            else:
                parent= Comment.objects.get(id=parent_id)
                comment=Comment(content=content, user=request.user, post=post , parent=parent) # construct a reply
                comment.save()
            messages.success(request, "Your reply has been posted successfully")
            return redirect(f"/blog/{post.slug}")
    context={'post':post, 'comments': comments, 'user': request.user, 'replyDict': replyDict}
    return render(request, "blog/post_details.html", context)

# or using id 
def post_detailview(request, slug):
    post_obj = Post.objects.filter(slug=slug) # post_obj = Post.objects.filter(slug=slug).first()
    comments = Comment.objects.filter(post=post_obj) # to show post with comment
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            # content = request.POST.get('content','post_id')
            # request.POST is a dictionary-like object that lets you access submitted data by key name (template context field var)
            post_id =request.POST.get('post_id')  # {% if user.id == post.author.id %} for only author of post to edit in template
            # request.POST.get('post_id') returns the ID/pk of the selected Post, as a string.
            content = request.POST.get('content') # just one field in comment form to be edited, others generated automatically
            comment = Comment.objects.create(post = request.post, user = request.user, content = content, post_id = post_id)
            ################ or directly ##################
            comment = Comment(user = request.user, content= form.cleaned_data['content'], name=form.cleaned_data['name'], post=post_obj) # this is better
            comment.save()
            return redirect(request.post.get_absolute_url())
        else:
            form = CommentForm()
    context = {'form':form, 'post':post_obj, 'comments':comments}
    return render(request, 'blog/post_detail.html', context)


# if you put field ==> id = models.IntegerField(primary_key=True) in post model
def PostDetail(request, _id):
    try:
        post_obj = Post.objects.get(id =_id)  # get the post object by id (you can change to slug)
        # get the comments objects that has relation to same post(field in Comment model)
        comments = Comment.objects.filter(post = post_obj)
    except Post.DoeidtExist:
        raise Http404('Data does not exist')
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = Comment(name= form.cleaned_data['name'],
            content=form.cleaned_data['content'],
            post=post_obj)
            comment.save()
            return redirect(f'/blog/{_id}')
    else:
        form = CommentForm()
    context = {'data':post_obj, 'form':form, 'comments':comments,}
    return render(request,'blog/detailview.html',context)

# class based vies simpler one
class PostDetailView(generic.DetailView): 
    """Generic class-based detail view for a post."""
    model = Post
    lookup_field = 'uuid'
    template_name = 'post_details.html'
    def get_queryset(self):
        """
        Excludes any posts that aren't published yet.
        """
        return Post.objects.filter(created_at__lte=timezone.now())
"""
class V(mixins.UpdateModelMixin, GenericViewSet):
    `` some codes``
    lookup_field = 'uuid'
    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser], url_path='approve/(?P<uuid>[\w-]+)')
    def approve(self, request, uuid, *args, **kwargs):
        obj = self.get_object()
        `` some codes ``
"""
# a complex one is just one view for all things
# one class based view for both list and details view
# (you can merge previous function based views in here)
# define a function for list view and function for details
class PostView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    template_name = 'blog/post.html' # Assigned HTML template to a variable name template_name for future reference
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # since our slug field is not unique, we need the primary key to get a unique post
        pk = self.kwargs['pk'] # get the object pk from arguments and put it in pk var
        slug = self.kwargs['slug'] # get the object pk from arguments and put it in pk var
        form = CommentForm()
        post = get_object_or_404(Post, pk=pk, slug=slug) # Assigning the Post object inside the post variable
        comments = post.comments.all() # post.comment_set.all() get all post comments using related name comments
        context['post'] = post # 
        context['comments'] = comments
        context['form'] = form
        return context
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST or None)
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        post = Post.objects.filter(id=self.kwargs['pk'], created_at__lte=timezone.now(), status=1)[0]
        comments = post.comment_set.all()
        context['post'] = post
        context['comments'] = comments
        context['form'] = form
        if form.is_valid():
            # data = Comment(content= form.cleaned_data['content'], name=form.cleaned_data['name'],...) # this is better
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']
            comment = Comment.objects.create(name=name, email=email, content=content, post=post)
            comment.save()
            form = CommentForm() # to get the form again but (clear) w/o any text data
            context['form'] = form
            return self.render_to_response(context=context)
            # Always return an HttpResponseRedirect after successfully dealing with Post request to be edited here
        return self.render_to_response(context=context)
@login_required
def vote(request, _id): 
    template_name = 'post_details.html' # Show that we can use attributes in fn. based rather than render(req.,blog/post_dwtails.html, contxt)
    post = get_object_or_404(Post, pk=_id)
    # request.POST is a dictionary-like object that lets you access submitted data by key name (template context field var)
    # comments = post.comment_set.get(pk=request.POST['comment'])
    # user = request.user.objects.get(pk=_id)
    # Vote.objects.filter(comment_votes__user=user)
    if request.method == 'POST':
        try:
            vote = post.votes.get(pk=request.POST['vote_type']) # ['vote_type'] field in template.html, at the same requested pk (choice prev.)
            # request.Post('vote') returns the ID/pk of the selected vote, as a string. request.POST values are always strings.
            up_votes = vote.filter(vote_type=vote.UP_VOTE)  # 
            # up_votes = post.votes.filter(vote_type=Vote.UP_VOTE) # all up votes for all posts
            # up_voters = up_votes.values_list('user__first_name', flat=True)
            down_votes = vote.filter(vote_type=vote.DOWN_VOTE)  # 
            # no_votes = vote.filter(vote_type=vote.NO_VOTE)  # 
            # Vote.objects.filter(post__vote_type__exact='UP_VOTE') # # all up votes for all posts
            score = Vote.objects.get(post = post) # we can put id =_id but better to specify the post itself, try
            form = VoteForm(request.POST or None)
            if Vote.objects.filter(id=_id, user_id=request.user.id).exists():
                return render(request, 'post_details.html', {'post': post, 'error_message': "Sorry, but you have already voted."})
            elif form.is_valid():
                if (up_votes):
                    vote.score += 1
                    vote.save()
                    up_count = up_votes.count()
                    down_count = down_votes.count()
                    Vote.objects.create(_id=_id, user_id=request.user.id)
                    # process the data in form.cleaned_data as required
                    add = form.save(commit=False)
                    add.post = post # post field in comment model => related_name = comments related to post model
                    add.save()
                elif(down_votes):
                    vote.score -= 1
                    vote.save()
                    up_count = up_votes.count()
                    down_count = down_votes.count()
                    up_voters = up_votes.values_list('user__first_name', flat=True)
                    Vote.objects.create(_id=_id, user_id=request.user.id)
                    # process the data in form.cleaned_data as required
                    add = form.save(commit=False)
                    add.post = post # post field in comment model => related_name = comments related to post model
                    add.save()
                else:
                    score.save()
        except (KeyError, vote.DoeidtExist):
            # Redisplay the question voting form.
            return render(request, 'blog/details.html', {'post': post, 'error_message': "You didn't select a vote.",})
        # Always return an HttpResponseRedirect after successfully dealing with Post request
        # This prevents data from being posted twice if a user hits the Back button.
        # Reverse fn. helps avoid having to hardcode a URL in the view function
        # redirect to a new URL:
        # return redirect(post.get_absolute_url())
        return HttpResponseRedirect(reverse('blog:details', args=(post.id,))) # blog/3/details.html or 'blog:results' '/polls/3/results.html/'
    else:
        form = VoteForm()
    context = {'post': post,'new_comment': add, 'form': form, 'score': score, 'up_count': up_count, 'down_count': down_count }
    return render(request, template_name, context)
def vote(request):
   post_id = int(request.POST.get('id')) # try uuid if int is not working
   vote_type = request.POST.get('type')
   vote_action = request.POST.get('action')
   thread = get_object_or_404(Post, pk=post_id)
   thisUserUpVote = thread.userUpVotes.filter(id = request.user.id).count()
   thisUserDownVote = thread.userDownVotes.filter(id = request.user.id).count()
   if (vote_action == 'vote'):
      if (thisUserUpVote == 0) and (thisUserDownVote == 0):
         if (vote_type == 'up'):
            thread.userUpVotes.add(request.user)
         elif (vote_type == 'down'):
            thread.userDownVotes.add(request.user)
         else:
            return HttpResponse('error-unknown vote type')
      else:
         return HttpResponse('error - already voted', thisUserUpVote, thisUserDownVote)
   elif (vote_action == 'recall-vote'):
      if (vote_type == 'up') and (thisUserUpVote == 1):
         thread.userUpVotes.remove(request.user)
      elif (vote_type == 'down') and (thisUserDownVote ==1):
         thread.userDownVotes.remove(request.user)
      else:
         return HttpResponse('error - unknown vote type or no vote to recall')
   else:
      return HttpResponse('error - bad action')
   num_votes = thread.userUpVotes.count() - thread.userDownVotes.count()
   return HttpResponse(num_votes)


def add_vote(request):
    if request.method == 'POST':
        try:
            post = Post.objects.get(pk=request.POST['id'])
        except Post.DoesNotExist:
            return HttpResponse("{'success': 'false'}")
        try:
            vote = Vote.objects.get(post=post, user=request.user)
        except Vote.DoesNotExist:
            pass
        else:
            return HttpResponse("{'success': 'false'}")
        if request.POST['type'] == 'up':
            post.score = post.score + 1
        else:
            post.score = post.score - 1
        post.save()
        Vote.objects.create(post=post, user=request.user, type=request.POST['type'])

        return HttpResponse("{'success':'true', 'score':" + post.score + "}")
    else:
        raise Http404('What are you doing here?')
def remove_vote(request):
    if request.method == 'POST':
        try:
            post = Post.objects.get(pk=request.POST['id'])
        except Post.DoesNotExist:
            return HttpResponse("{'success': 'false'}")
        try:
            vote = Vote.objects.get(post=post, user=request.user)
        except Vote.DoesNotExist:
            return HttpResponse("{'success': 'false'}")
        else:
            vote.delete()
        if request.POST['type'] == 'up':
            post.score = post.score - 1
        else:
            post.score = post.score + 1
        post.save()
        return HttpResponse("{'success':'true', 'score':" + post.score + "}")
    else:
        raise Http404('What are you doing here?')

from django.contrib.auth.mixins import LoginRequiredMixin
# add a view for getting the list of all new posts that's been posted by the current user
# "N" is the stored code for "new" and we order by the renew_on(due_on/delet_on/etc...) date so that the newest items are displayed first.
class PostedByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing only new posts(or loaned books) created by current user(maybe admin or normal user acc. to perms)
    ordered by date of renewal(OR due_back_date for abook)."""
    model = PostInstance
    # declare a template_name, rather than using the default
    template_name = 'blog/postinstance_list_renewed_user.html'
    paginate_by = 10
    def get_queryset(self):
        return PostInstance.objects.filter(commenter=self.request.user).filter(status__exact='N').order_by('renew_on')

# add a view for all renewed posts that's been viewd by only employee or admin of site
# you can use decoratot for permission in function based like
"""
@permission_required('blog.can_edit')
@permission_required('catalog.can_mark')
or use PermissionRequiredMixin for class based
class MyView(PermissionRequiredMixin, View):
    permission_required = 'catalog.can_mark'
there are a lot of permission decorators or mixins like LoginRequiredMixin or @login_required for function based
when you use function based views you must use raise_exception=True
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def my_view(request):
    ...
"""
class RenewedAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all renewed(R)/new(N) posts(OR loaned). Only visible to users with can_renew permission."""
    model = PostInstance
    permission_required = ('blog.can_renew', 'blog.can_edit')
    template_name = 'blog/PostInstance_list_renewed_all.html'
    paginate_by = 10
    def get_queryset(self):
        return PostInstance.objects.filter(status__exact='R').order_by('renew_on')

from django.shortcuts import get_object_or_404 # Get a specified object from a model based on its primary key value or NF
from django.http import Http404, HttpResponseRedirect # Creates a redirect to a specified URL (HTTP status code 302)
from django.urls import reverse # Generates a URL from a URL configuration name and a set of arguments
# reverse is the Python equivalent of the url tag that we've been using in our templates.
import datetime # A Python library for manipulating dates and times.
from django.contrib.auth.decorators import login_required, permission_required
from blog.forms import RenewPostForm # import our form (RenewPostForm) ==  from .forms import RenewPostForm
@login_required # To restrict access to the view to just logged-in emloyees who have permission to renew posts
@permission_required('blog.can_renew', 'blog.can_edit', raise_exception=True) # Allow access (with our can_renew/"can_renew") pr "<app label>.<permission codename>"
def renew_post_admin(request, pk): # You should have created a new permission setting in PostInstance ("can_renew")
    """View function for renewing a specific PostInstance by admin."""
    post_instance = get_object_or_404(PostInstance, pk=pk)
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewPostForm(request.POST)
        # Check if the form is valid:
        if form.is_valid(): # runs all the validation code on all of the fields
            # process the data in form.cleaned_data as required (here we just write it to the model renew_on field)
            post_instance.renew_on = form.cleaned_data['renewal_date']
            post_instance.save() # Save the data into the renew_on value of the associated PostInstance object
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-renewed'))
    # If this is a GET (or any other method) create the default form
    # We create the default form passing in an initial value for the renewal_date field, 3 weeks from the current date
    else: # Not a POST Request then we create the default form passing in an initial value for the renewal_date field,
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3) # 3 weeks from the current date.
        form = RenewPostForm(initial={'renewal_date': proposed_renewal_date})
    context = {
        'form': form, # post_instance passed to context to list post title, commenter, and the original due date that we...
        'post_instance': post_instance, # well use it in template to provide information about the post we're renewing
    } # We Call render to create the HTML page, specifying the template and a context that contains our form
    return render(request, 'blog/post_renew_admin.html', context) # You can redirect to a "success" page or '/'
# we use HttpResponseRedirect and reverse() to redirect to usually a "success" page, here to a view named 'all-renewed'
##############################################################################
#----------------------------- Maintainers Views ----------------------------#
##############################################################################
class MaintainerListView(generic.ListView):
    """Generic class-based list view for a list of maintainers."""
    model = Maintainer
    context_object_name = 'maintainers'
    template_name = 'blog/maintainer_list.html'
    paginate_by = 3
    def get_queryset(self):
        maintainer = get_object_or_404(Maintainer, id=self.kwargs.get('pk'))
        post = Post.objects.filter(maintainer=maintainer).order_by('-created_at')
        return post
@login_required
def maintainers_list(request):
    maintainers = Maintainer.objects.all()
    filter = MaintainerFilter(request.GET, queryset=maintainers)
    paginator = Paginator(maintainers, 3)  # Paginator object Show filtered 3 posts per page.
    page_obj = request.GET.get('page') # page object on the request
    page = paginator.get_page(page_obj) # give filtered page to Paginator to be Paginated float page numbers or (page() for int. doesn't matter)
    # Generate counts of some of the main objects
    context = {'maintainers': page, 'filter': filter} # posts is the key name to use in template
    return render(request, 'blog/maintainer_list.html', context) # you can just write only posts.html to refer to templates/blog/posts.html

def maint_details(request, pk):
    try:
        maintainer = Maintainer.objects.get(id =pk)  # get the post object by id (you can change to slug)
        # get the comments objects that has relation to same post(field in Comment model)
        posts = Post.objects.filter(maintainer = maintainer)
    except Post.DoeidtExist:
        raise Http404('Data does not exist')
    context = {'maintainer':maintainer, 'posts':posts,}
    return render(request,'blog/maintainer_details.html',context)

# class based vies simpler one
class MaintainerDetailView(generic.DetailView): 
    """Generic class-based detail view for an maintainer."""
    model = Maintainer
    lookup_field = 'uuid'
    template_name = 'blog/maintainer_details.html'
    def get_queryset(self):
        """
        Excludes any posts that aren't published yet.
        """
        return Maintainer.objects.all()

@login_required
@permission_required( 'account.can_publish', 'blog.can_edit', raise_exception=True)
def create_maint(request):
    if request.method == 'POST':
        form = MaintainerForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            user = form.cleaned_data.get('user')
            maint = Maintainer.objects.get(user=user)
            if maint:
                return redirect('blog:maintainer-detail',  maint.pk)
            else:
                form.save()
    else:
        form = MaintainerForm()
    return render(request, 'blog/maintainer_form.html', {'form': form,})
class MaintainerCreate(PermissionRequiredMixin, CreateView):
    permission_required = ['blog.can_renew', 'account.can_publish']
    model = Maintainer
    fields = ['first_name', 'last_name', 'user']
    template_name = 'blog/maintainer_form.html'
    #initial = {'date_of_death': '11/06/2020'}

class MaintainerUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ['blog.can_renew', 'account.can_publish']
    model = Maintainer
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class MaintainerDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ['blog.can_renew', 'account.can_publish']
    model = Maintainer
    success_url = reverse_lazy('maintainers')

##############################################################################
#------------------------------- Snippet Views ------------------------------#
##############################################################################
class SnippetListView(generic.ListView):
    """Generic class-based list view for a list of maintainers."""
    model = Snippet
    paginate_by = 10
class SnippetDetailView(generic.DetailView):
    """Generic class-based detail view for an maintainer."""
    model = Snippet
class SnippetCreate(PermissionRequiredMixin, CreateView):
    model = Snippet
    fields = '__all__'
    #permission_required = 'blog.can_renew'
class SnippetUpdate(PermissionRequiredMixin, UpdateView):
    model = Snippet
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    #permission_required = 'blog.can_renew'
class SnippetDelete(PermissionRequiredMixin, DeleteView):
    model = Snippet
    success_url = reverse_lazy('blog')
    #permission_required = 'blog.can_renew'

# delete post class based
"""
class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('posts')
    permission_required = 'blog.can_renew'
"""
class PostDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('blog')
    permission_required = 'blog.can_renew'
    model = Post
    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been deleted successfully.')
        return reverse_lazy("blog:index")
    def get_queryset(self):
        return self.model.objects.filter(creator=self.request.user)

def delete_view(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
    # fetch the object related to passed id
    obj = get_object_or_404(Post, id = id)
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # home page
        return HttpResponseRedirect("/blog/")
    return render(request, "delete_view.html", context)

def delete(request, id):
    data = get_object_or_404(Post, id=id) 
    data.delete()
    return redirect('blog:index')

def likePost(request):
    if request.method == 'GET':
        post_id = request.GET['post_id']
        likedpost = Post.objects.get(pk=post_id) #getting the liked posts
        m = Like(post=likedpost) # Creating Like Object
        m.save()  # saving it to store in database
        return HttpResponse("Success!") # Sending an success response
    else:
        return HttpResponse("Request method is not a GET")

from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
def search_titles(request):
    ctx = {}
    url_parameter = request.GET.get("q")
    if url_parameter:
        posts = Post.objects.filter(title__contains=url_parameter)
    else:
        posts = Post.objects.filter(created_at__lte=timezone.now()).order_by('-created_at')[:5]
    ctx["posts"] = posts
    does_req_accept_json = request.accepts("application/json")
    is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json
    if is_ajax_request:
        html = render_to_string(
            template_name="components/posts-results-partial.html", context={"posts": posts}
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
    return render(request, "blog/posts.html", context=ctx)

'''
EX:
<QuerySet [<Post: AI Intellegent (comments count: 1)>]>
Then these lines:
html = render_to_string(template_name="posts-results-partial.html", context={"posts": posts})
print(html)
Will print the following:
<ul>
  <li>AI Intellegent</li>
</ul>

URL requested: https://ourapp.com/artists?q=Queen
url_parameter value: "Queen"
URL requested: https://ourapp.com/artists?q=Samba
url_parameter value: "Samba"
URL requested: https://ourapp.com/artists?q=Chet Faker (decoded)
url_parameter value: "Chet Faker"
URL requested: https://ourapp.com/artists/?q=Chet%20Faker (encoded)
url_parameter value: "Chet Faker"

'''