
  
import datetime
from configparser import ConfigParser
from checkers.models import JobWebsite
import time
from itertools import cycle
from django_eventstream import send_event

from jobdetailsextractor.models import Job
from jobdetailsextractor.main import JobDetails

def extract_jobs(pending_jobs):
    # for parameter options
    CONFIG = "C:/Users/Lenovo/job-mining-using-web-mining-and-recommendation/jobminersserver/timers/timersettings.ini"
    parser = ConfigParser()
    parser.read(CONFIG)
    server_wait_time = datetime.timedelta(minutes=float(parser.get('times', 'server_wait_time')))
    job_websites = JobWebsite.objects.all()

    for job_website in cycle(job_websites):
        for job in pending_jobs:
            if job.website == job_website:
                send_event('backend_daemon', 'message', {
                    'currentMessage': f'Extracting For {job.website.name}: Job: {job.title}',
                    'messagePriority': 'info'
                })
                job_start_time = datetime.datetime.now()
                job_details = JobDetails(job.url, job.title)
                print(job.url, job.title, pending_jobs)
                job_details.fetch()
                job_details.get_details()
                job_details.store_into_database()
                pending_jobs = Job.objects.filter(extracted=False)

                job_end_time = datetime.datetime.now()

                time_elapsed = job_end_time - job_start_time
                if time_elapsed < server_wait_time: 
                    time_to_sleep = server_wait_time - time_elapsed
                    print(time_to_sleep)
                    time.sleep(time_to_sleep.total_seconds())
                break
        if not pending_jobs: break