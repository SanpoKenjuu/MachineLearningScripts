from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'products', views._get_products, name='products'),
    url(r'entitlements', views._get_entitlements, name ='entitlements'),
    url(r'alldata', views._get_alldata, name ='alldata'),
    ]

