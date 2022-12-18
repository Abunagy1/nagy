from django.test import TestCase # A unit test Class from Django for tests    
from blog.models import Maintainer
class MaintainerModelTest(TestCase): # our test class for Maintainer model (descriptive name)
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        Maintainer.objects.create(first_name='Big', last_name='Bob') # أو بنشيء أوبجكتس آو بدي قيم لمتغيرات جلوبال مش حغيرها تاني 
    def test_first_name_label(self):
        maintainer = Maintainer.objects.get(id=1) # Get an maintainer object to test
        # Get the metadata for the required field and use it to query the required field data
        field_label = maintainer._meta.get_field('first_name').verbose_name # بستخدم ميتا اتربيوت علشان مقدرش أوصل للأوبجكت بروبرتيس مباشره من فرست نيم لأنه سترنج
        self.assertEqual(field_label, 'first name') # Compare the value to the expected result بتأكد انه الفرست نيم مطابق للفيربوس نيم 
    def test_last_name_label(self):
        maintainer = Maintainer.objects.get(id=1)
        field_label = maintainer._meta.get_field('last_name').verbose_name # verbose_name == last name
        self.assertEqual(field_label, 'last name')
    def test_date_of_birth_label(self):
        maintainer = Maintainer.objects.get(id=1)
        field_label = maintainer._meta.get_field('date_of_birth').verbose_name # verbose_name == date of birth
        self.assertEqual(field_label, 'date of birth')
    def test_date_of_death_label(self):
        maintainer = Maintainer.objects.get(id=1)
        field_label = maintainer._meta.get_field('date_of_death').verbose_name # verbose_name == Died
        self.assertEqual(field_label, 'died') # will fail if the name in models.py is Died  change it either here / in Model
    def test_first_name_max_length(self):
        maintainer = Maintainer.objects.get(id=1)
        max_length = maintainer._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)
    def test_last_name_max_length(self):
        maintainer = Maintainer.objects.get(id=1)
        max_length = maintainer._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 100)
    def test_object_name_is_last_name_comma_first_name(self): # Test Ordering in meta class  last_name, first_name
        maintainer = Maintainer.objects.get(id=1)
        expected_object_name = '{0}, {1}'.format(maintainer.last_name, maintainer.first_name)
        self.assertEqual(str(maintainer), expected_object_name)
    def test_get_absolute_url(self):
        maintainer = Maintainer.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(maintainer.get_absolute_url(), '/catalog/maintainer/1')
