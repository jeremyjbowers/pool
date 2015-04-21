from django.conf.urls import patterns, url
from pool import views

urlpatterns = patterns('',
    url(r'^offer/(?P<offer_action>.*)/(?P<offer_code>.*)/$', views.offer_action),
)