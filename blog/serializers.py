# serializer is like Django's forms but used in API to defines the fields that get serialized/deserialized
# we mean by serializing/deserializing, converting the data or to provide a way of
# serializing and deserializing the Model instances into representations such as json.
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import serializers
from blog.models import Snippet, Post, Maintainer, LANGUAGE_CHOICES, STYLE_CHOICES

'''
# explicitly define the fields to be serialized/deserialized maneually (much code) like the following:
class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    snippet_title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})  # equivalent to using widget=widgets.Textarea 
    linenos = serializers.BooleanField(required=False)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
    # The create() and update() methods define how 
    # fully fledged instances are created or modified when calling serializer.save()
    # you cann pass aditional information before saving by ovveriding them in views
    # using .perform_create() or .perform_update() etc...
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        create() & update() methods define how fully fledged instances are created or modified 
        """
        return Snippet.objects.create(**validated_data)
    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.snippet_title = validated_data.get('snippet_title', instance.snippet_title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance

'''
'''
# or better using generic class based & incluse the create, perform, etc...
class SnippetSerializer(serializers.ModelSerializer): # ModelSerializer using id or pk
    owner = serializers.ReadOnlyField(source='owner.username') # or CharField(read_only=True
    class Meta:
        model = Snippet
        fields = ['id', 'snippet_title', 'code', 'linenos', 'language', 'style']

'''

'''
If we're going to have a hyperlinked API, we need to make sure we name our URL patterns.
The HyperlinkedModelSerializer has the following differences from ModelSerializer:
•	It does not include the id field by default.
•	It includes a url field, using HyperlinkedIdentityField.
•	Relationships use HyperlinkedRelatedField, instead of PrimaryKeyRelatedField.
'''
class SnippetSerializer(serializers.HyperlinkedModelSerializer): # HyperlinkedModelSerializer using url
    # reflect that the owner field that been associated in snippets api views
    # we need to reflect that here in SnippetSerializer itself by adding the following line:
    owner = serializers.ReadOnlyField(source='owner.username') # or CharField(read_only=True)
    # # ReadOnlyField class views for the user representations to be Un-typed in contrast to other
    # CharField, BooleanField etc... The untyped ReadOnlyField is always read-only, but will
    # not be used for updating model instances when they are deserialized.
    # The source argument controls which attribute is used to populate a field, here(username)
    # and can point at any attribute on the serialized instance,
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')
    # path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view(), name='snippet-highlight'),
    # we've added a new 'highlight' field. This field is of the same type as the url field,
    # except that it points to the 'snippet-highlight' url pattern, 
    # instead of the 'snippet-detail' url pattern. 
    # Because we've included format suffixed URLs such as '.json',
    # we also need to indicate on the highlight field that 
    # any format suffixed hyperlinks it returns should use the '.html' suffix
    view_name = 'post_datails'
    #queryset = Snippet.objects.all()
    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'slug': obj.post.slug,
            'pk': obj.pk
    }
        return reverse(view_name, kwargs=url_kwargs, request=request,     format=format)
    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'post__slug': view_kwargs['slug'],
        'pk': view_kwargs['pk']
        }
        return self.get_queryset().get(**lookup_kwargs)
    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner', 'snippet_title', 'code', 'linenos', 'language', 'style')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='job-highlight', format='html')
    class Meta:
        model = Post
        fields = ['url', 'creator', 'title', 'post_type', 'tag', 'created_at', 'maintainer',
                  'genre', 'video', 'post_img', 'slug', 'urls']

class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True)
        # path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name='snippet-detail'),
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

