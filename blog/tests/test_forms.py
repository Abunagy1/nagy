from django.test import TestCase
import datetime         #  from django.utils import timezone
from blog.forms import RenewPostForm
class RenewPostFormTest(TestCase):
    def test_renew_form_date_in_past(self):
        """Test form is invalid if renewal_date is before today."""
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewPostForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())
    def test_renew_form_date_too_far_in_future(self):
        """Test form is invalid if renewal_date more than 4 weeks from today."""
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewPostForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())
    def test_renew_form_date_today(self):
        """Test form is valid if renewal_date is today."""
        date = datetime.date.today()
        form = RenewPostForm(data={'renewal_date': date})
        self.assertTrue(form.is_valid())
    def test_renew_form_date_max(self):
        """Test form is valid if renewal_date is within 4 weeks."""
        date = datetime.date.today() + datetime.timedelta(weeks=4)
        form = RenewPostForm(data={'renewal_date': date})
        self.assertTrue(form.is_valid())
    def test_renew_form_date_field_label(self):
        """Test renewal_date label is 'renewal date'."""
        form = RenewPostForm()
        self.assertTrue( # We have to access the field using the fields dictionary (e.g. form.fields['field_name'])
            form.fields['renewal_date'].label is None or
            form.fields['renewal_date'].label == 'renewal date')
    def test_renew_form_date_field_help_text(self):
        """Test renewal_date help_text is as expected."""
        form = RenewPostForm()
        self.assertEqual(
            form.fields['renewal_date'].help_text,
            'Enter a date between now and 4 weeks (default 3).')


from django.test import TestCase
from ..models import User
from ..forms import EditProfileForm
class EditProfileFormTest(TestCase):
    def test_username_already_taken(self):
        User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234')
        form = EditProfileForm(
            data={
                'username': 'user1',
                'about_me': 'somthing about me'
            },
            original_username='user'
        )
        self.assertFalse(form.is_valid())
