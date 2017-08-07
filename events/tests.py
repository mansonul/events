from django.test import TestCase
from events.models import Event


class TestEvent(TestCase):
    def test_can_create_event(self):
        """Event can be created"""
        first_item = Event()
        first_item.title = 'First title'
        first_item.description = 'First description'
        first_item.save()

        second_item = Event()
        second_item.title = 'Second title'
        second_item.description = 'Second description'
        second_item.save()

        saved_items = Event.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.title, 'First title')
        self.assertEqual(first_saved_item.description, 'First description')
        self.assertEqual(second_saved_item.title, 'Second title')
        self.assertEqual(second_saved_item.description, 'Second description')
