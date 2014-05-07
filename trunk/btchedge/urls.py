from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'btchedge.views.home', name='home'),
    # url(r'^btchedge/', include('btchedge.foo.urls')),

    url(r'^future/', include('bhsite.urls')),
    url(r'^api/', include('api.urls')),
)
