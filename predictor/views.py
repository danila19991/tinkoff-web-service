import hashlib
import datetime

from predictor.predict_controller import make_prediction
from django.http import HttpResponse
from django.shortcuts import render
from predictor.models import Result


#todo refactor it
def index(request):
    if request.method == 'POST':
        hash_md5 = hashlib.md5()
        if 'menu' in request.FILES and 'file' in request.FILES:
            for chunk in request.FILES['menu'].chunks():
                hash_md5.update(chunk)
            hash_md5.update(b' salt ')
            for chunk in request.FILES['file'].chunks():
                hash_md5.update(chunk)
        result = hash_md5.hexdigest()
        request.session['result'] = result
        predict = Result.objects.filter(key_hash=result)
        print(len(predict))
        if not len(predict):
            #todo add any cashe cleaning
            #todo delete temp file or found how not to create it
            result = Result(key_hash=result, menu=request.FILES['menu'],
                            people=request.FILES['file'],
                            generation_time=datetime.datetime.now(),
                            prediction=make_prediction(request.FILES['menu'],
                                                       request.FILES['file'],
                                                       result))
            result.save(force_insert=True)
        return render(request, 'predictor/index.html', {'some_text': result})
    if request.method == 'GET' and 'download' in request.GET and\
            'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'
        pred = Result.objects.get(key_hash=
                                  request.session['result']).prediction
        for chunk in pred.chunks():
            response.write(chunk)
        return response
    return render(request, 'predictor/index.html', {})
