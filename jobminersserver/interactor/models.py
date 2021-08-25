from django.db import models
from checkers.models import JobURL, JobWebsiteURL

# Create your models here.
class Job(models.Model):
    CATEGORIES = [
        ('IT', 'IT'),
        ('Non', 'Non-IT')
    ]

    title = models.CharField(max_length=200)
    website = models.ForeignKey(
        JobWebsiteURL,
        on_delete = models.CASCADE
    )
    url = models.OneToOneField(
        JobURL,
        on_delete = models.CASCADE
    )
    level = models.CharField(max_length=50)
    description = models.TextField()
    salary = models.CharField(max_length=50, default=0)
    qualification = models.TextField()
    skills = models.TextField()
    experience = models.TextField()
    num_vacancy = models.IntegerField(default=1)
    employer = models.CharField(max_length=150)
    employer_description = models.TextField()
    location = models.CharField(max_length=250)
    category = models.CharField(
        max_length=6,
        choices=CATEGORIES,
        default='IT'
    )
    others = models.TextField(null=True)
    deadline = models.DateField()

    def __str__(self):
        return str(self.title)