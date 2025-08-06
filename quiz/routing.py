# quiz/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/lobby/<str:session_code>/', consumers.LobbyConsumer.as_asgi()),
    path('ws/game/<str:session_code>/<str:player_name>/', consumers.GameConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]