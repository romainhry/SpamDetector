from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^kmeans/', views.kmeans, name='kmeans'),
    url(r'^extraction/', views.extraction, name='extraction'),
    url(r'^reinit/', views.reinit, name='reinit'),

]