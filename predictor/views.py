import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse


# todo add correct downloading result file
def index(request):
    if request.method == 'POST':
        result = ''
        if 'menu' in request.FILES and 'file' in request.FILES:
            for chunk in request.FILES['menu'].chunks():
                result += chunk.decode()
            result += ' '
            for chunk in request.FILES['file'].chunks():
                result += chunk.decode()
        request.session['result'] = result
        return render(request, 'predictor/index.html', {'some_text': result})
    if request.method == 'GET' and 'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'
        writer = csv.writer(response)
        writer.writerow(request.session['result'])
        return response
    return render(request, 'predictor/index.html', {})
