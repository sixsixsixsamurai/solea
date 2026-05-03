from django.test import TestCase, Client
from django.urls import reverse
from .models import Partner


class PartnerModelTest(TestCase):
    def test_str(self):
        partner = Partner(name='FreshFarm')
        self.assertEqual(str(partner), 'FreshFarm')


class PartnersViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Partner.objects.create(name='Active Partner', is_active=True, order=1)
        Partner.objects.create(name='Inactive Partner', is_active=False, order=2)

    def test_partners_page_loads(self):
        response = self.client.get(reverse('partners:partners'))
        self.assertEqual(response.status_code, 200)

    def test_only_active_partners_shown(self):
        response = self.client.get(reverse('partners:partners'))
        partners = list(response.context['partners'])
        names = [p.name for p in partners]
        self.assertIn('Active Partner', names)
        self.assertNotIn('Inactive Partner', names)

    def test_partners_page_accessible_without_login(self):
        response = self.client.get(reverse('partners:partners'))
        self.assertEqual(response.status_code, 200)
