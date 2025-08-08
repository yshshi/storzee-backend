from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import create_booking,update_luggage_deatils,update_luggage_location_by_saathi,get_luggage_deatils,validate_pickup,submit_to_rakshak,request_return
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^create_booking', create_booking, name='create_booking'),
    re_path(r'^update_luggage_deatils', update_luggage_deatils, name='update_luggage_deatils'),
    re_path(r'^update_luggage_location_by_saathi', update_luggage_location_by_saathi, name='update_luggage_location_by_saathi'),
    re_path(r'^get_luggage_deatils', get_luggage_deatils, name='get_luggage_deatils'),
    re_path(r'^validate_pickup', validate_pickup, name='validate_pickup'),
    re_path(r'^submit_to_rakshak', submit_to_rakshak, name='submit_to_rakshak'),
    re_path(r'^request_return', request_return, name='request_return'),

    *router.urls
] 