import datetime
from checkers.checkjobwebsite import CheckJobWebsite
from checkers.models import JobWebsite

from jobdetailsextractor.models import Job
from interactor.titleextractor import TitleExtractor

from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from interactor.searcher import Search

import logging

mainlogger = logging.getLogger('main')

def check_deadline_existing_job():
    for job in Job.objects.all():
        if job.deadline:
         if job.deadline < datetime.datetime.now():
            job.delete()

def check_for_new_job_website_urls():
    rg = RequestGoogle()
    urls = rg.get_100_urls()

    checker = CheckJobWebsite(urls=urls)
    job_websites = checker.check_urls()

    searcher = Search()
    for job_website in job_websites:
        job_website_obj = JobWebsite.objects.get(url=job_website)
        search_url, title_xpath = "", ""
        titleextractor = None

        try:
            search_url = searcher.get_search_url(job_website)
            
            titleextractor = TitleExtractor(search_url)
            title_xpath = titleextractor.extract_title_xpath()
            titleextractor.extract_jobs_from_title_xpath(title_xpath)
        
        except Exception as e:
            mainlogger.error(e)

        finally:
            job_website_obj.search_url = search_url
            job_website_obj.job_title_xpath = title_xpath
            job_website_obj.save()
            if titleextractor: titleextractor.store_into_database()
            

    check_new_job_urls_in_existing_websites()
    
def check_new_job_urls_in_existing_websites():
    for job_website in JobWebsite.objects.all():
        titleextractor = TitleExtractor(job_website)
        titleextractor.extract_jobs_from_title_xpath(job_website.job_title_xpath)
        
        for job_title, job_url in titleextractor.jobs.items():
            if Job.objects.filter(url=job_url).first():
                titleextractor.jobs.pop(job_title)
        
        titleextractor.store_into_database()