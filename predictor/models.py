from django.db import models
from django.contrib.auth.models import User


# todo clean files after removing
# Algorithm and other settings for user.
class AlgorithmSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    algorithm_name = models.CharField(max_length=32,
                                      default='LinearRegression')
    algorithm_package = models.CharField(max_length=32,
                                         default='linear_model')

    default_string = '''{
        "fit_intercept": true,
        "normalize": false,
        "copy_X": true,
        "n_jobs": 1
    }'''
    algorithm_settings = models.CharField(max_length=2048,
                                          default=default_string)
    # todo move files to dir models
    model_file = models.FileField(upload_to='models/')
    parser_rows = models.IntegerField(null=True)
    parser_proportion = models.FloatField(default=0.7)
    parser_raw_date = models.BooleanField(default=True)
    question = models.CharField(max_length=128)
    answer = models.CharField(max_length=128)
    with_debug = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

