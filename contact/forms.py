from django import forms
from django.db.models import fields
# i didn't take the contact model fields because it's not gonna be saved in db
class ContactForm(forms.Form): 
    subject = forms.CharField(max_length=100)
    sender_email = forms.EmailField(required=True)
    cc_myself = forms.BooleanField(required=False)
    message = forms.CharField(widget=forms.Textarea)
