from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from predictor.views_utils import make_prediction, check_content, is_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .models import AlgorithmSettings


@login_required(login_url='/auth')
def index(request):
    """
    View for main page.

    :param request:
    Http request.

    :return:
    Prediction page or files with result.
    """
    context = {}
    # Checking user rights for showing research page.
    if request.user.groups.filter(name='researcher').exists():
        context['research_rights'] = True

    # Processing user uploading files for calculating prediction.
    if request.method == 'POST' and 'input_data' in request.FILES:
        try:
            response = HttpResponse()
            make_prediction(request.FILES['input_data'], response)
            request.session['result'] = response.getvalue().decode()
        except Exception:
            context['invalid_data'] = True

    # Processing user logout.
    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:index'))

    # Processing sending prediction files to user.
    if request.method == 'GET' and 'download' in request.GET and \
            'result' in request.session:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="predictions.csv'
        response.write(request.session['result'])
        return response

    # Processing showing prediction result to user.
    if 'result' in request.session:
        if len(request.session['result']) > settings.TEXT_FIELD_MAX_LENGTH:
            context['result_description'] = \
                request.session['result'][0:settings.TEXT_FIELD_MAX_LENGTH] \
                + '...'
        else:
            context['result_description'] = request.session['result']

    return render(request, 'predictor/index.html', context)


def auth(request):
    """
    View for authorisation page.

    :param request:
    Http request.

    :return:
    Authorisation page or redirection to next page.
    """
    if request.method == 'POST' and 'submit' in request.POST:
        # Checking necessary_fields.
        necessary_fields = ('username', 'password')
        error_context = check_content(necessary_fields, request.POST)
        if error_context:
            return render(request, 'predictor/auth.html', error_context)

        # Checking user details.
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
    """
    View for registration page. And added registered users.

    :param request:
    Http request.

    :return:
    Registration page or redirection to authorisation page.
    """
    if request.method == 'POST':
        # Check necessary fields.
        necessary_fields = ('first_name', 'last_name', 'email', 'password',
                            'login', 'question', 'password_double', 'answer')
        error_context = check_content(necessary_fields, request.POST)

        # Check main fields
        if not error_context:
            if User.objects.filter(username=request.POST['login']):
                error_context['another_name'] = True
            if User.objects.filter(email=request.POST['email']):
                error_context['another_name'] = True
            if request.POST['password'] != request.POST['password_double']:
                error_context['not_match_passwords'] = True
            if not is_email(request.POST['email']):
                error_context['another_email'] = True

        if error_context:
            return render(request, 'predictor/register.html', error_context)

        # Adding user.
        user = User.objects.create_user(request.POST['login'],
                                        request.POST['email'],
                                        request.POST['password'],
                                        first_name=request.POST['first_name'],
                                        last_name=request.POST['last_name'])

        user_settings = AlgorithmSettings(user=user,
                                          question=request.POST['question'],
                                          answer=request.POST['answer'])
        user_settings.save()

        if 'is_researcher' in request.POST:
            group = Group.objects.get_or_create(name='researcher')
            user.groups.add(group[0])
            user.save()

        return HttpResponseRedirect(reverse('predictor:auth'))
    return render(request, 'predictor/register.html', {})


def restore(request):
    """
    View for restore password page.

    :param request:
    Http request.

    :return:
    Restore password page or redirection to authorisation page.
    """
    if request.method == 'GET' and 'restore' in request.GET:
        return HttpResponseRedirect(reverse('predictor:auth'))

    return render(request, 'predictor/restore.html', {})


@login_required(login_url='/auth')
def research_page(request):
    """
    View for researcher page.

    :param request:
    Http request.

    :return:
    Researcher page.
    """
    # Checking user rights for showing research page.
    if not request.user.groups.filter(name='researcher').exists():
        return HttpResponseRedirect(reverse('predictor:index'))

    # Processing user uploading files for calculating prediction.
    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:research'))

    return render(request, 'predictor/research.html', {})
