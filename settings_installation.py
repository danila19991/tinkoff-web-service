from mlalgorithms.shell import Shell
import os
import shutil


# Delete migrations.
if os.path.exists('predictor\migrations'):
    print('remove migrations: predictor')
    shutil.rmtree('predictor\migrations')

# Delete db.
if os.path.isfile('db.sqlite3'):
    print('remove db: db.sqlite3')
    os.remove('db.sqlite3')

# Make migrations.
os.system('python manage.py makemigrations predictor')
os.system('python manage.py migrate')

sh = Shell()
sh.train('train.csv')
sh.save_model('forest_model')
