from django.db import models
from django.contrib.auth.models import User

class JobSeeker(models.Model):
    """
    A person who seeks jobs and has skills. S/he is a user and has a skill set.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skill_set = models.TextField(null=True)

    def __str__(self) -> str:
        return str(self.user)