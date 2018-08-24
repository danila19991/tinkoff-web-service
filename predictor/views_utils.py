from mlalgorithms.shell import Shell
import re

prog = re.compile(r"^[-0-9\w\s\.@]+$")


# todo get model from db not train
def make_prediction(input_data, menu_data, result_data):
    """
    Function for make prediction on trained model.

    :param input_data: File
    Test data for getting prediction.

    :param menu_data: File
    Menu data for prediction.

    :param result_data: File
    Result of prediction in needed format.
    """
    sh = Shell(existing_model_name='forest_model')
    sh.predict(input_data, menu_data)
    sh.output(result_data)


def is_correct_string(line):
    if type(line) != str:
        return False
    try:
        line.encode()
    except Exception:
        return False
    return len(line) > 0 and prog.match(line)


# todo add security checks for fields
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
