from predictor.views_utils import get_md5_from_two_files
from predictor.views_utils import add_new_result
from django.http import HttpResponse
from django.shortcuts import render
from predictor.models import Result


def index(request):
    if request.method == 'POST':
        if 'menu' not in request.FILES or 'file' not in request.FILES:
            #todo add message with error
            return render(request, 'predictor/index.html', {})

        result = get_md5_from_two_files(request.FILES['menu'],
                                        request.FILES['file'])

        request.session['result'] = result

        predict = Result.objects.filter(key_hash=result)

        if not len(predict):
            add_new_result(request.FILES['menu'], request.FILES['file'],
                           result)

        description = b''

        for line in Result.objects.get(key_hash=result).prediction.readlines():
            description += line
            if len(line) > 800:
                break

        request.session['description'] = description.decode()
    if request.method == 'GET' and 'download' in request.GET and\
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
