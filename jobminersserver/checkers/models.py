from django.db import models

class JobWebsite(models.Model):
    """
    PostGreSQL table for Job Website
    """
    name = models.CharField(max_length=100, null=True)
    url = models.CharField(max_length=500)
    search_url = models.CharField(max_length=500, null=True)
    visited = models.BooleanField(default=False)
    job_title_xpath = models.CharField(max_length=500, null=True)

    def __str__(self) -> str:
        return str(self.name)
