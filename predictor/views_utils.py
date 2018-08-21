from mlalgorithms.shell import Shell


def make_prediction(input_data, result_data):
    sh = Shell()
    sh.train(input_data)
    sh.test()
    sh.output(result_data)
    return sh.get_formatted_predictions()


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
