from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter(trailing_slash=False)

app_name = "payment" 

urlpatterns = [
    
    path('initiate_return_payment/', views.initiate_return_payment, name='initiate_return_payment'),
    path('hosted_checkout/<int:payment_id>/', views.hosted_checkout, name='hosted_checkout'),
    path('verify_return_payment/', views.verify_return_payment, name='verify_return_payment'),
    path('calculate_return_payment/', views.calculate_return_payment, name='calculate_return_payment'),



    *router.urls
]