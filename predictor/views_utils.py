from mlalgorithms.shell import Shell
import re, os, json
from django.core.files import File

prog = re.compile(r"^[0-9\w\s\.-@]+$")


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
    if not os.path.exists('models'):
        os.mkdir('models')
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

                "model_params": json.loads(alg_settings.algorithm_settings)
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
    if os.path.isfile("models/" + str(alg_settings.user) + ".mdl"):
        os.remove("models/" + str(alg_settings.user) + ".mdl")
    if os.path.isfile("models/" + str(alg_settings.user) + ".py"):
        os.remove("models/" + str(alg_settings.user) + ".py")
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
                    if not is_correct_string(have_fields[field]) and \
                            len(have_fields[field]) < max_len:
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