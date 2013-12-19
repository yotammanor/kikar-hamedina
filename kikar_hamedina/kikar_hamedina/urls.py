from django.conf.urls import patterns, include, url
from django.contrib import admin
from core.views import index

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kikar_hamedina.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index, name='index'),
)
