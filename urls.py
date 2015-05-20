from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    (r'^pool/admin/', include(admin.site.urls)),
    (r'^pool/', include('pool.urls')),
)