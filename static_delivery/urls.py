from django.urls import path

from . import views


app_name = 'static'

urlpatterns = [
    path('<path:path>', views.get_file),
]