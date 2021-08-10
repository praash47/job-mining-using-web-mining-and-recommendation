from django.db import models

class API(models.Model):
    api_key = models.CharField(max_length=50)
    usage_count = models.IntegerField(default=0)
    last_access = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)