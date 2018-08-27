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

