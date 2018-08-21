from django.db import models
from django.contrib.auth.models import User


class AlgorithmSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=128, default='ExtraTreesModel')
    metrics = models.CharField(max_length=128, default='MeanF1Score')
    parser = models.CharField(max_length=128, default='CommonParser')
    with_debug = models.BooleanField()

