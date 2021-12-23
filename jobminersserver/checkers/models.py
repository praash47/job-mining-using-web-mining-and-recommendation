from django.db import models

class JobWebsiteURL(models.Model):
    """
    PostGreSQL table for Job Website
    """
    url = models.CharField(max_length=500)
    search_url = models.CharField(max_length=500)
    visited = models.BooleanField()
    job_title_xpath = models.CharField(max_length=500)

    def __str__(self) -> str:
        return str(self.url)

