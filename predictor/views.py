import json
from django.shortcuts import render, get_object_or_404
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
    if request.method == 'POST' and 'code' in request.POST:
        # Check necessary files.
        necessary_fields = ('input_data', 'input_menu')
        no_error_context = check_content(necessary_fields, request.FILES,
                                         context)
        if no_error_context:
            try:
                response = HttpResponse()
                make_prediction(request.FILES['input_data'],
                                request.FILES['input_menu'], response)
                request.session['result'] = response.getvalue().decode()
            except Exception:
                context['incorrect_data'] = True

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
    context = {}
    if request.method == 'POST' and 'submit' in request.POST:
        # Checking necessary_fields.
        necessary_fields = ('username', 'password')
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)
        if no_error_context:
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
                context['incorrect_username_or_password'] = True

    return render(request, 'predictor/auth.html', context)


def register_page(request):
    """
    View for registration page. And added registered users.

    :param request:
    Http request.

    :return:
    Registration page or redirection to authorisation page.
    """
    context = {}
    if request.method == 'POST':
        # Check necessary fields.
        necessary_fields = ('first_name', 'last_name', 'email', 'password',
                            'login', 'question', 'password_double', 'answer')
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)

        # Check main fields
        if no_error_context:
            if User.objects.filter(username=request.POST['login']):
                context['incorrect_username'] = True
                no_error_context = False

            if not is_email(request.POST['email']) or \
                    User.objects.filter(email=request.POST['email']):
                context['incorrect_email'] = True
                no_error_context = False

            if request.POST['password'] != request.POST['password_double']:
                context['not_match_passwords'] = True
                no_error_context = False

        if no_error_context:
            # Adding user.
            user = User.objects.create_user(request.POST['login'],
                                            request.POST['email'],
                                            request.POST['password'],
                                            first_name=
                                            request.POST['first_name'],
                                            last_name=
                                            request.POST['last_name'])

            user_settings = AlgorithmSettings(user=user,
                                              question=
                                              request.POST['question'],
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
    context = {}
    # Process sending email
    if request.method == 'POST' and 'email_button' in request.POST:
        necessary_fields = ('email', )
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)
        if no_error_context:
            users = User.objects.filter(email=request.POST['email'])
            if len(users) != 1:
                context['incorrect_email'] = True
            else:
                request.session['user_email'] = request.POST['email']
                request.session['confirmed'] = False

    if request.method == 'POST' and 'answer_button' in request.POST:
        necessary_fields = ('answer',)
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)
        if no_error_context:
            users = User.objects.filter(email=request.session['user_email'])
            answer = AlgorithmSettings.objects.filter(user=users[0])[0].answer
            if answer != request.POST['answer']:
                context['incorrect_answer'] = True
            else:
                request.session['confirmed'] = True

    if request.method == 'POST' and 'restore_button' in request.POST:
        necessary_fields = ('password', 'password_double')
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)
        if no_error_context:
            if request.POST['password'] != request.POST['password_double']:
                context['not_match_password'] = True
            else:
                users = User.objects.filter(email=
                                            request.session['user_email'])
                user = users[0]
                user.set_password(request.POST['password'])
                user.save()
                return HttpResponseRedirect(reverse('predictor:auth'))

    if 'user_email' in request.session:
        if 'confirmed' not in request.session or\
                not request.session['confirmed']:
            users = User.objects.filter(email=
                                        request.session['may_be_user_email'])
            question = AlgorithmSettings.objects.filter(user=
                                                        users[0])[0].question
            context['secret_question'] = question
        else:
            context['confirmed'] = True
        context['email'] = request.session['user_email']

    return render(request, 'predictor/restore.html', context)


@login_required(login_url='/auth')
def research_page(request):
    """
    View for researcher page.

    :param request:
    Http request.

    :return:
    Researcher page.
    """
    context = {}
    # Checking user rights for showing research page.
    if not request.user.groups.filter(name='researcher').exists():
        return HttpResponseRedirect(reverse('predictor:index'))

    # Processing user uploading files for calculating prediction.
    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:research'))

    form_fields = ('algorithm_name', 'algorithm_package', 'algorithm_settings',
                   'parser_proportion', 'parser_rows')
    settings = get_object_or_404(AlgorithmSettings, user=request.user)
    # todo move to extra function
    context['algorithm_name'] = settings.algorithm_name
    context['algorithm_package'] = settings.algorithm_package
    context['algorithm_settings'] = settings.algorithm_settings
    context['parser_proportion'] = settings.parser_proportion
    context['parser_rows'] = settings.parser_rows

    if request.method == 'POST' and 'submit' in request.POST:
        for field in form_fields:
            if field in request.POST:
                request.session[field] = request.POST[field]
        necessary_fields = ('algorithm_name', 'algorithm_package',
                            'parser_proportion', 'parser_rows')
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)
        if no_error_context:
            try:
                settings.algorithm_settings = \
                    json.loads(request.POST['algorithm_settings'])
            except Exception:
                context['incorrect_algorithm_settings'] = True
                no_error_context = False
            try:
                settings.parser_proportion = \
                    float(request.POST['parser_proportion'])
                if settings.parser_proportion <= 0 or\
                        settings.parser_proportion >= 1:
                    raise ValueError
            except Exception:
                context['incorrect_proportion'] = True
                no_error_context = False
            try:
                if len(request.POST['parser_rows']) == 0:
                    settings.parser_rows = None
                else:
                    settings.parser_proportion = \
                        int(request.POST['parser_rows'])
            except Exception:
                context['incorrect_parser_rows'] = True
                no_error_context = False

        if no_error_context:
            settings.algorithm_name = request.POST['algorithm_name']
            settings.algorithm_package = request.POST['algorithm_package']
            if 'parser_raw_date' in request.POST:
                settings.parser_raw_date = True
            else:
                settings.parser_raw_date = False
            settings.save()

    for field in form_fields:
        if field in request.session:
            context[field] = request.session[field]

    return render(request, 'predictor/research.html', context)
