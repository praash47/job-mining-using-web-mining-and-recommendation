import datetime
from checkers.models import JobWebsite
from jobdetailsextractor.models import Job
import os

def check_deadline_existing_job():
    for job in Job.objects.all():
        if job.deadline < datetime.datetime.now():
            job.delete()

def check_for_new_job_url():
    for job_website in JobWebsite.objects.all():
        # Placement of spider on website whose search URL is passed.
        os.system(f'curl http://localhost:6800/schedule.json \
            -d project=scraper -d spider=CrawlSite -d \
            search_page_url="{job_website.search_url}"')