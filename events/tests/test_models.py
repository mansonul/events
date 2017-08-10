from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from events.models import Event
from project.users.models import User


class TestEvent(TestCase):
    def setUp(self):
        Event.objects.create(title='First title',
                             user=User.objects.create(username='main'),
                             description='First description',
                             image=SimpleUploadedFile(name='foo.gif',
                                 content=b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00'))

    def test_can_create_event(self):
        """Event can be created"""
        event = Event.objects.get(title='First title')
        self.assertEqual(event.title, 'First title')
        self.assertEqual(event.slug, 'first-title')
        self.assertEqual(event.description, 'First description')

    def test_can_get_user(self):
        event = Event.objects.get(title='First title')
        self.assertEqual(event.user.username, 'main')

    def test_can_upload_photo(self):
        image = Event.objects.get(title='First title')
        self.assertTrue(image.image)
