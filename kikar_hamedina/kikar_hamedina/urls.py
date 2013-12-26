from django.conf.urls import patterns, include, url
from django.contrib import admin
from core.views import index

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('core.urls')),
    url(r'^$', index, name='index'),
)
