from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache

class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skill_set = models.TextField(null=True)

    def __str__(self) -> str:
        return str(self.user)