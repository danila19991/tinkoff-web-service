import os
import shutil


if os.path.exists('predictor\migrations'):
    print('remove migrations: predictor')
    shutil.rmtree('predictor\migrations')

if os.path.isfile('db.sqlite3'):
    print('remove db: db.sqlite3')
    os.remove('db.sqlite3')

os.system('manage.py makemigrations predictor')
os.system('manage.py migrate')
