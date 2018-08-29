from predictor.views_utils import *
import json
from logging import getLogger
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
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
    if check_if_user_is_researcher(request.user):
        context['research_rights'] = True

    # Processing user logout.
    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return HttpResponseRedirect(reverse('predictor:index'))

    # Processing user uploading files for calculating prediction.
    if request.method == 'POST' and 'code' in request.POST:
        # Check necessary files.
        index_calculate_prediction(request, context)

    # Processing sending prediction files to user.
    if request.method == 'GET' and 'download' in request.GET:
        response = index_create_http_with_prediction_result(request)
        if response is not None:
            return response

    # Processing showing prediction result to user.
    index_fill_context(request, context)

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
        return next_redirection(request)

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

    register_fill_context(request, context, form_fields)

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
    if request.method == 'POST' and 'answer_button' in request.POST:
        restore_check_answer(request, context)

    # Process changing email.
    if request.method == 'POST' and 'restore_button' in request.POST and \
            restore_change_password(request, context):
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

    # Set new params and make new model.
    if request.method == 'POST' and 'submit' in request.POST:
        process_researcher(request, context, form_fields)

    research_fill_context(request, context, form_fields)

    logger.info(context)
    return render(request, 'predictor/research.html', context)
