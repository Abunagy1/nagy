from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ # One of Django's translation functions 
import datetime  # for checking renewal date range.
from account.models import User
from django import forms
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from django.forms import models
from django.forms.fields import MultipleChoiceField
from django.forms import BaseModelFormSet, ModelForm
from django.forms import modelformset_factory, inlineformset_factory
#import os
#os.environ.setdefault('PATH', '')
from blog.models import Post, Comment, Vote, Snippet, Tag, Genre, Maintainer

class RenewPostForm(forms.Form):  # This is a new form ==> take  class (Form)
    """Form for a employees to renew posts."""
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
# To validate a single field you should override the method clean_<fieldname>()
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date'] # 1st we get our cleaned data, then do some logic checks and return data
        # Check date is not in past.
        if data < datetime.date.today(): # If fail Raise a ValidationError specifying error text that we want to display
            raise ValidationError(_('Invalid date - renewal in past')) #  wraps text in ugettext_lazy() translation fn.(_)
# Check date is in range employee allowed to change (+4 weeks)||which is good practice if you want to translate your site 
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
        # Remember to always return the cleaned data.
        return data # After converted into correct standard type (in this case a Python datetime.datetime object)
        """
        # if you want to ovverride some model fields
    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}
        """
"""
from .models import Review, check_review_details
class EditReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'technical_merit', 'relevance', 'originality', 'clarity',
            'details', 'submitted'
        ]

    submitted = forms.BooleanField(required=False)
    technical_merit = forms.ChoiceField(choices=Review.SCORE_CHOICES, required=False)
    relevance = forms.ChoiceField(choices=Review.SCORE_CHOICES, required=False)
    originality = forms.ChoiceField(choices=Review.SCORE_CHOICES, required=False)
    details = forms.CharField(widget=forms.Textarea(attrs={'rows': '5'}), required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['submitted']:
            # If the review is submitted, it must provide scores and details
            # with the number of words as specified in the submission type:
            is_incomplete = False
            for score_field in self.instance.score_fields().keys():
                if not cleaned_data[score_field]:
                    self.add_error(score_field, 'Must select a score')
                    is_incomplete = True
            stype = self.instance.paper.stype
            if not check_review_details(cleaned_data['details'], stype):
                self.add_error(
                    'details',
                    f'Review details must have at least '
                    f'{stype.min_num_words_in_review} words'
                )
                is_incomplete = True
            if is_incomplete:
                self.cleaned_data['submitted'] = False
                raise forms.ValidationError('Review is incomplete')
        return cleaned_data
"""
# if you want to choose all the fields in related model using ModelMultibleChoiceField ovverride the iterator methode
class CustomModelChoiceIterator(models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj)
class CustomModelChoiceField(models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return CustomModelChoiceIterator(self)
    choices = property(_get_choices, MultipleChoiceField._set_choices)
class CustomePostFormset(BaseModelFormSet):
    code = CustomModelChoiceField(queryset=Snippet.objects.none(), label='ADD CODE', widget=forms.CheckboxSelectMultiple)
    def __init__(self, *args, **kwargs):
        super(BasePostFormset, self).__init__(*args, **kwargs)
        self.fields['snippet'].queryset = Snippet.objects.objects.all()
    class Meta:
        model = Post
        fields = '__all__'
# and then give it to the modelformset_factory
PostFSet = modelformset_factory(Post, form=ModelForm, formfield_callback=None, formset=CustomePostFormset, extra=1,  exclude = ('creator', 'snippet',),)
 
# the following multichoice fields depends on if you have already snippet model and the relation is foreign key not one to one
# to add data-* attributes to <option> elements.
# You can use a Select widget subclass to include the value of snippet.id
# as the HTML attribute data-id for each <option> element: 
class SnippetSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['data-id'] = value.instance.id
        return option
class PForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {'snippet': SnippetSelect}
"""
This will render the Post.Snippet select as:
<select id="id_snippet" name="snippet" required>
<option value="" selected>---------</option>
<option value="1" data-id="abc...">title1, code1</option>
<option value="2" data-id="adc...">title2, code2</option>
<option value="3" data-id="a=b...">title3, code3</option>
<option value="4" data-id="x==...">title2, code4</option>
</select>
""" 
"""
class SnippetModelChoice(ModelChoiceField):
    def label_from_instance(self, obj):
        return "Snippet #%s %s" % (obj.id, obj.title)
class SnippetModelChoiceForm(forms.ModelForm):
    snippet = forms.SnippetModelChoice(queryset=Snippet.objects.all())
    class Meta:
        model = Post
        fields = '__all__'
"""
class BasePostFormset(BaseModelFormSet):
    snippet = forms.ModelMultipleChoiceField(queryset=Snippet.objects.none(), label='ADD CODE', widget=forms.CheckboxSelectMultiple) # (queryset=None)
    def __init__(self, *args, **kwargs):
        super(BasePostFormset, self).__init__(*args, **kwargs)
        self.fields['snippet'].queryset = Snippet.objects.all()
    class Meta:
        model = Post
PostFormSet = modelformset_factory(Post, form=ModelForm, formfield_callback=None, formset=BasePostFormset, extra=1, exclude = ('creator', 'snippet'))

class PoForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('creator', 'snippet',)
        labels = {'snippet': _('Add Code'),} # if snippet is a forign key model
        widgets = {
            'snippet': forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'checkbox', 'id': 'post-snippet'}) # attr. for JS addEvent or css styling
        }
    def clean(self):
        snippet = self.cleaned_data.get('snippet')
        if snippet:
            self.fields_required(snippet.snippet_title, snippet.code, snippet.linenos, snippet.language, snippet.style, snippet.highlighted) # ['title', 'code', 'linenos', '', '', 'highlighted']
        else:
            self.cleaned_data['snippet'] = False
        return self.cleaned_data
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        #posts = Post.objects.filter(snippet=True)
        #snpts = Snippet.objects.get(Snippet.id==posts.id)
        self.queryset = Snippet.objects.all(snippet=True)
        #self.fields['snippet'].widget.attrs.update({'type': 'checkbox', 'class': 'checkbox', 'id': 'post-snippet'})
        #self.fields['snippet_title'].empty_label = "" / widget = forms.HiddenInput()
        #self.fields['snippet_title'].queryset = Post.objects.filter(snippet=True)
        #self.fields['snippet_title', 'code', 'linenos', 'language', 'style', 'highlighted'].queryset = Snippet.objects.all()
        # [{}] => unhashable type: 'set' ({}) or just () => 'dict' object is not callable  
        # with [] only KeyError at /blog/posts/add/ ('title', 'code', 'linenos',... 
        #self.fields({'title': self.snippet_title, 'code': self.code, 'linenos': self.code, 'language': self.code, 'style': self.code, 'highlighted': self.code,}).queryset = Post.objects.filter(snippet=True)
class PostForm(forms.ModelForm):
    add_code = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox', 'id': 'post-snippet'}), required=False)# attr. for JS addEvent or css styling
    tag = forms.ModelChoiceField(queryset=Tag.objects.all(), widget=forms.Select())
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), widget=forms.Select())
    class Meta:
        model = Post
        #fields = '__all__'
        #fields = ['title', 'tag', 'maintainer', 'post_img', 'content', 'snippet', 'genre', 'post_language', 'video', 'post_type', 'urls', 'views', 'status' ]
        exclude = ('creator', 'snippet', 'slug', 'userUpVotes', 'score', 'userDownVotes')

class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = '__all__'
        #exclude = ('id',)
class PostUpForm(forms.ModelForm):
    #add_code = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox', 'id': 'post-snippet'}), required=False)# attr. for JS addEvent or css styling
    tag = forms.ModelChoiceField(queryset=Tag.objects.all(), widget=forms.Select())
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), widget=forms.Select())
    class Meta:
        model = Post
        #fields = '__all__'
        #fields = ['title', 'tag', 'maintainer', 'post_img', 'content', 'snippet', 'genre', 'post_language', 'video', 'post_type', 'urls', 'views', 'status' ]
        exclude = ('creator', 'views', 'maintainer', 'tag', 'genre')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['snippet'].queryset = Snippet.objects.all()
        # override clean(self): method if you have any logical operations for any fields see (an invalid form control file)
    def clean(self):
        cleaned_data = super().clean()
        # if this Item already exists
        if self.instance.add_code:
            # add the old quantity to the new quantity
            cleaned_data['snippet_title', 'code', 'linenos', 'language', 'style', 'highlighted'] = self.instance.snippet
        return cleaned_data
    def save(self, commit=True):
        post, created = Post.objects.update_or_create(snippet=self.snippet, creator=self.creator)
        #rest of your logic
        return post
# or the next simpler one and works ine too
class PostUpdateForm(forms.ModelForm):
    #tag = forms.ModelChoiceField(queryset=Tag.objects.all(), widget=forms.Select())
    #genre = forms.ModelChoiceField(queryset=Genre.objects.all(), widget=forms.Select())
    class Meta:
        model = Post
        exclude = ('views', 'creator', 'maintainer', 'snippet', 'tag', 'genre', 'userUpVotes', 'score', 'userDownVotes')
        #fields = ['title', 'tag', 'maintainer', 'post_img', 'content', 'genre', 'post_language', 'video', 'post_type', 'urls', 'views', 'status' ]
class SnippetUpdateForm(forms.ModelForm):
    class Meta:
        model = Snippet
        exclude = ('highlighted',)
# if you haven't any model for Comment ==> take (forms.Form), but if you have a Comment model take ModelForm
class CommentForm(forms.ModelForm):
    content = forms.CharField(label ="", widget=forms.Textarea(attrs={ 'placeholder':'Comment here !', 'rows':4, 'cols':50, 'class': 'comnt_area', 'id': 'post-comnt'}), required=False)
    class Meta:
        model = Comment
        fields = ['content']

class MaintainerForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(), required=True)
    class Meta:
        model = Maintainer
        fields = ['first_name', 'last_name']

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['vote_type',]  # or ==> fields = '__all__'

"""
Ex:
widgets = {
'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Title of the Blog'}),
'slug': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Copy the title with no space and a hyphen in between'}),
'content': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Content of the Blog'}),
}
class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "name"
    }))
    age= forms.CharField(widget=forms.TextInput(attrs={
        'type': "number",
        "class": "form-control",
        "placeholder": "age"
    }))
    def __init__(self, school, *args, **kwargs):
        super(StudentsForm, self).__init__(*args, **kwargs)
        self.fields['form'] = forms.ModelChoiceField(
            queryset=Form.objects.filter(school=school))  
    class Meta:
        model = CRUD
        fields = [
            'name', 'age','level'
        ]  
"""