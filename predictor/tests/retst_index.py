from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.views_utils import crete_user_with_settings
from unittest import skip


correct_user = {
    'first_name': 'oleg',
    'last_name': 'tester',
    'login': 'test-user1',
    'email': 'lion@mail.ru',
    'password': '12345',
    'password_double': '12345',
    'question': 'How many wheels had a Telezhka',
    'answer': 'three',
    'register': ''
}


class TestAuthPageSimple(TestCase):

    @classmethod
    def setUpTestData(cls):
        context = correct_user.copy()
        crete_user_with_settings(context)
        context['login'] = 'test-user2'
        context['email'] = 'oleg@yandex.ru'
        context['is_researcher'] = ''
        crete_user_with_settings(context)

    @classmethod
    def tearDownClass(cls):
        for user in User.objects.all():
            user.delete()

    def setUp(self):
        user = User.objects.get(username='test-user1')
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('predictor:index'))
        self.assertEqual(resp.status_code, 200)

    def test_right_template_used(self):
        resp = self.client.get(reverse('predictor:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/index.html')

    def test_logout_user(self):
        self.client.logout()
        resp = self.client.get(reverse('predictor:index'))
        self.assertRedirects(resp, reverse('predictor:auth') + '?next=' +
                             reverse('predictor:index'))

    def test_empty_file_fields(self):
        context = {'code': ''}

        resp = self.client.post(reverse('predictor:index'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/index.html')

        self.assertTrue('no_menu_data' in resp.context)
        self.assertTrue(resp.context['no_menu_data'])

