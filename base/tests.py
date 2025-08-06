from django.test import TestCase
from django.test import TestCase
from .models import Event

# Create your tests here.
class EventModelTest(TestCase):
    def test_string_representation(self):
        event = Event(name="Seminar AI")
        self.assertEqual(str(event), "Seminar AI")
