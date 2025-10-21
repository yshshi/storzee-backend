from rest_framework.decorators import api_view, permission_classes 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.users.models import UserDeviceToken
from utils.trigger_notiifcation import send_push_notification

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
def register_token(request):
    token = request.data.get('token')
    user_id = request.data.get('user_id')
    platform = request.data.get('platform')

    
    if token:
        UserDeviceToken.objects.create(token=token,
                                       user_id=user_id,
                                       platform=platform)
        return Response({'message': 'Token registered successfully'})
    return Response({'error': 'No token provided'}, status=400)

@api_view(['POST'])
def send_notification(request):
    title = request.data.get('title')
    body = request.data.get('body')

    tokens = UserDeviceToken.objects.all()
    for t in tokens:
        send_push_notification(t.token, title, body)

    return Response({'message': 'Notifications sent!'})