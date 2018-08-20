import csv
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


def index(request):
    if request.method == 'POST':
        result = b''
        if 'file' in request.FILES:
            for chunk in request.FILES['file'].chunks():
                result += chunk
        request.session['result'] = result.decode()
        return render(request, 'predictor/index.html', {'some_text': result})
    if request.method == 'GET' and 'download' in request.GET and\
            'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'
        writer = csv.writer(response)
        writer.writerow(request.session['result'])
        return response
    if 'result' in request.session:
        return render(request, 'predictor/index.html',
                      {'some_text': request.session['result']})
    else:
        return render(request, 'predictor/index.html', {})


def auth(request):
    if request.method == 'GET' and 'submit' in request.GET:
        return HttpResponseRedirect(reverse('predictor:index'))

    return render(request, 'predictor/auth.html', {})


def register_page(request):
    if request.method == 'GET' and 'register' in request.GET:
        return HttpResponseRedirect(reverse('predictor:auth'))
    return render(request, 'predictor/register.html', {})

