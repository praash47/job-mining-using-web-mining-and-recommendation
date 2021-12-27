import datetime
from checkers.checkjobwebsite import CheckJobWebsite
from checkers.models import JobWebsite

from jobdetailsextractor.models import Job
import os
from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from interactor.searcher import Search

def check_deadline_existing_job():
    # for job in Job.objects.all():
    #     if job.deadline < datetime.datetime.now():
    #         job.delete()
    pass

def check_for_new_job_url():
    rg = RequestGoogle()
    urls = rg.get_100_urls()

    checker = CheckJobWebsite(urls=urls)
    job_websites = checker.check_urls()

    searcher = Search()
    for job_website in job_websites:
        job_website_obj = JobWebsite.objects.get(url=job_website)
        
        search_url = searcher.get_search_url(job_website)
        
        job_website_obj.search_url = search_url
        job_website_obj.save()
    
    # for job_website in JobWebsite.objects.all():
    #     # Placement of spider on website whose search URL is passed.
    #     os.system(f'curl http://localhost:6800/schedule.json \
    #         -d project=scraper -d spider=CrawlSite -d \
    #         search_page_url="{job_website.search_url}"')
    