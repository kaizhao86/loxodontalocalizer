from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
  url(r'^$', views.index, name='index'), 
  url(r'^aligning/$', views.aligning, name='aligning'),
  url(r'^getCsv/', views.getCsv, name='getCsv'),
  url(r'^editElephant/(?P<elephantID>[0-9]+)/$', views.editElephant, name='editElephant'),
  url(r'^createElephant/', views.createElephant, name='createElephant'),
  url(r'^editElephantJson/$', views.editElephantJson, name='editElephantJson'),
  url(r'^fromGoogleSpreadsheets/$', views.fromGoogleSpreadsheets, name='fromGoogleSpreadsheets'),
  url(r'^editLocation/(?P<locationID>[0-9]+)/$', views.editLocation, name='editLocation'),
  url(r'^createLocation/', views.createLocation, name='createLocation'),
  url(r'^editLocationJson/$', views.editLocationJson, name='editLocationJson'),
  url(r'^createHaplotype/$', views.createHaplotype, name='createHaplotype'),
  url(r'^createHaplotypeJson/$', views.createHaplotypeJson, name='createHaplotypeJson'),
  url(r'^admin/$', views.admin, name='admin'),
  url(r'^migrate/$', views.migrateData, name='migrate'),
]