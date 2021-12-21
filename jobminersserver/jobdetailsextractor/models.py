from django.db import models
from checkers.models import JobWebsiteURL

# Create your models here.
class Job(models.Model):
    """
    PostGreSQL table for Job URL
    """
    # CATEGORIES = ['IT', 'NonIT']
    # category = models.CharField(max_length=5,choices=CATEGORIES)
    website = models.ForeignKey(JobWebsiteURL, on_delete=models.CASCADE)
    title = models.TextField()
    url = models.CharField(max_length=500)
    deadline = models.DateTimeField(auto_now=False, auto_now_add=False)
    job_skills = models.TextField()
    company_name = models.TextField()
    company_info = models.TextField()
    company_email = models.EmailField(max_length=254)
    company_location = models.TextField()
    job_description = models.TextField()
    salary = models.IntegerField()
    no_vacancy = models.IntegerField()
    level = models.TextField()
    qualification = models.CharField(max_length=150)
    experience = models.CharField(max_length=500)
    misc_field = models.TextField()

    def __str__(self) -> str:
        return str(self.title)

class JobWebsiteStrucutre(models.Model):
    """
    PostgreSQL table for xpath structure for job websites
    """
    url = models.CharField(max_length=500)
    name_xpath = models.CharField(max_length=1000)
    deadline_xpath = models.DateTimeField()
    c_name_xpath = models.CharField(max_length=1000)
    c_information_xpath = models.CharField(max_length=1000)
    email_xpath = models.CharField(max_length=1000)
    location_xpath = models.CharField(max_length=1000)
    job_description_xpath = models.CharField(max_length=1000)
    salary_xpath = models.CharField(max_length=1000)
    no_vacancy_xpath = models.CharField(max_length=1000)
    level_xpath = models.CharField(max_length=1000)
    qualification_xpath = models.CharField(max_length=1000)
    experience_xpath = models.CharField(max_length=1000)
    
    def __str__(self) -> str:
        return str(self.title)
