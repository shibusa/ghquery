from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^query', views.query, name='query'),
    url(r'^delete/(?P<query_id>[0-9]+)$', views.delete, name='delete'),
]
