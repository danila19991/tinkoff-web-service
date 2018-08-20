import csv
from django.shortcuts import render


def index(request):
    if request.method == 'POST' and 'file' in request.FILES:
        request.session['result'] = make_prediction(request.FILES['file'])

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
        #todo add anouther string view for list
        str_result = ''
        for row in request.session['result']:
            str_result += str(row)[1:-1] + '\n'
            if len(str_result) > 200:
                break

        return render(request, 'predictor/index.html',
                      {'some_text': str_result})
    else:
        return render(request, 'predictor/index.html', {})


def auth(request):
    if request.method == 'GET' and 'submit' in request.GET:
        return HttpResponseRedirect(reverse('predictor:index'))
    return render(request, 'predictor/auth.html', {})
