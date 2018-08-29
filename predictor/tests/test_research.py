from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.views_utils import crete_user_with_settings, \
    create_dict_for_algorithm_description
from predictor.models import AlgorithmSettings
from tempfile import NamedTemporaryFile
from csv import writer as csv_writer
from random import randint, choice
from string import ascii_lowercase, digits, whitespace
from os import path, remove
from django.core.files import File


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


default_settings = {
    'algorithm_name': 'LinearRegression',
    'algorithm_package': 'linear_model',
    'algorithm_settings': '''{
    "fit_intercept": true,
    "normalize": false,
    "copy_X": true,
    "n_jobs": 1
}''',
    'parser_proportion': 0.7,
    'parser_rows': '',
    'parser_raw_date': True,
    'debug_info': False
}


correct_settings = {
    'algorithm_name': 'Ridge',
    'algorithm_package': 'linear_model',
    'algorithm_settings': '''{
    "alpha": 1.0,
    "fit_intercept": true,
    "normalize": false,
    "copy_X": true,
    "max_iter": null,
    "tol": 0.001,
    "solver": "auto",
    "random_state": null
}''',
    'parser_proportion': 0.8,
    'parser_rows': 100
}


save_fields = ('algorithm_name', 'algorithm_package', 'algorithm_settings',
               'parser_proportion', 'parser_rows')


def random_dish():
    return ''.join(choice(ascii_lowercase + digits + whitespace)
                   for _ in range(randint(15, 25)))


class TestResearchPageSimple(TestCase):

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
            alg_settings = AlgorithmSettings.objects.get(user=user)
            if path.isfile(str(alg_settings.model_file)):
                remove(str(alg_settings.model_file))
            user.delete()

    def setUp(self):
        user = User.objects.get(username='test-user2')
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/research')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('predictor:research'))
        self.assertEqual(resp.status_code, 200)

    def test_right_template_used(self):

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

    def test_no_user_rights(self):
        self.client.logout()
        user = User.objects.get(username='test-user1')
        self.client.force_login(user=user)

        resp = self.client.get(reverse('predictor:research'))

        self.assertRedirects(resp, reverse('predictor:index'))

    def test_user_not_login(self):
        self.client.logout()

        resp = self.client.get(reverse('predictor:research'))

        self.assertRedirects(resp, reverse('predictor:auth') + '?next=' +
                             reverse('predictor:research'))

    def test_right_default_settings(self):

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in save_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], default_settings[field],
                             msg=field)
        self.assertFalse('result_description' in resp.context)

    def test_transfer_algorithm_settings_to_dict(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        context = create_dict_for_algorithm_description(alg_settings)

        for field in save_fields:
            self.assertTrue(field in context)
            self.assertEqual(context[field], default_settings[field],
                             msg=field)

    def test_correct_fields_template(self):
        context = correct_settings.copy()
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in save_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], str(correct_settings[field]),
                             msg=field)

        self.assertFalse('result_description' in resp.context)

    def test_correct_fields_db(self):
        context = correct_settings.copy()
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        algorithm = create_dict_for_algorithm_description(alg_settings)

        for field in save_fields:
            self.assertTrue(field in algorithm)
            if algorithm[field]:
                self.assertEqual(algorithm[field], correct_settings[field],
                                 msg=field)

        self.assertFalse('result_description' in resp.context)

    def test_empty_text_fields(self):
        text_fields = ('algorithm_name', 'algorithm_package',
                       'algorithm_settings', 'parser_proportion')

        context = correct_settings.copy()
        context['submit'] = ''

        for field in text_fields:
            context[field] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in text_fields:
            self.assertTrue('no_' + field in resp.context, msg=field)
            self.assertTrue(resp.context['no_' + field], msg=field)

        self.assertFalse('result_description' in resp.context)

    def test_big_text_fields(self):
        text_fields = ('algorithm_name', 'algorithm_package',
                       'algorithm_settings', 'parser_proportion',
                       'parser_rows')

        context = correct_settings.copy()
        context['submit'] = ''

        for field in text_fields:
            context[field] = '1'*3000

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in text_fields:
            self.assertTrue('incorrect_' + field in resp.context, msg=field)
            self.assertTrue(resp.context['incorrect_' + field], msg=field)

        self.assertFalse('result_description' in resp.context)

    def test_middle_text_fields(self):
        text_fields = ('algorithm_name', 'algorithm_package',
                       'algorithm_settings', 'parser_proportion',
                       'parser_rows')

        context = correct_settings.copy()
        context['submit'] = ''

        for field in text_fields:
            context[field] = '1'*300

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in text_fields:
            if field != 'algorithm_settings':
                self.assertTrue('incorrect_' + field in resp.context,
                                msg=field)
                self.assertTrue(resp.context['incorrect_' + field], msg=field)

        self.assertFalse('result_description' in resp.context)

    def test_incorrect_text_fields(self):
        text_fields = ('algorithm_name', 'algorithm_package',
                       'algorithm_settings', 'parser_proportion',
                       'parser_rows')

        context = correct_settings.copy()
        context['submit'] = ''

        for field in text_fields:
            context[field] = '<p>kill all</p>'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in text_fields:
            self.assertTrue('incorrect_' + field in resp.context, msg=field)
            self.assertTrue(resp.context['incorrect_' + field], msg=field)

        self.assertFalse('result_description' in resp.context)

    def test_parser_rows_empty_check(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        alg_settings.parser_rows = 100
        alg_settings.save()

        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_rows'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        alg_settings = AlgorithmSettings.objects.get(user=user)
        algorithm = create_dict_for_algorithm_description(alg_settings)

        self.assertTrue('parser_rows' in algorithm)
        self.assertEqual(algorithm['parser_rows'], '')

        self.assertFalse('result_description' in resp.context)

    def test_incorrect_int(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_rows'] = '100a'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_parser_rows' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_rows'])

        self.assertFalse('result_description' in resp.context)

    def test_small_int(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_rows'] = '-1'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_parser_rows' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_rows'])

        self.assertFalse('result_description' in resp.context)

    def test_incorrect_float(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_proportion'] = '0.1a'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_parser_proportion' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_proportion'])

        self.assertFalse('result_description' in resp.context)

    def test_big_float(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_proportion'] = '1.1'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        print(resp.context)

        self.assertTrue('incorrect_parser_proportion' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_proportion'])

        self.assertFalse('result_description' in resp.context)

    def test_small_float(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_proportion'] = '0'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_parser_proportion' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_proportion'])

        self.assertFalse('result_description' in resp.context)

    def test_incorrect_json(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['algorithm_settings'] = '{"my_area":"some text </textarea>' \
                                        '<textarea name="algorithm_settings' \
                                        '" rows="15" cols="150" style="width' \
                                        ': 100%"> some text"}'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_algorithm_settings' in resp.context)
        self.assertTrue(resp.context['incorrect_algorithm_settings'])

        self.assertFalse('result_description' in resp.context)

    def test_big_correct_json(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['algorithm_settings'] = '{'

        for i in range(1000):
            context['algorithm_settings'] += '"field'+str(i) + \
                                             '":"very important text\n'
        context['algorithm_settings'] = '"size":1000}'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_algorithm_settings' in resp.context)
        self.assertTrue(resp.context['incorrect_algorithm_settings'])

        self.assertFalse('result_description' in resp.context)

    def test_zero_parse_rows(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_rows'] = '0'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_parser_rows' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_rows'])

        self.assertFalse('result_description' in resp.context)

    def test_one_parse_rows(self):
        context = correct_settings.copy()
        context['submit'] = ''

        context['parser_rows'] = '1'

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('incorrect_parser_rows' in resp.context)
        self.assertTrue(resp.context['incorrect_parser_rows'])

        self.assertFalse('result_description' in resp.context)

    def test_bool_save_db_true_to_false(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = False
        alg_settings.parser_raw_date = False
        alg_settings.save()

        context = correct_settings.copy()
        context['submit'] = ''
        context['parser_raw_date'] = ''
        context['debug_info'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertTrue(alg_settings.parser_raw_date)
        self.assertTrue(alg_settings.with_debug)

        self.assertFalse('result_description' in resp.context)

    def test_bool_save_db_false_to_true(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = True
        alg_settings.parser_raw_date = True
        alg_settings.save()

        context = correct_settings.copy()
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertFalse(alg_settings.parser_raw_date)
        self.assertFalse(alg_settings.with_debug)

        self.assertFalse('result_description' in resp.context)

    def test_bool_get_from_db_false(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = False
        alg_settings.parser_raw_date = False
        alg_settings.save()

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('parser_raw_date' in resp.context)
        self.assertFalse(resp.context['parser_raw_date'])
        self.assertTrue('debug_info' in resp.context)
        self.assertFalse(resp.context['debug_info'])

        self.assertFalse('result_description' in resp.context)

    def test_bool_get_from_db_true(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = True
        alg_settings.parser_raw_date = True
        alg_settings.save()

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('parser_raw_date' in resp.context)
        self.assertTrue(resp.context['parser_raw_date'])
        self.assertTrue('debug_info' in resp.context)
        self.assertTrue(resp.context['debug_info'])

        self.assertFalse('result_description' in resp.context)

    def test_bool_set_true(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = False
        alg_settings.parser_raw_date = False
        alg_settings.save()

        context = correct_settings.copy()
        context['submit'] = ''
        context['parser_raw_date'] = ''
        context['debug_info'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('parser_raw_date' in resp.context)
        self.assertTrue(resp.context['parser_raw_date'])
        self.assertTrue('debug_info' in resp.context)
        self.assertTrue(resp.context['debug_info'])

        self.assertFalse('result_description' in resp.context)

    def test_bool_set_false(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = True
        alg_settings.parser_raw_date = True
        alg_settings.save()

        context = correct_settings.copy()
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('parser_raw_date' in resp.context)
        self.assertFalse(resp.context['parser_raw_date'])
        self.assertTrue('debug_info' in resp.context)
        self.assertFalse(resp.context['debug_info'])

        self.assertFalse('result_description' in resp.context)

    def test_no_result_description(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = True
        alg_settings.parser_raw_date = True
        alg_settings.save()

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertFalse('result_description' in resp.context)

    def test_has_result_description(self):
        result = 'metric: 0.12\n quality: False'

        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.model_results = result
        alg_settings.save()

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('result_description' in resp.context)
        self.assertEqual(resp.context['result_description'], result)
        self.assertNotEqual(resp.context['result_description'],
                            'Train failed.')

    def test_session_saving_text_fields(self):
        session = self.client.session
        for field in save_fields:
            session[field] = correct_settings[field]
        session.save()

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        for field in save_fields:
            self.assertTrue(field in resp.context)
            self.assertEqual(resp.context[field], correct_settings[field],
                             msg=field)

    def test_bool_was_true(self):
        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.with_debug = False
        alg_settings.parser_raw_date = False
        alg_settings.save()

        session = self.client.session
        session['debug_info'] = True
        session['parser_raw_date'] = True
        session.save()

        resp = self.client.get(reverse('predictor:research'))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        self.assertTrue('parser_raw_date' in resp.context)
        self.assertTrue(resp.context['parser_raw_date'])
        self.assertTrue('debug_info' in resp.context)
        self.assertTrue(resp.context['debug_info'])

        self.assertFalse('result_description' in resp.context)


class TestResearchPageNewModel(TestCase):

    def setUp(self):
        context = correct_user.copy()
        context['login'] = 'test-user2'
        context['email'] = 'oleg@yandex.ru'
        context['is_researcher'] = ''
        crete_user_with_settings(context)
        user = User.objects.get(username='test-user2')
        self.client.force_login(user=user)

    def tearDown(self):
        for user in User.objects.all():
            alg_settings = AlgorithmSettings.objects.get(user=user)
            if path.isfile(str(alg_settings.model_file)):
                remove(str(alg_settings.model_file))
            user.delete()

    def test_no_result_correct_train(self):
        train = NamedTemporaryFile(mode='w+')
        train_csv = csv_writer(train)
        train_csv.writerow(['chknum', 'person_id', 'month', 'day', 'good',
                            'good_id'])
        for i in range(100):
            train_csv.writerow(["id" + str(i), str(randint(20, 200)), '1',
                            '17', random_dish(), str(i + 1)])
        train.seek(0)

        context = correct_settings.copy()
        context['train_data'] = train
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertNotEqual(alg_settings.model_results, '')

        self.assertTrue('result_description' in resp.context)
        self.assertEqual(resp.context['result_description'],
                         alg_settings.model_results)

    def test_no_result_incorrect_train(self):
        train = NamedTemporaryFile(mode='w+')
        train.write('It is cool school!')
        train.seek(0)

        context = correct_settings.copy()
        context['train_data'] = train
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertEqual(alg_settings.model_results, '')

        self.assertTrue('result_description' in resp.context)
        self.assertEqual(resp.context['result_description'], 'Train failed.')

    def test_has_result_incorrect_train(self):
        result = 'metric: 0.12\n quality: False'

        user = User.objects.get(username='test-user2')
        alg_settings = AlgorithmSettings.objects.get(user=user)
        alg_settings.model_results = result
        alg_settings.save()

        train = NamedTemporaryFile(mode='w+')
        train.write('It is cool school!')
        train.seek(0)

        context = correct_settings.copy()
        context['train_data'] = train
        context['submit'] = ''

        resp = self.client.post(reverse('predictor:research'), context)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'predictor/research.html')

        alg_settings = AlgorithmSettings.objects.get(user=user)

        self.assertEqual(alg_settings.model_results, result)

        self.assertTrue('result_description' in resp.context)
        self.assertEqual(resp.context['result_description'], 'Train failed.')
