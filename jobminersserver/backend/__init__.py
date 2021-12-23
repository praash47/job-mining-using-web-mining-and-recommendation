"""
The django's server configurations for the server. It handles websocket connections and
manages the server and is responsible for handling the general flow of the application.
"""
from .main import check_for_new_job_url, check_deadline_existing_job