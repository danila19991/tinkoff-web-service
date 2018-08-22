from mlalgorithms.shell import Shell


# todo get model from db not train
def make_prediction(input_data, result_data):
    """
    Function for make prediction on trained model.

    :param input_data: File
    Test data for getting prediction.

    :param result_data: File
    Result of prediction in needed format.
    """
    sh = Shell()
    sh.train(input_data)
    sh.test()
    sh.output(result_data)


# todo add security checks for fields
def check_content(necessary_fields, have_fields):
    """
    Function for checking dict on contenting all necessary fields.

    :param necessary_fields:
    Fields which must contain have_fields.

    :param have_fields:
    Dict with fields we have.

    :return:
    Dict with fields which was missed with 'no_'.
    """
    missing_context = {}

    for field in necessary_fields:
        if field not in have_fields:
            missing_context['no_' + field] = True

    return missing_context


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
