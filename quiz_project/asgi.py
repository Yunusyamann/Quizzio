# quiz_project/asgi.py

import os
from django.core.asgi import get_asgi_application

# Önce Django ortam değişkenini ayarlayın.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_project.settings')

# Django'nun kurulumunu ve uygulama kaydının doldurulmasını sağlamak için
# get_asgi_application() fonksiyonunu erken çağırın.
django_asgi_app = get_asgi_application()

# ARTIK Django hazır olduğuna göre, model ve consumer'ları import eden
# routing dosyamızı güvenle import edebiliriz.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import quiz.routing

application = ProtocolTypeRouter({
    # HTTP istekleri için zaten oluşturduğumuz uygulamayı kullanıyoruz.
    "http": django_asgi_app,

    # WebSocket istekleri için yönlendirmeyi ayarlıyoruz.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            quiz.routing.websocket_urlpatterns
        )
    ),
})