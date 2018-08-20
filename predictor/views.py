import csv
from django.shortcuts import render
from django.http import HttpResponse
from predictor.views_utils import make_prediction


def index(request):
    if request.method == 'POST':
        result = None
        if 'file' in request.FILES:
            result = make_prediction(request.FILES['file'])
        print(type(result))
        request.session['result'] = result
    if request.method == 'GET' and 'download' in request.GET and\
            'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'
        writer = csv.writer(response)
        for row in request.session['result']:
            writer.writerow(row)
        return response
    if 'result' in request.session:
        str_result = ''
        print(type(request.session['result']))
        for row in request.session['result']:
            str_result += str(row)[1:-1] + '\n'
            if len(str_result) > 200:
                break
        return render(request, 'predictor/index.html',
                      {'some_text': str_result})
    else:
        return render(request, 'predictor/index.html', {})
