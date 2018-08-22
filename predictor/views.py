from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from predictor.views_utils import make_prediction, check_content, is_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .models import AlgorithmSettings


@login_required(login_url='/auth')
def index(request):
    context = {}
    if request.user.groups.filter(name='researcher').exists():
        context['research_rights'] = True
    if request.method == 'POST' and 'input_data' in request.FILES:
        try:
            response = HttpResponse()
            make_prediction(request.FILES['input_data'], response)
            request.session['result'] = response.getvalue().decode()
        except Exception:
            context['invalid_data'] = True

    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:index'))

    if request.method == 'GET' and 'download' in request.GET and\
            'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'
        response.write(request.session['result'])
        return response

    if 'result' in request.session:
        if len(request.session['result']) > 200:
            context['result_description'] = request.session['result'][0:200]\
                                            + '...'
        else:
            context['result_description'] = request.session['result']

    return render(request, 'predictor/index.html', context)


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
        necessary_fields = ('first_name', 'last_name', 'email', 'password',
                            'login')

        error_context = check_content(necessary_fields, request.POST)

        if not error_context:
            if User.objects.filter(username=request.POST['login']):
                error_context['another_name'] = True
            if is_email(request.POST['email']):
                error_context['another_email'] = True

        if error_context:
            return render(request, 'predictor/register.html', error_context)

        user = User.objects.create_user(request.POST['login'],
                                        request.POST['email'],
                                        request.POST['password'],
                                        first_name=request.POST['first_name'],
                                        last_name=request.POST['last_name'])

        user_settings = AlgorithmSettings(user=user)
        user_settings.save()

        if 'is_researcher' in request.POST:
            group = Group.objects.get_or_create(name='researcher')
            user.groups.add(group[0])
            user.save()

        return HttpResponseRedirect(reverse('predictor:auth'))
    return render(request, 'predictor/register.html', {})


def restore(request):
    if request.method == 'GET' and 'restore' in request.GET:
        return HttpResponseRedirect(reverse('predictor:auth'))

    return render(request, 'predictor/restore.html', {})


@login_required(login_url='/auth')
def research_page(request):
    if not request.user.groups.filter(name='researcher').exists():
        return HttpResponseRedirect(reverse('predictor:index'))

    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:research'))

    return render(request, 'predictor/research.html', {})
