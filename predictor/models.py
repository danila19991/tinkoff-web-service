from django.db import models
from django.contrib.auth.models import User


# Algorithm and other settings for user.
class AlgorithmSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=128, default='ExtraTreesModel')
    metrics = models.CharField(max_length=128, default='MeanF1Score')
    parser = models.CharField(max_length=128, default='CommonParser')
    question = models.CharField(max_length=128)
    answer = models.CharField(max_length=128)
    with_debug = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

