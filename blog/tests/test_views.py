from django.test import TestCase
from blog.models import Maintainer
from django.urls import reverse
class MaintainerListViewTest(TestCase):
    @classmethod     # A Property method   
    def setUpTestData(cls):
        # Create maintainers for pagination tests Ex: 13 Maintainers
        number_of_maintainers = 13
        for maintainer_id in range(number_of_maintainers):
            Maintainer.objects.create(first_name='Christian {0}'.format(maintainer_id),
                                  last_name='Surname {0}'.format(maintainer_id))
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/maintainer/') # 1st type of URL, just the specific path without the domain
        self.assertEqual(response.status_code, 200)
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('maintainers')) # 2nd type of URL, generates URL from its name in the URL config.
        self.assertEqual(response.status_code, 200)
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('maintainers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/maintainer_list.html')
    def test_pagination_is_ten(self):
        response = self.client.get(reverse('maintainers'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True) # or (== True) or assertEqual... (, True)
        self.assertEqual(len(response.context['maintainer_list']), 10) # or assertTrue... (== Number) Ex: 
#self.assertTrue(len(response.context['maintainer_list']) == 5) # NO acc. To value of paginate_by var. in views.MaintainerListView
    def test_lists_all_maintainers(self): # response.context is the cotx. var. passed to the template by the view
        # Get second page and confirm it has (exactly) the remaining 3 items
        response = self.client.get(reverse('maintainers')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['maintainer_list']), 3)
import datetime
from django.utils import timezone
from blog.models import PostInstance, Post, Genre, Language
from django.contrib.auth.models import User  # To assign User as a borrower(create users programmatically rather than admin panel)
class LoanedPostInstancesByUserListViewTest(TestCase):
    ''' used SetUp() rather than setUpTestData() because we'll be modifying some of these objects later '''
    def setUp(self): # دي بقي سيتب اللي قلت لو في أي اوبجكتس بتتغير قيمها كل مره اختبر أو أثناء الإختبار يبقي مكانها هنا فعاوز منها نسخه جديده كل مره أرن التيست
        # Create two users create users programmatically using the DJ admin panel default fields username/email/password
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK') # كمان لما حعمل تطبيق اكونتات حستخدمها
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD') # علشان اليوزرز مينفعش يخشوا الأدمين بانل
        test_user1.save()
        test_user2.save()
        # Create a Post
        test_maintainer = Maintainer.objects.create(first_name='John', last_name='Smith') # طبعا دي حقول الموديل يعني مش بجيب من عندي
        test_genre = Genre.objects.create(name='Fantasy') # طبعا حقل واحد بس والباقي نفس الكلام للغه والكتاب
        test_language = Language.objects.create(name='English')
        test_post = Post.objects.create(
            title='Post Title',
            summary='My post summary',
            isbn='ABCDEFG',
            maintainer=test_maintainer,
            language=test_language,
        )
        # Create genre as a post-step
        genre_objects_for_post = Genre.objects.all()
        test_post.genre.set(genre_objects_for_post)
        test_post.save()
        # Create 30 PostInstance objects
        number_of_post_copies = 30
        for post_copy in range(number_of_post_copies):
            return_date = timezone.now() + datetime.timedelta(days=post_copy % 5)
            if post_copy % 2: # Half of the posts are borrowed by each test user
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm' # we've initially set the status of all posts to "maintenance"
            PostInstance.objects.create(post=test_post, imprint='Unlikely Imprint, 2016', due_back=return_date,
                                        borrower=the_borrower, status=status)
    def test_redirect_if_not_logged_in(self): # علشان لو اليوزر مش لاجج الفيو يوجهه لصفحه اللوجين حستخدم اسيرت ريديركت فيها
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/myposts/')
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/postinstance_list_borrowed_user.html')
    def test_only_borrowed_posts_in_list(self): # علشان أتأكد إنه الصفحه بتاعه الكتب حتظهر للمستخدم اللاجج في الأول حلوج بالمستخدم بتاع الإختبار
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK') # حيجرب يلوج بالمستخدم اللي عمله للإختبار
        response = self.client.get(reverse('my-borrowed')) # بعد كده بتشيك بالصفحه الدمي اجيب عنوان الصفحه بتاعه الكتب المستعاره لليوزر ده
        # Check our user is logged in علشان أتأكد إنه اليوزر اللي لاجج ده هو فعلا التيست يوزر حقوله اسيرت إيكوال انه الكونتكست فاريابل بتاع اليوزر هو بتاع التست يوزر
        self.assertEqual(str(response.context['user']), 'testuser1') # طبعا علشان اسم اليوزر نيم ده سترينج فبحوله لسترنج وبعدين أقارنه
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200) # علشان أتأكد إنه الريسبونس ستيتس فعلا نجح ب ٢٠٠ 
        # Check that initially we don't have any posts in list (none on loan)
        self.assertTrue('postinstance_list' in response.context)
        self.assertEqual(len(response.context['postinstance_list']), 0)
        # Now change all posts to be on loan
        get_ten_posts = PostInstance.objects.all()[:10]
        for copy in get_ten_posts:
            copy.status = 'o'
            copy.save()
        # Check that now we have borrowed posts in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        self.assertTrue('postinstance_list' in response.context)
        # Confirm all posts belong to testuser1 and are on loan
        for postitem in response.context['postinstance_list']:
            self.assertEqual(response.context['user'], postitem.creator)
            self.assertEqual(postitem.status, 'o')
    def test_pages_paginated_to_ten(self):
        # Change all posts to be on loan.
        # This should make 15 test user ones.
        for copy in PostInstance.objects.all():
            copy.status = 'o'
            copy.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Confirm that only 10 items are displayed due to pagination
        # (if pagination not enabled, there would be 15 returned)
        self.assertEqual(len(response.context['postinstance_list']), 10)
    def test_pages_ordered_by_due_date(self):
        # Change all posts to be on loan
        for copy in PostInstance.objects.all():
            copy.status = 'o'
            copy.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['postinstance_list']), 10)
        last_date = 0
        for copy in response.context['postinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)
import uuid # 
from django.contrib.auth.models import Permission  # Required to grant the permission needed to set a post as returned.
class RenewPostInstancesViewTest(TestCase): # بختبر ان الفيو مش حيظهر غير للي معاهم بيرميشن كان ماركريترنيد وتوجهه لصفحه نوت فاوند لو حاول تجديد كتاب مش موجود
    def setUp(self):
        # We creates two users and two post instances, but only gives one user the permission required to access the view
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()
        # Give test_user2 permission to renew posts.
        permission = Permission.objects.get(name='Set post as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        # Create a post
        test_maintainer = Maintainer.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_post = Post.objects.create(title='Post Title', summary='My post summary',
                                        isbn='ABCDEFG', maintainer=test_maintainer, language=test_language,)
        # Create genre as a post-step
        genre_objects_for_post = Genre.objects.all()
        test_post.genre.set(genre_objects_for_post) # Direct assignment of many-to-many types not allowed
        test_post.save()
        # Create a PostInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_postinstance1 = PostInstance.objects.create(post=test_post,
                                                              imprint='Unlikely Imprint, 2016', due_back=return_date,
                                                              borrower=test_user1, status='o')
        # Create a PostInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_postinstance2 = PostInstance.objects.create(post=test_post, imprint='Unlikely Imprint, 2016',
                                                              due_back=return_date, borrower=test_user2, status='o')
# the next part check that only users with the correct permissions (testuser2) can access the view
#Warning: If you use the form class RenewPostModelForm(forms.ModelForm) instead of class RenewPostForm(forms.Form), then the form field name is 'due_back' instead of 'renewal_date'.
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}))
        self.assertEqual(response.status_code, 403)
    def test_logged_in_with_permission_borrowed_post(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance2.pk}))
        # Check that it lets us login - this is our post and we have the right permissions.
        self.assertEqual(response.status_code, 200)
    def test_logged_in_with_permission_another_users_borrowed_post(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}))
        # Check that it lets us login. We're a admin, so we can view any users post
        self.assertEqual(response.status_code, 200)
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/post_renew_admin.html')
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)
# next two function test POST requests, but in this case with invalid renewal dates. We use assertFormError() to verify that the error messages are
# as expected
    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}),
                                    {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')
    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}),
                                    {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')
# the next part checks that the view redirects to a list of all borrowed posts if renewal succeeds
# The post data is the second argument to the post function, and is specified as a dictionary of key/values
    def test_redirects_to_all_borrowed_post_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-post-admin', kwargs={'pk': self.test_postinstance1.pk}),
                                    {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))
    def test_HTTP404_for_invalid_post_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our postinstance!
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-post-admin', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)
class MaintainerCreateViewTest(TestCase):
    """Test case for the MaintainerCreate view (Created as Challenge)."""
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()
        permission = Permission.objects.get(name='Set post as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        # Create a post
        test_maintainer = Maintainer.objects.create(first_name='John', last_name='Smith')
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('maintainer-create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/maintainer/create/')
    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('maintainer-create'))
        self.assertEqual(response.status_code, 403)
    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('maintainer-create'))
        self.assertEqual(response.status_code, 200)
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('maintainer-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/maintainer_form.html')
    def test_form_date_of_death_initially_set_to_expected_date(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('maintainer-create'))
        self.assertEqual(response.status_code, 200)
        expected_initial_date = datetime.date(2020, 6, 11)
        response_date = response.context['form'].initial['date_of_death']
        response_date = datetime.datetime.strptime(response_date, "%d/%m/%Y").date()
        self.assertEqual(response_date, expected_initial_date)
    def test_redirects_to_detail_view_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('maintainer-create'),
                                    {'first_name': 'Christian Name', 'last_name': 'Surname'})
        # Manually check redirect because we don't know what maintainer was created
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/maintainer/'))




# test that the user cannot update a post of another user and that the post creation is associated with the current user
from django.urls import reverse
from django.test import TestCase
from blog.models import Post
from django.contrib.auth.models import User
class PostCreateViewTest(TestCase):
    def test_post_create_stores_user(self):
        user1 = User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234'
        )
        post_data = {
            'title': 'test post',
            'content': 'Hello world',
        }
        self.client.force_login(user1)
        self.client.post(reverse('core:post_create'), post_data)
        self.assertTrue(Post.objects.filter(author=user1).exists())
class PostUpdateViewTest(TestCase):
    def test_post_update_returns_404(self):
        user1 = User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234'
        )
        user2 = User.objects.create_user(
            username='user2', email='user2@gmail.com', password='1234'
        )
        post = Post.objects.create(
            author=user1, title='test post', content='Hello world')
        self.client.force_login(user2)
        response = self.client.post(
            reverse('core:post_update', kwargs=({'pk': post.id})),
            {'title': 'change title'}
        )
        self.assertEqual(response.status_code, 404)

