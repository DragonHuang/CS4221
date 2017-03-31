from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload', views.upload_file, name='upload_file'),
    url(r'^confirm', views.confirm, name='index'),
    url(r'^finish', views.finish, name='index'),
    url(r'^todo', views.todo, name='index'),
    url(r'^$', views.index, name='index'),
]