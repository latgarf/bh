from django.conf.urls import *
from bhsite import views

urlpatterns = patterns('',

	url(r'^investors', views.investors),
	url(r'^experts', views.experts),
	url(r'^faq', views.faq),
	url(r'^contact', views.contact),

	url(r'^how_it_works', views.how_it_works),

    url(r'^$', views.futurebuy, name='future'),
    url(r'^premium/', views.premium, name='premium'),
    url(r'^query/', views.query, name='query'),

    url(r'^validate_address/', views.validate_address, name='validate_address'),
    )
