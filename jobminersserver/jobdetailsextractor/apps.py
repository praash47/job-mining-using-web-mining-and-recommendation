"""
Contains configuration for jobdetailsextractor django app. Also, starts our backend server when the jobdetailsextractor django app is ready.
"""
import threading

from django.apps import AppConfig


class JobdetailsextractorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobdetailsextractor"

    def ready(self):
        """
        When the jobdetailsextractor is ready, this function starts creates a timer object and
        starts it in a new thread.
        """
        from timers.mainloop import Timer

        timer = Timer()

        from backend.misc import log

        log("main", "info", "Starting the backend (timer module) in a seperate thread")
        thread = threading.Thread(target=timer.run)
        thread.start()
