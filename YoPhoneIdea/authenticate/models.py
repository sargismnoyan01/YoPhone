from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator



class CustomUser(AbstractUser):
    coins = models.DecimalField('Coins',max_digits=10,decimal_places=2,default=0.00)
    password = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField("email address",unique=True)







