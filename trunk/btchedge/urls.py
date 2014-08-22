from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^future/', include('bhsite.urls')),
    #~ url(r'^api/', include('api.urls')),
)
