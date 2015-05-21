from django.conf.urls import patterns, url
from pool import views

urlpatterns = patterns('',
    url(r'^login/$', views.login_user),
    url(r'^logout/$', views.logout_user),
    url(r'^foreign/$', views.foreign_detail),
    url(r'^offer/seat/(?P<offer_action>.*)/(?P<offer_code>.*)/$', views.resolve_seat_offer),
    url(r'^user/verify/(?P<temporary_code>.*)/$', views.verify_user),
    url(r'^user/create/$', views.create_user),
    url(r'^$', views.pool_list),
)