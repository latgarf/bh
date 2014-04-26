from django.conf.urls import *
from api import views
urlpatterns = patterns('',
    url(r'^query_cost$', views.query_cost, name='query_cost'),
    url(r'^query_cost/test$', views.query_cost_test, name='query_cost_test'),
    )
