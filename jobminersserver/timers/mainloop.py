from jobdetailsextractor.models import Job
from .jobextractor import extract_jobs
import schedule
from backend.main import check_for_new_job_website_urls, check_deadline_existing_job
from django_eventstream import send_event

import time
import logging
mainlogger = logging.getLogger('main')

class Timer():
    def __init__(self):
        pass

    def run(self):
        send_event('test', 'message', 'Asim')
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
        pending_jobs = Job.objects.filter(extracted=False)
        if pending_jobs: extract_jobs(pending_jobs)