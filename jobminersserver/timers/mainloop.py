from jobdetailsextractor.models import Job
from .jobextractor import extract_jobs
import schedule
from backend.main import check_for_new_job_url, check_deadline_existing_job
from jobdetailsextractor.main import JobDetails

class Timer():
    def __init__(self):
        pass
    
    def run(self):
        # schedule.every().day.at('00:00').do(check_deadline_existing_job)
        # schedule.every().day.at('00:00').do(check_for_new_job_url)
        # self.check_pending_job_urls()

        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)
        jobs = Job.objects.all()
        job_details = JobDetails(jobs[0].url, jobs[0].title)
        job_details.fetch()
        job_details.get_details()

    def check_pending_job_urls(self):
        pass
        # pending_jobs = Job.objects.filter()
        # if pending_jobs: extract_jobs(pending_jobs)