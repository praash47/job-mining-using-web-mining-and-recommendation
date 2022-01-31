"""
This file contains the main tasks of the backend server.

There are three main functions here:
1. check_deadline_existing_job()
2. check_for_new_job_website_urls()
"""
import logging

from django.utils import timezone

from interactor.titleextractor import TitleExtractor

from checkers.models import JobWebsite
from jobdetailsextractor.models import Job


mainlogger = logging.getLogger('main')


def check_deadline_existing_job():
    """
    Checks for deadline in existing job websites. Deletes the 
    job website from database upon expired deadline.
    """
    for job in Job.objects.all():
        if job.deadline:
            if job.deadline < timezone.now():
                job.delete()


def check_for_new_job_website_urls():
    """
    This function checks for job URLs in new job websites as well as in
    new job URLs in existing job websites.
    """
    # Get 100 URLs from Google
    from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
    rg = RequestGoogle()
    urls = rg.get_100_urls()

    # Check for the job websites
    from checkers.checkjobwebsite import CheckJobWebsite
    checker = CheckJobWebsite(urls=urls)
    job_websites = checker.check_urls()

    # Create a searcher object
    from interactor.searcher import Search
    searcher = Search()
    for job_website in job_websites:
        job_website_obj = JobWebsite.objects.get(url=job_website)
        search_url, title_xpath = "", ""
        titleextractor = None

        try:
            # Run searcher and obtain search URL.
            search_url = searcher.get_search_url(job_website)

            # Find job title in the search page and it's xpath.
            titleextractor = TitleExtractor(search_url)
            title_xpath = titleextractor.extract_title_xpath()

            # Extract further jobs from the extracted title xpath.
            titleextractor.extract_jobs_from_title_xpath(title_xpath)

        except Exception as e:
            mainlogger.error(e)

        finally:
            # save
            job_website_obj.search_url = search_url
            job_website_obj.job_title_xpath = title_xpath
            job_website_obj.save()
            if titleextractor:
                titleextractor.store_into_database()

    # check_new_job_urls_in_existing_websites(job_websites)


def check_new_job_urls_in_existing_websites(job_websites):
    """
    Checks for new job URLs in existing job websites.

    Parameters
    ----------
    job_websites: list of new job website URLs
        new job websites obtained in this iteration.
    """
    mainlogger.info('Checking for new Job URLs in existing job websites.')
    for job_website in JobWebsite.objects.all():
        # If this is not new job website
        if not job_website.url in job_websites:
            try:
                titleextractor = TitleExtractor(job_website.search_url)
                titleextractor.extract_jobs_from_title_xpath(
                    job_website.job_title_xpath
                )
                titleextractor.store_into_database()

            except Exception as e:
                mainlogger.error(e)
