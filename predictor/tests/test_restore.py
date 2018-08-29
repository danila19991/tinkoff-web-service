from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from predictor.models import AlgorithmSettings
from predictor.views_utils import crete_user_with_settings


correct_user = {
    'first_name': 'oleg',
    'last_name': 'tester',
    'login': 'test-login0',
    'email': 'lion@mail.ru',
    'password': 'OlEgCOdEr',
    'password_double': 'OlEgCOdEr',
    'question': 'How many wheels had a Telezhka',
    'answer': 'three',
    'register': ''
}


class TestRestorePageSimple(TestCase):

    @classmethod
    def setUpTestData(cls):
        context = correct_user.copy()
        crete_user_with_settings(context)
        context['login'] = 'test-login2'
        context['email'] = 'oleg@yandex.ru'
        context['is_researcher'] = ''
        crete_user_with_settings(context)

    @classmethod
    def tearDownClass(cls):
        for user in User.objects.all():
            alg_settings = AlgorithmSettings.objects.get(user=user)
            alg_settings.model_file.delete()
            user.delete()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/restore')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('predictor:restore'))
        self.assertEqual(resp.status_code, 200)

    def test_right_template_used(self):
        resp = self.client.get(reverse('predictor:restore'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

    def test_wrong_email(self):
        context = {'email': 'oleg@yamdex.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

    def test_empty_email(self):
        context = {'email': '', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

    def test_incorrect_email(self):
        context = {'email': '<p>my-email@pm.ru</p>', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

    def test_big_email(self):
        context = {'email': 'q'*1000+'@mail.com', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

    def test_correct_email(self):
        context = {'email': 'lion@mail.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_redirection_signed_in(self):
        user = User.objects.get(username='test-login0')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:restore'))

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_signed_in_index(self):
        user = User.objects.get(username='test-login0')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:restore') + '?next=' +
                               reverse('predictor:index'))

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_signed_in_research(self):
        user = User.objects.get(username='test-login0')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:restore') + '?next=' +
                               reverse('predictor:research'), follow=True)

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_redirection_signed_in_research_researcher(self):
        user = User.objects.get(username='test-login2')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:restore') + '?next=' +
                               reverse('predictor:research'))

        self.assertRedirects(resp, reverse('predictor:research'))


class TestRestorePageWithEmail(TestCase):

    @classmethod
    def setUpTestData(cls):
        context = correct_user.copy()
        crete_user_with_settings(context)
        context['login'] = 'test-login2'
        context['email'] = 'oleg@yandex.ru'
        context['question'] = 'Enter three'
        crete_user_with_settings(context)

    @classmethod
    def tearDownClass(cls):
        for user in User.objects.all():
            alg_settings = AlgorithmSettings.objects.get(user=user)
            alg_settings.model_file.delete()
            user.delete()

    def setUp(self):
        session = self.client.session
        session['user_email'] = 'lion@mail.ru'
        session['confirmed'] = False
        session.save()

    def tearDown(self):
        session = self.client.session
        session.flush()
        session.save()

    def test_update_after_email(self):
        resp = self.client.get(reverse('predictor:restore'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_empty_answer(self):
        context = {'answer': '', 'answer_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        self.assertTrue('incorrect_answer' in resp.context)
        self.assertTrue(resp.context['incorrect_answer'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_incorrect_answer(self):
        context = {'answer': 'os.kill_all()', 'answer_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        self.assertTrue('incorrect_answer' in resp.context)
        self.assertTrue(resp.context['incorrect_answer'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_big_answer(self):
        context = {'answer': 'z'*1000, 'answer_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        self.assertTrue('incorrect_answer' in resp.context)
        self.assertTrue(resp.context['incorrect_answer'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_wrong_answer(self):
        context = {'answer': 'four', 'answer_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        self.assertTrue('incorrect_answer' in resp.context)
        self.assertTrue(resp.context['incorrect_answer'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_wrong_email_after_correct(self):
        context = {'email': 'oleg@yamdex.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login0')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_correct_email_after_correct(self):
        context = {'email': 'oleg@yandex.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login2')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'oleg@yandex.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_correct_answer(self):
        context = {'answer': 'three', 'answer_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('confirmed' in resp.context)
        self.assertTrue(resp.context['confirmed'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])


class TestRestorePageWithConfirmed(TestCase):

    @classmethod
    def setUpTestData(cls):
        context = correct_user.copy()
        crete_user_with_settings(context)
        context['login'] = 'test-login2'
        context['email'] = 'oleg@yandex.ru'
        crete_user_with_settings(context)

    @classmethod
    def tearDownClass(cls):
        for user in User.objects.all():
            alg_settings = AlgorithmSettings.objects.get(user=user)
            alg_settings.model_file.delete()
            user.delete()

    def setUp(self):
        session = self.client.session
        session['user_email'] = 'lion@mail.ru'
        session['confirmed'] = True
        session.save()

    def tearDown(self):
        user = User.objects.get(username='test-login0')
        user.set_password('OlEgCOdEr')
        user.save()
        session = self.client.session
        session.flush()
        session.save()

    def test_empty_fields(self):
        fields = ('password', 'password_double')

        context = {'restore_button': ''}

        for field in fields:
            context[field] = ''

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('confirmed' in resp.context)
        self.assertTrue(resp.context['confirmed'])

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])

    def test_incorrect_fields(self):
        fields = ('password', 'password_double')

        context = {'restore_button': ''}

        for field in fields:
            context[field] = '<p>color=#000000</p>'

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('confirmed' in resp.context)
        self.assertTrue(resp.context['confirmed'])

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])

    def test_big_fields(self):
        fields = ('password', 'password_double')

        context = {'restore_button': ''}

        for field in fields:
            context[field] = 'p'*1000

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('confirmed' in resp.context)
        self.assertTrue(resp.context['confirmed'])

        for field in fields:
            self.assertTrue('incorrect_'+field in resp.context)
            self.assertTrue(resp.context['incorrect_'+field])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])

    def test_different_passwords(self):
        context = {'password': 'password',
                   'password_double': 'password-double', 'restore_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('confirmed' in resp.context)
        self.assertTrue(resp.context['confirmed'])

        self.assertTrue('not_match_password' in resp.context)
        self.assertTrue(resp.context['not_match_password'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])

    def test_wrong_email_after_confirm(self):
        context = {'email': 'oleg@yamdex.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        self.assertTrue('confirmed' in resp.context)
        self.assertTrue(resp.context['confirmed'])

        self.assertTrue('incorrect_email' in resp.context)
        self.assertTrue(resp.context['incorrect_email'])

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])

    def test_correct_email_after_confirm(self):
        context = {'email': 'oleg@yandex.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/restore.html')

        user = User.objects.get(username='test-login2')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue('secret_question' in resp.context)
        self.assertEqual(resp.context['secret_question'],
                         alg_settings.question)

        session = self.client.session
        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'oleg@yandex.ru')

        self.assertTrue('confirmed' in session)
        self.assertFalse(session['confirmed'])

    def test_correct_passwords(self):
        context = {'password': 'password',
                   'password_double': 'password', 'restore_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        self.assertRedirects(resp, reverse('predictor:auth'))

        user = User.objects.get(username='test-login0')
        self.assertTrue(user.check_password('password'))

    def test_change_email_to_same(self):
        context = {'email': 'lion@mail.ru', 'email_button': ''}

        resp = self.client.post(reverse('predictor:restore'), context)

        session = self.client.session

        self.assertTrue('user_email' in session)
        self.assertEqual(session['user_email'], 'lion@mail.ru')

        self.assertTrue('confirmed' in session)
        self.assertTrue(session['confirmed'])
