from django.db import models
from checkers.models import JobWebsite

# Create your models here.
class Job(models.Model):
    """
    PostGreSQL table for Job URL
    """

    website = models.ForeignKey(JobWebsite, on_delete=models.CASCADE)
    title = models.TextField()
    url = models.CharField(max_length=500)
    deadline = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    job_skills = models.TextField(null=True)
    company_name = models.TextField(null=True)
    company_info = models.TextField(null=True)
    company_email = models.EmailField(max_length=254, null=True)
    location = models.TextField(null=True)
    description = models.TextField(null=True)
    salary = models.CharField(max_length=1000, null=True)
    n_vacancy = models.CharField(max_length=1000, null=True)
    level = models.TextField(null=True)
    qualifications = models.CharField(max_length=150, null=True)
    experiences = models.CharField(max_length=500, null=True)
    misc = models.TextField(null=True)
    extracted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.title)
