import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from notifications.routing import websocket_urlpatterns  # importa as rotas de WS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # requisições HTTP normais
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # rotas do WebSocket
        )
    ),
})
