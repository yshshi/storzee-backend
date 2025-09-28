from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import ai_assist
router = DefaultRouter(trailing_slash=False)


urlpatterns = [
    
    re_path(r'^ai_assist', ai_assist, name='ai_assist'),


    *router.urls
]