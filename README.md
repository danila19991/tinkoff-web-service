# tinkoff-web-service
Web-service for Tinkoff Cafe Challenge.

For starting server when data base was created run command:

python manage.py runserver

Before starting server you need to make migrations and optionally create super user. It should be done one time for creating database and administrator profile for redacting it. Learn more: http://robotlab.apmath.spbu.ru/xwiki/bin/view/Python-Dev/2.%20Популярные%20пакеты%20и%20фреймворки/Django/

For making migrations enter commands:

python manage.py makemigrations predictor

python manage.py migrate

For adding super user enter command:

python manage.py createsuperuser