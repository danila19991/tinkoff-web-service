from mlalgorithms.shell import Shell
import os
import shutil


# Delete migrations.
if os.path.exists('predictor\migrations'):
    print('remove migrations: predictor')
    shutil.rmtree('predictor\migrations')

# Delete models.
if os.path.exists('models'):
    print('remove models')
    shutil.rmtree('models')

# Delete db.
if os.path.isfile('db.sqlite3'):
    print('remove db: db.sqlite3')
    os.remove('db.sqlite3')

# Make migrations.
os.system('python manage.py makemigrations predictor')
os.system('python manage.py migrate')

# Add models dir
if not os.path.exists('models'):
    print('add models storage')
    os.mkdir('models')


sh = Shell()
sh.train('train.csv')
sh.save_model('models/default.mdl')
