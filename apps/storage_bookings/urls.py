from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import create_booking,update_luggage_deatils,update_luggage_location_by_saathi,get_luggage_deatils,validate_pickup,submit_to_rakshak,request_return,booking_details,booking_status,change_status,get_all_bookings,change_amount,get_detail_bookings
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^create_booking', create_booking, name='create_booking'),
    re_path(r'^update_luggage_deatils', update_luggage_deatils, name='update_luggage_deatils'),
    re_path(r'^update_luggage_location_by_saathi', update_luggage_location_by_saathi, name='update_luggage_location_by_saathi'),
    re_path(r'^get_luggage_deatils', get_luggage_deatils, name='get_luggage_deatils'),
    re_path(r'^validate_pickup', validate_pickup, name='validate_pickup'),
    re_path(r'^submit_to_rakshak', submit_to_rakshak, name='submit_to_rakshak'),
    re_path(r'^request_return', request_return, name='request_return'),
    re_path(r'^booking_details', booking_details, name='booking_details'),
    re_path(r'^booking_status', booking_status, name='booking_status'),
    re_path(r'^change_status', change_status, name='change_status'),
    re_path(r'^get_all_bookings', get_all_bookings, name='get_all_bookings'),
    re_path(r'^change_amount', change_amount, name='change_amount'),
    re_path(r'^get_detail_bookings', get_detail_bookings, name='get_detail_bookings'),

    *router.urls
] 