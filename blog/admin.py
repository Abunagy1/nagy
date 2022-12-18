from django.contrib import admin
from .models import Maintainer, Genre, Post, PostInstance, Snippet, Tag, Comment, PostViews
"""Minimal registration of Models.
admin.site.register(Post)
admin.site.register(Maintainer)
admin.site.register(PostInstance)
admin.site.register(Genre) # not important to make an admin class for it as it just have one record
admin.site.register(Language)
"""
admin.site.register(Genre)
admin.site.register(PostViews)

# Define class for any model we need to adjoin it in other model, here we want to adjoin Post Class or model in Maintainer model
class PostsInline(admin.TabularInline): # TabularInline=Horizontal/StackedInline=Vertical--Like default layout
    """Defines format of inline post insertion (used in MaintainerAdmin)"""
    model = Post
    extra: 3

class PostsInstanceInline(admin.TabularInline): # Define admin class for PostInstance Model
    """Defines format of inline post instance insertion (used in PostAdmin)"""
    model = PostInstance

"""
class SnippetsInline(admin.StackedInline): # Define admin class for PostInstance Model
    model = Snippet
"""

class CommentsInline(admin.StackedInline): # Define admin class for PostInstance Model
    """Defines format of inline post instance insertion (used in PostAdmin)"""
    model = Comment

"""
class MaintainersInline(admin.StackedInline): # Define admin class for PostInstance Model
    model = Maintainer
"""

# Define admin class for Maintainer, then admin.site.register(Maintainer, MaintainerAdmin) or @admin.register(Maintainer) befor
@admin.register(Maintainer) # == equivalent to admin.site.register(Maintainer, MaintainerAdmin) after defining the below MaintainerAdmin class 
class MaintainerAdmin(admin.ModelAdmin):
    """Administration object for Maintainer models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields), grouping the date fields horizontally
     - adds inline addition of posts in maintainer view (inlines)
    """
    list_display = ('last_name', 'first_name') 
    fields = ['first_name', 'last_name', 'user'] # ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    search_fields = ['first_name', 'user'] # or try search_fields = ('title',)
    inlines = [PostsInline] # only for foreign key relations

class PostAdmin(admin.ModelAdmin): # Define admin class for Post Model
    """Administration object for Post models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of post instances in post view (inlines)
    """
    #fields = ['title', 'tag', 'maintainer', 'post_img', 'content', 'snippet', 'genre', 'creator', 'post_language', 'video', 'post_type', 'urls', 'views', 'status' ]
    list_display = ('title', 'maintainer', 'display_genre', 'created_at', 'updated_at')
    inlines = [PostsInstanceInline, CommentsInline]
    list_filter = ( 'status', 'created_at', 'updated_at')
    search_fields = ['first_name', 'title', ] # or try search_fields = ('title',)
    # create the slug field from the title field
    #prepopulated_fields = {'slug': ('title',)} # automatically add slug field without having to do in models
    # The value of 'autocomplete_fields[0]' must be a foreign key or a many-to-many field. Ex: ['maintainer',] / post_language
    autocomplete_fields = ('maintainer',) # autocomplete_fields works only for FK & M2M 
    #readonly_fields = ["", ""]
    
admin.site.register(Post, PostAdmin) # alternative to @admin.site.register(Post) before PostAdmin.

# TagAdmin must define "search_fields", because it's referenced by PostAdmin.autocomplete_fields.
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    # wrong inlines = [PostsInline] # that mean only one Tag can have many Posts (it has many to many not foreign key relation to post)
    # blog.admin.PostsInline': 'blog.Post' has no ForeignKey to 'blog.Tag'.
admin.site.register(Tag, TagAdmin)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('commenter', 'created_on', 'content', 'post', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('commenter', 'content')
    # actions method will help us for approving many comment objects at once
    actions = ['approve_comments']
    # approve_comments takes a queryset and updates the active boolean field to True
    def approve_comments(self, request, queryset): # 
        queryset.update(active=True)

@admin.register(PostInstance)
class PostInstanceAdmin(admin.ModelAdmin): # Define admin class for PostInstance Model
    """Administration object for PostInstance models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    list_display = ('post', 'status', 'commenter', 'renew_on', 'id')
    list_filter = ('status', 'renew_on') 
    fieldsets = (   # making group of fields and naming it
        (None, { 
            'fields': ('post', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'commenter', 'renew_on')
        }),
    )
# EX: adding commenter field in list_display/fieldsets make the field visible in Admin, allowing us to assign a User to a PostInstance when needed

@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin): # Define admin class for PostInstance Model
    list_display = ('snippet_title', 'linenos', 'created', 'language', 'id')
    list_filter = ('highlighted', 'style') 
    fieldsets = ( 
        (None, { 
            'fields': ('post', 'code', 'id')
        }),
        ('Availability', {
            'fields': ('created', 'owner', 'snippet_title')
        }),
    )