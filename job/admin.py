from django.contrib import admin
from .models import Job, Category, Applicant
"""
admin.site.register(Job)
admin.site.register(Category)
admin.site.register(Applicant)
"""
class JobsInline(admin.TabularInline):
    """Defines format of inline job insertion (used in AuthorAdmin)"""
    model = Job
    extra: 3
class ApplicantInline(admin.TabularInline):
    """Defines format of inline job insertion (used in AuthorAdmin)"""
    model = Applicant
    extra: 3
@admin.register(Job) # == equivalent to admin.site.register(Author, AuthorAdmin) after defining the below AuthorAdmin class 
class JobAdmin(admin.ModelAdmin):
    inlines = [ApplicantInline]
    list_display = ('title', 'job_type', 'category',)
    list_filter = ('published_at',)
    search_fields = ['category']

@admin.register(Applicant) # == equivalent to admin.site.register(Author, AuthorAdmin) after defining the below AuthorAdmin class 
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('name', 'applicant', 'email', 'website', 'cv', 'date_of_application')
    #fields = ['name', 'applicant', ('cv', 'cover_letter')]
    list_filter = ('date_of_application',)
    search_fields = ['name']
    """
    fieldsets = ( 
    (None, { 
        'fields': ('job', '')
    }),
    ('Availability', {
        'fields': ('published_at', '', '')
    }), )
    """
    #prepopulated_fields = {'slug': ('title',)} # automatically add slug field without having to do in models
@admin.register(Category) 
class CategoryAdmin(admin.ModelAdmin): # Define admin class for PostInstance Model
    """Administration object for PostInstance models.
    Defines:
    - fields to be displayed in list view (list_display)
    - filters that will be displayed in sidebar (list_filter)
    - grouping of fields into sections (fieldsets)
    """
    inlines = [JobsInline] 
    list_display = ('name',)
    list_filter = ('job',) 

