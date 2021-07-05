import json
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    balance = models.FloatField(default=0)
    sale_price = models.FloatField(default=0)

    def __str__(self):
        return self.email


class Requests(models.Model):
    user_id = models.IntegerField()
    request_date = models.DateTimeField(default=datetime.now())


class Request(models.Model):
    requests_id = models.IntegerField()
    phone = models.IntegerField()
    hlr_status = models.CharField(max_length=100)
    hlr_status_code = models.IntegerField(null=True, blank=True)


class TempRequest(models.Model):
    user_id = models.IntegerField()
    price = models.FloatField()
    phones = models.TextField()
    status = models.BooleanField(default=False)

    def set_phones(self, x):
        self.phones = json.dumps(x)

    def get_phones(self):
        return json.loads(self.phones)


class Price(models.Model):
    default_price = models.FloatField(default=80)

    def __str__(self):
        return str(self.default_price)
