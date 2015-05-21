from django.conf.urls import patterns, url
from pool import views

urlpatterns = patterns('',
    url(r'^foreign/seat/$', views.foreign_seat_list),
    url(r'^login/$', views.login_user),
    url(r'^user/verify/(?P<temporary_code>.*)/$', views.verify_user),
    url(r'^user/create/$', views.create_user),
    url(r'^offer/seat/(?P<offer_action>.*)/(?P<offer_code>.*)/$', views.resolve_seat_offer),
    url(r'^$', views.pool_list),
)