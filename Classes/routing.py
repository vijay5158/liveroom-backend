from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/class/(?P<class_name>[0-9A-Z][-\w]+)/$', consumers.ClassConsumer.as_asgi()),
]