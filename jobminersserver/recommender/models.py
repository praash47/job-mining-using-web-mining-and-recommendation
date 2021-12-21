from django.db import models
from django.contrib.auth.models import User

class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skill_set = models.TextField()

    def __str__(self) -> str:
        return str(self.url)

