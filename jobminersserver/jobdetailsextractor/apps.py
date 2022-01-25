from django.apps import AppConfig
import threading

class JobdetailsextractorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobdetailsextractor'

    # def ready(self):
    #     from timers.mainloop import Timer
    #     timer = Timer()
    #     thread = threading.Thread(target=timer.run)
    #     thread.start()