from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.views_utils import create_user_with_settings
from predictor.models import AlgorithmSettings


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
        create_user_with_settings(context)
        context['login'] = 'test-user2'
        context['email'] = 'oleg@yandex.ru'
        context['is_researcher'] = ''
        create_user_with_settings(context)

    @classmethod
    def tearDownClass(cls):
        for user in User.objects.all():
            alg_settings = AlgorithmSettings.objects.get(user=user)
            alg_settings.model_file.delete()
            user.delete()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/auth')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('predictor:auth'))
        self.assertEqual(resp.status_code, 200)

    def test_right_template_used(self):
        resp = self.client.get(reverse('predictor:auth'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/auth.html')

    def test_empty_fields_send(self):
        fields = ('username', 'password')

        context = {'submit': ''}

        for field in fields:
            context[field] = ''

        resp = self.client.post(reverse('predictor:auth'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/auth.html')

        for field in fields:
            self.assertTrue('no_'+field in resp.context)
            self.assertTrue(resp.context['no_'+field])

    def test_incorrect_fields_send(self):
        fields = ('username', 'password')

        context = {'submit': ''}

        for field in fields:
            context[field] = 'os.hack_my_system()'

        resp = self.client.post(reverse('predictor:auth'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/auth.html')

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

    def test_big_fields_send(self):
        fields = ('username', 'password')

        context = {'submit': ''}

        for field in fields:
            context[field] = 'qwe'*100

        resp = self.client.post(reverse('predictor:auth'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/auth.html')

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

    def test_wrong_password(self):
        context = {'username': 'test-user1', 'password': '123466',
                   'submit': ''}

        resp = self.client.post(reverse('predictor:auth'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/auth.html')

        self.assertTrue('incorrect_username_or_password' in resp.context)
        self.assertTrue(resp.context['incorrect_username_or_password'])

    def test_wrong_username(self):
        context = {'username': 'wrong-username', 'password': '12345',
                   'submit': ''}

        resp = self.client.post(reverse('predictor:auth'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/auth.html')

        self.assertTrue('incorrect_username_or_password' in resp.context)
        self.assertTrue(resp.context['incorrect_username_or_password'])

    def test_correct_username_and_password(self):
        context = {'username': 'test-user1', 'password': '12345',
                   'submit': ''}

        resp = self.client.post(reverse('predictor:auth'), context,
                                follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_index(self):
        context = {'username': 'test-user1', 'password': '12345',
                   'submit': ''}

        resp = self.client.post(reverse('predictor:auth') + '?next=/', context,
                                follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_research(self):
        context = {'username': 'test-user1', 'password': '12345',
                   'submit': ''}

        resp = self.client.post(reverse('predictor:auth') + '?next=/research',
                                context, follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_research_researcher(self):
        context = {'username': 'test-user2', 'password': '12345',
                   'submit': ''}

        resp = self.client.post(reverse('predictor:auth') + '?next=' +
                                reverse('predictor:research'), context,
                                follow=True)

        self.assertRedirects(resp, reverse('predictor:research'))

    def test_redirection_signed_in(self):
        user = User.objects.get(username='test-user1')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:auth'))

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_index_signed_in(self):
        user = User.objects.get(username='test-user1')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:auth') + '?next=' +
                               reverse('predictor:index'), follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_research_signed_in(self):
        user = User.objects.get(username='test-user1')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:auth') + '?next=' +
                               reverse('predictor:research'), follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_research_signed_in_researcher(self):
        user = User.objects.get(username='test-user2')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:auth') + '?next=' +
                               reverse('predictor:research'), follow=True)

        self.assertRedirects(resp, reverse('predictor:research'))
