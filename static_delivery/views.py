from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse, FileResponse
import os, re

prog = re.compile(r"^(img|css)/[-0-9\w]+.(png|css)")


def get_file(request, path=''):
    if prog.match(path) and os.path.isfile('static/' + path):
        return FileResponse(open('static/' + path, 'rb'))
    return HttpResponseNotFound
