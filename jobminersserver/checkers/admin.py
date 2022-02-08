# Registers the Job Website Table provided by checkers to the admin site.
from django.contrib import admin

from .models import JobWebsite

admin.site.register(JobWebsite)
