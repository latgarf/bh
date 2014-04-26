from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'btchedge.views.home', name='home'),
    # url(r'^btchedge/', include('btchedge.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^future/', include('bhsite.urls')),
    url(r'^api/', include('api.urls')),

)

# urlpatterns += staticfiles_urlpatterns()
# urlpatterns += static(
#     '/static/',
#     document_root='/home/kfeng/btc/webserver/btchedge/'
# )
