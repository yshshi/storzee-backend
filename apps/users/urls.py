from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import register
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^register', register, name='register'),

    *router.urls
]