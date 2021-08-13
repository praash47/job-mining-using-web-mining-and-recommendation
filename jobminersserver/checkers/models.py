from django.db import models

class JobWebsiteURL(models.Model):
    """
    PostGreSQL table for Job Website
    """
    url = models.CharField(max_length=500)

    def __str__(self) -> str:
        return str(self.url)

class JobURL(models.Model):
    """
    PostGreSQL table for Job URL
    """
    website = models.ForeignKey(JobWebsiteURL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    url = models.CharField(max_length=500)

    def __str__(self) -> str:
        return str(self.title)