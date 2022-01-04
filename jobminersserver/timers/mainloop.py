from checkers.models import JobWebsite
from jobdetailsextractor.models import Job
from .jobextractor import extract_jobs
import schedule
from backend.main import check_for_new_job_website_urls, check_deadline_existing_job
from django_eventstream import send_event
from jobdetailsextractor.main import JobDetails

import random
from itertools import cycle
import time
import logging
mainlogger = logging.getLogger('main')

class Timer():
    def __init__(self):
        pass

    def run(self):
        # priorities = ['info', 'error', 'scraping']
        # message = 'Asim '
        # max_messages = 200
        # i = 1
        # for priority in cycle(priorities):
        #     if i > max_messages: break
        #     send_event('backend_daemon', 'message', {
        #         'currentMessage': message + str(i) + ' ' + priority,
        #         'messagePriority': priority
        #     })
        #     time.sleep(random.randint(1, 4))
        #     i += 1
        # schedule.every().day.at('00:00').do(check_deadline_existing_job)
        # schedule.every().day.at('00:00').do(check_for_new_job_website_urls)
        # schedule.every().day.at('00:00').do(self.check_pending_job_urls)

        # for the first bootup.
        # check_deadline_existing_job()
        # check_for_new_job_website_urls()
        self.check_pending_job_urls()

        while True:
            schedule.run_pending()
            time.sleep(1)

    def check_pending_job_urls(self):
        with open('/home/aasis/Documents/jobminersserver/timers/sample.txt') as textfile:
            for line in textfile.readlines():
                job_website, job_url, job_title = line.split(',')
                job_website = JobWebsite.objects.get(url=job_website)
                Job.objects.get_or_create(website=job_website, url=job_url, title=job_title)[0].save()
        pending_jobs = Job.objects.filter(extracted=False)
        if pending_jobs: extract_jobs(pending_jobs)