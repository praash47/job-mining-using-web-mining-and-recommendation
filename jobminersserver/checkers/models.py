from django.db import models

class JobWebsiteURL(models.Model):
    url = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.url)

class JobURL(models.Model):
    website = models.ForeignKey(JobWebsiteURL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    url = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.title)