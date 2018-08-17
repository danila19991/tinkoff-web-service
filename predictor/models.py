from django.db import models


#todo move cashed files to super dir
class Result(models.Model):
    prediction = models.FileField(upload_to='prediction/')
    menu = models.FileField(upload_to='menu/')
    people = models.FileField(upload_to='people/')
    key_hash = models.TextField(primary_key=True)
    generation_time = models.DateTimeField(blank=True, null=True)
