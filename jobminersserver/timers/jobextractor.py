"""
This submodule handles the extraction of all job details

Functions
---------
extract_jobs(): timely extract jobs in pending_jobs in the time mentioned in timersettings.ini
"""
import datetime
import spacy
import time

from django_eventstream import send_event

from backend.misc import log
from jobdetailsextractor.main import JobDetails

from jobdetailsextractor.models import Job


def extract_jobs(pending_jobs):
    """
    Extracts job parameters from the pending jobs in a cyclic fashion. Cyclic fashion means each job website gets once per cycle for it's single job extraction.

    Parameters
    ----------
    pending_jobs: QuerySet
        Django QuerySet containing the iterable of pending jobs (extracted=False).
    """
    from checkers.models import JobWebsite

    job_websites = JobWebsite.objects.all()

    log("main", "info", "Reading 183,000+ company names.")
    company_names = []
    # titles_combined.txt: 70,000 titles to match xpaths from.
    with open("jobdetailsextractor/reqs/company_names.txt") as company_names:
        company_names = [
            company_name.strip("\n") for company_name in company_names.readlines()
        ]

    # Cycle through the job websites so that no server gets request often.
    from itertools import cycle

    for job_website in cycle(job_websites):
        job = pending_jobs.filter(website=job_website).first()
        if not job:
            continue

        from tagprocessor.misc import clean_text

        send_event(
            "backend_daemon",
            "message",
            {
                "currentMessage": f"Extracting For {job.website.name}: Job: {clean_text(job.title)}",
                "messagePriority": "info",
            },
        )

        extraction_start_time = datetime.datetime.now()

        # Get job details
        job_details = JobDetails(job)
        job_details.fetch()
        job_details.get_details(company_names)
        job_details.store_into_database()
        del job_details  # free up memory

        # Update pending jobs
        pending_jobs = Job.objects.filter(extracted=False)
        if not pending_jobs:
            break

        extraction_end_time = datetime.datetime.now()

        wait(extraction_start_time, extraction_end_time)


def wait(job_start_time, job_end_time):
    """
    Sleeps for the time frame mentioned in server wait time excluding the job execution time.

    Parameters
    ----------
    job_start_time: datetime
        datetime object of the job starting time
    job_end_time: datetime
        datetime object of the job ending time
    """
    from backend.misc import read_config

    config = read_config("timers/timersettings.ini")
    server_wait_time = float(config.get("times", "server_wait_time"))

    time_elapsed = job_end_time - job_start_time
    time_elapsed = time_elapsed.total_seconds() / 60  # Conversion into minutes
    log("main", "info", f"Scraping the job took: {time_elapsed} minutes")
    if time_elapsed < server_wait_time:
        time_to_sleep = server_wait_time - time_elapsed
        log("main", "info", f"Waiting for {time_to_sleep} minutes")
        time.sleep(time_to_sleep * 60)
