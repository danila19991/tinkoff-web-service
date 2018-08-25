from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.models import AlgorithmSettings
from django.core.files import File
from time import sleep


correct_user = {
    'first_name': 'oleg',
    'last_name': 'tester',
    'login': 'test-login1',
    'email': 'oleg@yandex.ru',
    'password': 'OlEgCOdEr',
    'password_double': 'OlEgCOdEr',
    'question': 'How many wheels had a Telezhka',
    'answer': 'three',
    'register': ''
}

saved_fields = ('first_name', 'last_name', 'email', 'login', 'question',
                'answer')


class TestAuthPageSimple(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('test-login0', 'lion@mail.ru',
                                        'cat-tologist',
                                        first_name='lev',
                                        last_name='tester-too')

        while True:
            try:
                default_model = File(open('models/default.mdl', 'rb+'))
                break
            except Exception:
                sleep(0.5)
        user_settings = AlgorithmSettings(user=user, question='Insert qwerty',
                                          answer='qwerty',
                                          model_file=default_model)
        user_settings.save()
        default_model.close()

    @classmethod
    def tearDownClass(cls):
        for user in User.objects.all():
            alg_settings = AlgorithmSettings.objects.get(user=user)
            alg_settings.model_file.delete()
            user.delete()

    def tearDown(self):
        users = User.objects.filter(username='test-login1')
        if len(users) == 1:
            alg_settings = AlgorithmSettings.objects.get(user=users[0])
            alg_settings.model_file.delete()
            users[0].delete()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/register')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('predictor:register'))
        self.assertEqual(resp.status_code, 200)

    def test_right_template_used(self):
        resp = self.client.get(reverse('predictor:register'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

    def test_empty_fields_send(self):
        fields = ('first_name', 'last_name', 'email', 'password', 'login',
                  'password_double', 'question', 'answer')

        context = {'register': True}

        for field in fields:
            context[field] = ''

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        for field in fields:
            self.assertTrue('no_'+field in resp.context)
            self.assertTrue(resp.context['no_'+field])

    def test_incorrect_fields_send(self):
        fields = ('first_name', 'last_name', 'email', 'password', 'login',
                  'password_double', 'question', 'answer')

        context = {'register': True}

        for field in fields:
            context[field] = 'os.hack_my_system()'

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

    def test_big_fields_send(self):
        fields = ('first_name', 'last_name', 'email', 'password', 'login',
                  'password_double', 'question', 'answer')

        context = {'register': True}

        for field in fields:
            context[field] = 'qwe'*100

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

    def test_medium_fields_send(self):
        fields = ('first_name', 'last_name', 'email', 'password', 'login',
                  'password_double',)
        long_fields = ('question', 'answer')

        context = {'register': True}

        for field in fields:
            context[field] = 'qwe'*30
        for field in long_fields:
            context[field] = 'qwe'*30

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

    def test_password_not_match(self):
        context = correct_user.copy()
        context['password'] = 'password'

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        self.assertTrue('not_match_passwords' in resp.context)
        self.assertTrue(resp.context['not_match_passwords'])

        for field in saved_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], context[field])

    def test_incorrect_email(self):
        context = correct_user.copy()
        context['email'] = 'email'

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

        for field in saved_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], context[field])

    def test_correct_registration(self):
        context = correct_user.copy()

        resp = self.client.post(reverse('predictor:register'), context,
                                follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

        self.assertEqual(len(User.objects.filter(username='test-login1')), 1)

        user = User.objects.filter(username='test-login1')[0]

        self.assertEqual(user.username, 'test-login1')
        self.assertEqual(user.first_name, 'oleg')
        self.assertEqual(user.last_name, 'tester')
        self.assertEqual(user.email, 'oleg@yandex.ru')
        self.assertTrue(user.check_password('OlEgCOdEr'))

        algo_settings = AlgorithmSettings.objects.filter(user=user)[0]

        self.assertEqual(algo_settings.question, correct_user['question'])
        self.assertEqual(algo_settings.answer, correct_user['answer'])

    def test_used_email(self):
        context = correct_user.copy()
        context['email'] = 'lion@mail.ru'

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

        for field in saved_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], context[field])

    def test_used_login(self):
        context = correct_user.copy()
        context['login'] = 'test-login0'

        resp = self.client.post(reverse('predictor:register'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/register.html')

        self.assertTrue('incorrect_login' in resp.context)
        self.assertTrue(resp.context['incorrect_login'])

        for field in saved_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], context[field])






