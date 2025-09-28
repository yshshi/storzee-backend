from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from utils.geo import get_nearby_units
from utils.AI_assist import ai_answer
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
# apps/assist/views.py

@api_view(["GET"])
@permission_classes([AllowAny])
def ai_assist(request):
    data = request.data
    msg, lat, lon = data.get("message",""), float(data["lat"]), float(data["lon"])
    units = get_nearby_units(lat, lon, limit=6)
    result = ai_answer(msg, units)
    return Response({
        "answer": result
    })
