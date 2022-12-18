"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
from django_private_chat2 import urls
#application = get_asgi_application()

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
import chat.routing
django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app, # or => get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns))
    ),
    "websocket": AuthMiddlewareStack(
        URLRouter(urls.websocket_urlpatterns)
    ),
})