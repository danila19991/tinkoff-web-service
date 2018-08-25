from django.contrib.auth import authenticate, login
from mlalgorithms.shell import Shell
from re import compile
from os import path, mkdir, remove
from json import loads
from time import sleep
from django.core.files import File
from django.contrib.auth.models import User, Group
from .models import AlgorithmSettings

prog = compile(r"^[-0-9\w\s\.@]+$")


def generate_model(package, algorithm, user_id):
    '''
    Function for creating new model source.

    :param package:
    Name of package.

    :param algorithm:
    Name of algorithm.

    :param user_id:
    Unique id for file.

    '''
    if not path.exists('models'):
        mkdir('models')
    file = open('models/' + str(user_id) + '.py', 'w+')
    file.write(
f'''
import numpy as np

from sklearn.{package} import {algorithm}

from mlalgorithms.models import model


class user_model(model.IModel):

    def __init__(self, **kwargs):
        self.model = {algorithm}(**kwargs)

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels, **kwargs)

    def predict(self, samples, **kwargs):
        predicts = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predicts.append(prediction)
        return predicts


'''
    )
    file.close()


def make_train(train_data, alg_settings):
    '''
    Function for train new model.

    :param train_data:
    Data for train

    :param alg_settings:
    Model of user settings

    :return:
    Description of resulted model.
    '''
    generate_model(alg_settings.algorithm_package, alg_settings.algorithm_name,
                   alg_settings.user)
    params = {
        "selected_model": "user_model",
        "models": [
            {
                "model_module_name": "models." + str(alg_settings.user),
                "model_name": "user_model",

                "model_params": loads(alg_settings.algorithm_settings)
            }
        ],
        "selected_parser": "CommonParser",
        "parsers": [
            {
                "parser_module_name": "mlalgorithms.parsers.common_parser",
                "parser_name": "CommonParser",

                "parser_params": {
                    "proportion": alg_settings.parser_proportion,
                    "raw_date": alg_settings.parser_raw_date,
                    "n_rows": alg_settings.parser_rows
                }
            }
        ],
        "selected_metric": "f1",
        "metrics": {
            "mse": "MeanSquadError",
            "f1": "MeanF1Score"
        },

        "debug": alg_settings.with_debug
    }
    sh = Shell(existing_parsed_json_dict=params)
    sh.train(train_data)
    test_result, quality = sh.test()
    sh.save_model("models/" + str(alg_settings.user) + ".mdl")
    new_model = File(open("models/" + str(alg_settings.user) + ".mdl", "rb+"))
    alg_settings.model_file.delete()
    alg_settings.model_file = new_model
    alg_settings.save()
    new_model.close()
    if path.isfile("models/" + str(alg_settings.user) + ".mdl"):
        remove("models/" + str(alg_settings.user) + ".mdl")
    if path.isfile("models/" + str(alg_settings.user) + ".py"):
        remove("models/" + str(alg_settings.user) + ".py")
    return f'test_result: {test_result}\nquality: {quality}'


# todo set model according to user
def make_prediction(input_data, menu_data, result_data, model_name):
    """
    Function for make prediction on trained model.

    :param input_data: File
    Test data for getting prediction.

    :param menu_data: File
    Menu data for prediction.

    :param result_data: File
    Result of prediction in needed format.

    :param model_name:
    Path to model.
    """

    sh = Shell(existing_model_name=str(model_name))
    sh.predict(input_data, menu_data)
    sh.output(result_data)


def is_correct_string(line):
    '''
    Function for checking correction of string

    :param line:
    String for checking.

    :return:
    True if correct string False otherwise.
    '''
    if type(line) != str:
        return False
    try:
        line.encode()
    except Exception:
        return False
    return len(line) > 0 and prog.match(line)


def check_content(necessary_fields, have_fields, exist_context={},
                  max_len = 32):
    """
    Function for checking dict on contenting all necessary fields.

    :param necessary_fields:
    Fields which must contain have_fields.

    :param have_fields:
    Dict with fields we have.

    :param exist_context:
    Context which was added in template context before this function.

    :param max_len:
    Max len of string in input.

    :return:
    True if all ok False otherwise.
    """
    correct = True

    for field in necessary_fields:
        if field not in have_fields:
            correct = False
            exist_context['no_' + field] = True
        else:
            if type(have_fields[field]) == str:
                    if len(have_fields[field]) == 0:
                        correct = False
                        exist_context['no_' + field] = True
                    if not is_correct_string(have_fields[field]) or \
                            not len(have_fields[field]) < max_len:
                        correct = False
                        exist_context['incorrect_' + field] = True

    return correct


# todo change to more valid check
def is_email(email):
    """
    Function for validation users email.

    :param email: str
    String for checking if it is email.

    :return:
    True if it is correct email, False otherwise.
    """
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        print(validate_email(email))
        return True
    except ValidationError:
        return False


def authorise_user(request, context):
    '''
    Function for processing users signing in.

    :param request:
    Http request for processing.

    :param context:
    Existing context for page template.

    :return:
    True if user was authorised.
    '''
    necessary_fields = ('username', 'password')
    no_error_context = check_content(necessary_fields, request.POST,
                                     context)
    if no_error_context:
        # Checking user details.
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return True
        else:
            context['incorrect_username_or_password'] = True
    return False


def register_user(request, context, form_fields):
    '''
    Function for registration new user in system.

    :param request:
    Http request for registration.

    :param context:
    Existing context.

    :param form_fields:
    Fields for being saved in session.

    :return:
    True if user was registered, False otherwise.
    '''
    for field in form_fields:
        if field in request.POST:
            request.session[field] = request.POST[field]

    # Check necessary fields.
    necessary_fields = ('first_name', 'last_name', 'email', 'password',
                        'login', 'password_double',)
    long_fields = ('question', 'answer')
    no_error_context = check_content(necessary_fields, request.POST, context)
    no_error_context = check_content(long_fields, request.POST, context, 128)\
                       and no_error_context

    # Check main fields
    if no_error_context:
        if User.objects.filter(username=request.POST['login']):
            context['incorrect_login'] = True
            no_error_context = False

        if not is_email(request.POST['email']) or \
                User.objects.filter(email=request.POST['email']):
            context['incorrect_email'] = True
            no_error_context = False

        if request.POST['password'] != request.POST['password_double']:
            context['not_match_passwords'] = True
            no_error_context = False

    if not no_error_context:
        return False

    user = User.objects.create_user(request.POST['login'],
                                    request.POST['email'],
                                    request.POST['password'],
                                    first_name=request.POST['first_name'],
                                    last_name=request.POST['last_name'])

    # todo check if it need
    while True:
        try:
            default_model = File(open('models/default.mdl', 'rb+'))
            break
        except Exception:
            sleep(0.5)
    user_settings = AlgorithmSettings(user=user,
                                      question=request.POST['question'],
                                      answer=request.POST['answer'],
                                      model_file=default_model)
    user_settings.save()
    default_model.close()

    if 'is_researcher' in request.POST:
        group = Group.objects.get_or_create(name='researcher')
        user.groups.add(group[0])
        user.save()

    return True


def fill_context(request, context, form_fields):
    '''
    Function for filling context with form_fields with values from session if
     they in session.

    :param request:
    Http request with session.

    :param context:
    Existing form context.

    :param form_fields:
    Fields for checking.
    '''
    for field in form_fields:
        if field in request.session:
            context[field] = request.session[field]
