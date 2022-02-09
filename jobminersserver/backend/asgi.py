"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting. Specifies the channels used
for the SSE for backend daemon and logging.
"""
import os

from django.core.asgi import get_asgi_application
from django.conf.urls import url
from django_eventstream.routing import urlpatterns

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = ProtocolTypeRouter(
    {
        "http": URLRouter(
            [
                url(
                    r"^events/(?P<channel>\w+)/",
                    AuthMiddlewareStack(URLRouter(urlpatterns)),  # our sse endpoint
                ),
                url(r"", get_asgi_application()),
            ]
        ),
    }
)
