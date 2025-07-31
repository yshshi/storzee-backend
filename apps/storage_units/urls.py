from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import create_feedback,create_storage_unit
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^create_feedback', create_feedback, name='create_feedback'),
    re_path(r'^create_storage_unit', create_storage_unit, name='create_storage_unit'),


    *router.urls
]