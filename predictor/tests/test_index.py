from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from predictor.views_utils import create_user_with_settings
from predictor.models import AlgorithmSettings
from tempfile import NamedTemporaryFile
from string import ascii_lowercase, digits, whitespace
from random import choice, randint
from csv import writer as csv_writer


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


def random_dish():
    return ''.join(choice(ascii_lowercase + digits + whitespace)
                   for _ in range(randint(15, 25)))


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

        self.assertTrue('no_input_data' in resp.context)
        self.assertTrue(resp.context['no_input_data'])

        self.assertTrue('no_input_menu' in resp.context)
        self.assertTrue(resp.context['no_input_menu'])

    def test_correct_files(self):
        test = NamedTemporaryFile(mode='w+')
        test_csv = csv_writer(test)
        test_csv.writerow(['chknum', 'person_id', 'month', 'day'])
        for i in range(159229, 159329):
            test_csv.writerow(["id" + str(i), str(randint(20, 200)), '5',
                               '25'])
        test.seek(0)

        menu = NamedTemporaryFile(mode='w+')
        menu_csv = csv_writer(menu)
        menu_csv.writerow(['month', 'day', 'good', 'good_id'])
        for i in range(1, 20):
            menu_csv.writerow(['5', '25', random_dish(), str(i)])
        menu.seek(0)

        context = {'code': '', 'input_data': test, 'input_menu': menu}

        resp = self.client.post(reverse('predictor:index'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/index.html')

        session = self.client.session

        self.assertFalse('incorrect_data' in resp.context)

        self.assertTrue('result' in session)

        self.assertTrue('result_description' in resp.context)
        self.assertEqual(resp.context['result_description'],
                         session['result'][0:settings.TEXT_FIELD_MAX_LENGTH] +
                         '...')

    def test_incorrect_files(self):
        test = NamedTemporaryFile(mode='w+')
        test.write('hasrcoded.')
        test.seek(0)

        menu = NamedTemporaryFile(mode='w+')
        menu.write('menu.')
        menu.seek(0)

        context = {'code': '', 'input_data': test, 'input_menu': menu}

        resp = self.client.post(reverse('predictor:index'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/index.html')

        self.assertTrue('incorrect_data' in resp.context)
        self.assertTrue(resp.context['incorrect_data'])

    def test_result_download(self):
        session = self.client.session
        session['result'] = '''chknum,pred
id159229,3 8 94
id159230,8 39 112
id159231,3 8 23
id159232,3 8 23
id159233,3 8 288
id159234,3 8 63
id159235,19 94 271
id159236,3 8 23
id159237,3 8 23
id159238,3 8 23
id159239,8 59 94
id159240,8 288
id159241,3 8 23
id159242,8 59'''
        session.save()

        resp = self.client.get(reverse('predictor:index'), {'download': ''})

        self.assertEqual(resp.content, session['result'].encode())

    def test_result_download_without_result(self):

        resp = self.client.get(reverse('predictor:index'), {'download': ''})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/index.html')


class TestAuthPageResearcherRights(TestCase):

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

    def tearDown(self):
        self.client.logout()

    def test_researcher_link_researcher(self):
        user = User.objects.get(username='test-user2')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:index'))

        self.assertTrue('research_rights' in resp.context)
        self.assertTrue(resp.context['research_rights'])

    def test_researcher_link_not_researcher(self):
        user = User.objects.get(username='test-user1')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:index'))

        self.assertFalse('research_rights' in resp.context)
