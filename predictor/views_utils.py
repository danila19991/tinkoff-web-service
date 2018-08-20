from ml_algorithm.shell import Shell


def make_prediction(input_data):
    sh = Shell()
    sh.predict(input_data)
    sh.test()
    return sh.predictions


def check_content(necessary_fields, have_fields):
    missing_context = {}

    for field in necessary_fields:
        if field not in have_fields:
            missing_context['no_' + field] = True

    return missing_context


# todo change to more valid check
def is_email(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
