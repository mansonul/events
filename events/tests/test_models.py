from django.test import TestCase
from events.models import Event


class TestEvent(TestCase):
    def setUp(self):
        Event.objects.create(title='First title', description='First description')

    def test_can_create_event(self):
        """Event can be created"""
        title = Event.objects.get(title='First title')
        self.assertEqual(title, 'First title')
