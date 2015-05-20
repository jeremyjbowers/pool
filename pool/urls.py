from django.conf.urls import patterns, url
from pool import views

urlpatterns = patterns('',
    url(r'^user/create/$', views.create_user),
    url(r'^offer/seat/(?P<offer_action>.*)/(?P<offer_code>.*)/$', views.resolve_seat_offer),
)