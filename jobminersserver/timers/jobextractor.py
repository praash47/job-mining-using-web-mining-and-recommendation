"""
This submodule handles the extraction of all job details
"""
import datetime
import time

from django_eventstream import send_event

from jobdetailsextractor.models import Job
from jobdetailsextractor.main import JobDetails


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

    # Cycle through the job websites so that no server gets request often.
    from itertools import cycle
    for job_website in cycle(job_websites):
        for job in pending_jobs:
            if job.website == job_website:
                send_event('backend_daemon', 'message', {
                    'currentMessage': f'Extracting For {job.website.name}: Job: {job.title}',
                    'messagePriority': 'info'
                })

                job_start_time = datetime.datetime.now()

                # Get job details
                job_details = JobDetails(job.url, job.title)
                job_details.fetch()
                job_details.get_details()
                job_details.store_into_database()
                # Update pending jobs
                pending_jobs = Job.objects.filter(extracted=False)
                if not pending_jobs:
                    break

                job_end_time = datetime.datetime.now()

                wait(job_start_time, job_end_time)


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
    config = read_config('timers/timersettings.ini')
    server_wait_time = datetime.timedelta(
        minutes=float(config.get('times', 'server_wait_time')))

    time_elapsed = job_end_time - job_start_time
    if time_elapsed < server_wait_time:
        time_to_sleep = server_wait_time - time_elapsed
        time.sleep(time_to_sleep.total_seconds())
