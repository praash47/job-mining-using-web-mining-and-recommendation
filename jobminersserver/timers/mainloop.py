from jobdetailsextractor.models import Job
from .jobextractor import extract_jobs
import schedule
from backend import check_for_new_job_url, check_deadline_existing_job
import time

class Timer():
    def __init__(self):
        pass
    
    def run(self):
        schedule.every().day.at('13:07').do(check_deadline_existing_job)
        schedule.every().day.at('13:07').do(check_for_new_job_url)
        self.check_pending_job_urls()

        while True:
            schedule.run_pending()
            time.sleep(1)

    def check_pending_job_urls(self):
        pending_jobs = Job.objects.filter()
        if pending_jobs: extract_jobs(pending_jobs)