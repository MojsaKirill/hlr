# coding: utf-8

try:
    from django.conf.urls.defaults import url
except ImportError:
    from django.conf.urls import url

from . import views as v


urlpatterns = [
    url(r'^result/$', v.receive_result, name='robokassa_result'),
    url(r'^success/$', v.success, name='robokassa_success'),
    url(r'^fail/$', v.fail, name='robokassa_fail'),
]
