import csv
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from predictor.views_utils import make_prediction
from predictor.views_utils import check_content
from predictor.views_utils import is_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


@login_required(login_url='/auth')
def index(request):
    if request.method == 'POST' and 'input_data' in request.FILES:
        try:
            request.session['result'] = \
                make_prediction(request.FILES['input_data'])
        except:
            return render(request, 'predictor/index.html',
                          {'invalid_data': True})

    if request.method == 'GET' and 'logout' in request.GET:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:index'))

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
        # TODO: add another string view for list
        str_result = ''
        for row in request.session['result']:
            str_result += str(row)[1:-1] + '\n'
            if len(str_result) > 200:
                break

        return render(request, 'predictor/index.html',
                      {'result_description': str_result})
    else:
        return render(request, 'predictor/index.html', {})


def auth(request):
    if request.method == 'POST' and 'submit' in request.POST:
        necessary_fields = ('username', 'password')

        error_context = check_content(necessary_fields, request.POST)

        if error_context:
            return render(request, 'predictor/auth.html', error_context)

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if 'next' in request.GET:
                return HttpResponseRedirect(request.GET['next'])
            else:
                return HttpResponseRedirect(reverse('predictor:index'))
        else:
            return render(request, 'predictor/auth.html',
                          {'wrong_username_or_password': True})

    return render(request, 'predictor/auth.html', {})


def register_page(request):
    if request.method == 'POST':
        necessary_fields = ('first_name', 'last_name', 'email', 'password')

        error_context = check_content(necessary_fields, request.POST)

        if not error_context:
            if User.objects.filter(username=request.POST['email']):
                error_context['another_name'] = True
            if is_email(request.POST['email']):
                error_context['another_email'] = True

        if error_context:
            return render(request, 'predictor/register.html', error_context)

        User.objects.create_user(request.POST['email'], request.POST['email'],
                                 request.POST['password'],
                                 first_name=request.POST['first_name'],
                                 last_name=request.POST['last_name'])
        return HttpResponseRedirect(reverse('predictor:auth'))
    return render(request, 'predictor/register.html', {})


def restore(request):
    if request.method == 'GET' and 'restore' in request.GET:
        return HttpResponseRedirect(reverse('predictor:auth'))

    return render(request, 'predictor/restore.html', {})


@login_required(login_url='/auth')
def research_page(request):
    if request.method == 'GET' and 'logout' in request.GET:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:research'))

    return render(request, 'predictor/research.html', {})
