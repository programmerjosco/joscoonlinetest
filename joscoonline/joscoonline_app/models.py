from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    branchid = models.IntegerField(blank=True, null=True, verbose_name="Branch ID")

    def __str__(self):
        return self.username