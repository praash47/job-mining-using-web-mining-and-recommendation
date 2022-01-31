"""
This file is responsible for looping through the main operations every day. This is the main entrypoint for the backend section and signifies the general flow of program seperate from Django.
"""
import logging
import schedule
import time

from .jobextractor import extract_jobs

from backend.main import check_for_new_job_website_urls, check_deadline_existing_job

mainlogger = logging.getLogger('main')


class Timer():
    """
    Schedules the checking for deadline in existing job and checking for new job website and new job URLs in existing websites. Finally, finds the pending jobs and runs extract_jobs() for extracting parameters from the jobs in timely manner.


    Methods
    -------
    run()
        Runs the backend part of the program. * Use this function inside a threading Thread.    
    """
    def __init__(self):
        pass

    def run(self):
        """
        Schedules the main operations in program at 12.00 am and performs it exactly once.
        """
        schedule.every().day.at('00:00').do(check_deadline_existing_job)
        schedule.every().day.at('00:00').do(check_for_new_job_website_urls)
        schedule.every().day.at('00:00').do(self.check_pending_job_urls)

        # for the first bootup.
        check_deadline_existing_job()
        check_for_new_job_website_urls()
        self.check_pending_job_urls()

        while True:
            schedule.run_pending()
            time.sleep(1)

    def check_pending_job_urls(self):
        """
        Finds pending job URLs and runs the extract_job() to extract jobs from it in a timely manner.
        """
        from jobdetailsextractor.models import Job

        pending_jobs = Job.objects.filter(extracted=False)
        if pending_jobs:
            extract_jobs(pending_jobs)
