from django.db import models

# Create your models here.


class Account(models.Model):
    user=models.CharField(max_length=64,primary_key=True)
    password=models.CharField(max_length=64)

