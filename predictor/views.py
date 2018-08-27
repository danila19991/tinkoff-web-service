from predictor.views_utils import *
import json
from logging import getLogger
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

logger = getLogger('django.template')


@login_required(login_url='/auth')
def index(request):
    """
    View for main page.

    :param request: HttpRequest
        Http request.

    :return: instance of HttpResponse
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
        alg_settings = AlgorithmSettings.objects.get(user=request.user)
        if no_error_context:
            try:
                response = HttpResponse()
                make_prediction(request.FILES['input_data'],
                                request.FILES['input_menu'], response,
                                alg_settings.model_file)
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
    logger.info(context)
    return render(request, 'predictor/index.html', context)


@decor_signed_in_to_next
def auth(request):
    """
    View for authorisation page.

    :param request: HttpRequest
        Http request.

    :return: instance of HttpResponse
        Authorisation page or redirection to next page.
    """
    request.session.flush()

    context = {}

    if request.method == 'POST' and 'submit' in request.POST and \
       authorise_user(request, context):
        if 'next' in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        elif 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])
        else:
            return HttpResponseRedirect(reverse('predictor:index'))
    logger.info(context)
    return render(request, 'predictor/auth.html', context)


@decor_signed_in_to_next
def register_page(request):
    """
    View for registration page. And added registered users.

    :param request: HttpRequest
        Http request.

    :return: instance of HttpResponse
        Registration page or redirection to authorisation page.
    """
    context = {}
    form_fields = ('first_name', 'last_name', 'email', 'login', 'question',
                   'answer')
    if request.method == 'POST' and register_user(request, context,
                                                  form_fields):
        return HttpResponseRedirect(reverse('predictor:auth'))

    fill_context(request, context, form_fields)

    logger.info(context)
    return render(request, 'predictor/register.html', context)


@decor_signed_in_to_next
def restore(request):
    """
    View for restore password page.

    :param request: HttpRequest
        Http request.

    :return: instance of HttpResponse
        Restore password page or redirection to authorisation page.
    """
    context = {}
    # Process sending email
    if request.method == 'POST' and 'email_button' in request.POST:
        restore_search_email(request, context)

    # Process checking secret answer.
    if 'user_email' in request.session and request.method == 'POST' and\
            'answer_button' in request.POST:
        restore_check_answer(request, context)

    # Process changing email.
    if 'confirmed' in request.session and request.session['confirmed'] and\
            request.method == 'POST' and 'restore_button' in request.POST:
        if restore_change_password(request, context):
            return HttpResponseRedirect(reverse('predictor:auth'))

    research_fill_data(request, context)

    logger.info(context)
    return render(request, 'predictor/restore.html', context)


@login_required(login_url='/auth')
def research_page(request):
    """
    View for researcher page.

    :param request: HttpRequest
        Http request.

    :return: instance of HttpResponse
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
                   'parser_proportion', 'parser_rows', 'parser_raw_date',
                   'debug_info')
    alg_settings = get_object_or_404(AlgorithmSettings, user=request.user)
    context['algorithm_name'] = alg_settings.algorithm_name
    context['algorithm_package'] = alg_settings.algorithm_package
    context['algorithm_settings'] = alg_settings.algorithm_settings
    context['parser_proportion'] = alg_settings.parser_proportion
    context['parser_rows'] = alg_settings.parser_rows
    context['parser_raw_date'] = alg_settings.parser_raw_date
    context['debug_info'] = alg_settings.with_debug
    context['result_description'] = alg_settings.model_results
    if context['parser_rows'] is None:
        context['parser_rows'] = ''
    # Set new params and make new model.
    if request.method == 'POST' and 'submit' in request.POST:
        for field in form_fields:
            if field in request.POST:
                request.session[field] = request.POST[field]
        necessary_fields = ('algorithm_name', 'algorithm_package',
                            'parser_proportion')
        no_error_context = check_content(necessary_fields, request.POST,
                                         context)
        # Check special fields.
        if no_error_context:
            try:
                tmp = json.loads(request.POST['algorithm_settings'])
                alg_settings.algorithm_settings = \
                    request.POST['algorithm_settings']
            except Exception:
                context['incorrect_algorithm_settings'] = True
                no_error_context = False
            try:
                alg_settings.parser_proportion = \
                    float(request.POST['parser_proportion'])
                if alg_settings.parser_proportion <= 0 or \
                        alg_settings.parser_proportion >= 1:
                    raise ValueError
            except Exception:
                context['incorrect_proportion'] = True
                no_error_context = False
            try:
                if len(request.POST['parser_rows']) == 0:
                    alg_settings.parser_rows = None
                else:
                    alg_settings.parser_rows = \
                        int(request.POST['parser_rows'])
            except Exception:
                context['incorrect_parser_rows'] = True
                no_error_context = False
        if no_error_context:
            alg_settings.algorithm_name = request.POST['algorithm_name']
            alg_settings.algorithm_package = request.POST['algorithm_package']
            if 'parser_raw_date' in request.POST:
                alg_settings.parser_raw_date = True
            else:
                alg_settings.parser_raw_date = False
            if 'debug_info' in request.POST:
                alg_settings.with_debug = True
            else:
                alg_settings.with_debug = False
            alg_settings.save()

            if 'train_data' in request.FILES:
                try:
                    request.session['result_description'] = \
                        make_train(request.FILES['train_data'], alg_settings)
                    alg_settings.model_results = \
                        request.session['result_description']
                    alg_settings.save()
                except Exception:
                    request.session['result_description'] = 'Train failed.'

    for field in form_fields:
        if field in request.session:
            context[field] = request.session[field]
    if 'result_description' in request.session and \
            len(request.session['result_description']):
        context['result_description'] = request.session['result_description']
    logger.info(context)
    return render(request, 'predictor/research.html', context)
