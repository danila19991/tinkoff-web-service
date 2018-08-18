from predictor.views_utils import get_md5_from_two_files
from predictor.views_utils import add_new_result
from predictor.views_utils import read_people_file
from predictor.views_utils import read_menu_file
from django.http import HttpResponse
from django.shortcuts import render
from predictor.models import Result


# todo split this method
def index(request):
    if request.method == 'POST':
        if 'menu' not in request.FILES or 'file' not in request.FILES:
            no_menu = None
            if 'menu' not in request.FILES:
                no_menu = True

            no_people = None
            if 'file' not in request.FILES:
                no_people = True

            return render(request, 'predictor/index.html',
                          {'no_people': no_people, 'no_menu': no_menu})

        result = get_md5_from_two_files(request.FILES['menu'],
                                        request.FILES['file'])

        request.session['result'] = result

        predict = Result.objects.filter(key_hash=result)

        if not len(predict):

            menu_parse_error = False
            menu_data = read_menu_file(request.FILES['menu'])
            if not menu_data:
                menu_parse_error = True

            people_parse_error = None
            people_data = read_people_file(request.FILES['file'])
            if not people_data:
                people_parse_error = True

            if menu_parse_error or people_parse_error:
                return render(request, 'predictor/index.html',
                              {'people_parse_error': people_parse_error,
                               'menu_parse_error': menu_parse_error
                               })

            add_new_result(menu_data, people_data, result)

        description = b''

        for line in Result.objects.get(key_hash=result).prediction.readlines():
            description += line
            if len(line) > 800:
                break

        request.session['description'] = description.decode()
    if request.method == 'GET' and 'download' in request.GET and \
            'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'

        result = Result.objects.get(key_hash=request.session['result'])
        for chunk in result.prediction.chunks():
            response.write(chunk)

        return response
    if 'description' not in request.session:
        return render(request, 'predictor/index.html', {})

    return render(request, 'predictor/index.html',
                  {'some_text': request.session['description']})
