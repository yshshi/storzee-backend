from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import create_booking,update_luggage_deatils,update_luggage_location_by_saathi,get_luggage_deatils
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^create_booking', create_booking, name='create_booking'),
    re_path(r'^update_luggage_deatils', update_luggage_deatils, name='update_luggage_deatils'),
    re_path(r'^update_luggage_location_by_saathi', update_luggage_location_by_saathi, name='update_luggage_location_by_saathi'),
    re_path(r'^get_luggage_deatils', get_luggage_deatils, name='get_luggage_deatils'),

    *router.urls
]