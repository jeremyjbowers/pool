from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    (r'^pool/', include('pool.urls')),
    (r'^admin/', include(admin.site.urls)),
)