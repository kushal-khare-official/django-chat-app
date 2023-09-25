from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([])
def chat_view(request, room_id=0):
    return render(request, 'chat.html', {"room_id": room_id})


@api_view(['GET'])
@permission_classes([])
def user_registration(request):
    return render(request, 'register.html')


@api_view(['GET'])
@permission_classes([])
def user_login(request):
    return render(request, 'login.html')
