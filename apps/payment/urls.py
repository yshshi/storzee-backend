from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import *
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^calculate_return_payment', calculate_return_payment, name='calculate_return_payment'),
    re_path(r'^initiate_return_payment', initiate_return_payment, name='initiate_return_payment'),
    re_path(r'^razor_payment_confirm', razor_payment_confirm, name='razor_payment_confirm'),



    *router.urls
]