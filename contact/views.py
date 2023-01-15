import datetime
from django.contrib.auth import authenticate, login
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import ContactForm
from .models import Contact
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.utils import translation
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormView
from django.core.mail import send_mail, send_mass_mail, BadHeaderError
from django.conf import settings
#@login_required  # or @login_required() only logged in users should access this
def contact(request):
    info = Contact.objects.first()  # from the Model
    form = ContactForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            subject = form.cleaned_data['subject']
            sender_email = form.cleaned_data['sender_email']
            message = form.cleaned_data['message']
            cc_myself = form.cleaned_data['cc_myself']
            recipients = ['postta@aol.com']
            if cc_myself:
                try:
                    recipients.append(sender_email)
                    send_mail(subject, message, sender_email, recipients, fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            else:
                send_mail(subject, message, sender_email, recipients, fail_silently=False)
            return HttpResponseRedirect('/contacts/thanks') # return redirect('/contacts/')
        else:
            return HttpResponse('Make sure all fields are entered and valid.') 
    return render(request, 'contact/contact.html', {'info': info, 'form': form})
#@login_required  # or @login_required() only logged in users should access this
def contact_me(request):
    info = Contact.objects.first()  # from the Model
    if request.method == 'POST':
        form = ContactForm(request.POST or None)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            sender_email = form.cleaned_data['sender_email']
            message = form.cleaned_data['message']
            cc_myself = form.cleaned_data['cc_myself']
            recipients = ['postta@aol.com']
            if cc_myself:
                try:
                    recipients.append(sender_email)
                    send_mail(subject, message, sender_email, recipients, fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            else:
                send_mail(subject, message, sender_email, recipients, fail_silently=False)
            return HttpResponseRedirect('/contacts/thanks') # return redirect('/contacts/')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'info': info, 'form': form})
class ContactFormView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = '/thanks/'
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super().form_valid(form)

#from messages.models import Message
#from messages.forms import NewMessageForm
'''@login_required
def message_me(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    #profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        form = NewMessageForm(request.POST, instance=user) # just username, email and password
        # create a form instance and populate it with data from the request:
        #Message.new_message(from_user=request.user, to_users=[user], subject=subject, content=content)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save(),  # prof2.save(commit=False)
            #prof2.user = request.user
            # ...
            #prof2.save()
            # redirect to a new URL:
            messages.success(request, _('Your profile has been successfully updated!'))
            return redirect('/accounts')
            #return HttpResponseRedirect('/accounts/')
        else:
            messages.error(request, _('Please correct the following error.'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewMessageForm()
    context = {'form': form,  }
    return render(request, 'account/profile_edit.html', context)'''


def thanks(request):
    return render(request, 'thanks.html')