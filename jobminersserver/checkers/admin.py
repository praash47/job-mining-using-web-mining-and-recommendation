from django.contrib import admin
from .models import JobWebsiteURL, JobURL

# Register your models here.
admin.site.register(JobURL)
admin.site.register(JobWebsiteURL)