import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse


def index(request):
    if request.method == 'POST':
        with open('data.cvs', 'wb+') as f:
            for chunk in request.FILES['menu'].chunks():
                f.write(chunk)
            f.write('\n'.encode())
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="predictions.csv'
        writer = csv.writer(response)
        writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
        writer.writerow(
            ['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
        return response
    return render(request, 'predictor/index.html', {})
