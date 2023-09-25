from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Message, ChatRoom
from .serializers import UserSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([])
def user_registration(request):
    request.data['password'] = make_password(request.data.get('password'))

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"message": "Both username/email and password are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)

        print(check_password(password, user.password))

        if not user.check_password(password):
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        request.session['token'] = token.key
        request.session['user_id'] = user.id

        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_online": user.is_online,
            "first_name": user.first_name,
            "last_name": user.last_name
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_online_users(request):
    online_users = User.objects.filter(is_online=True)
    serializer = UserSerializer(online_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat(request):
    recipient_username = request.data.get('recipient_username')

    recipient_user = get_object_or_404(User, username=recipient_username)

    if not recipient_user:
        return Response({"message": "Recipient user not found"}, status=status.HTTP_404_NOT_FOUND)

    if not recipient_user.is_online:
        return Response({"message": "Recipient is offline"}, status=status.HTTP_400_BAD_REQUEST)

    chat_room = ChatRoom.objects.filter(users=request.user).filter(users=recipient_user).first()

    if chat_room is None:
        chat_room_name = f"chat_{request.user.username}_{recipient_username}"

        chat_room, created = ChatRoom.objects.get_or_create(name=chat_room_name)
        chat_room.users.add(request.user, recipient_user)

    return Response({"chat_room_id": chat_room.id},
                    status=status.HTTP_200_OK)


with open(settings.FRIENDS_JSON_PATH, 'r') as json_file:
    friends_data = json.load(json_file)["users"]


@api_view(['GET'])
def suggested_friends(request, user_id):
    user = next((user for user in friends_data if user['id'] == user_id), None)

    if not user:
        return JsonResponse({"message": "User not found"}, status=404)

    user_interests = user.get('interests', {})

    friend_scores = {}

    for friend in friends_data:
        friend_id = friend['id']
        if friend_id == str(user_id):
            continue

        friend_interests = friend.get('interests', {})

        friend_score = sum(user_interests[interest] + friend_interests[interest]
                           for interest in user_interests if interest in friend_interests)

        friend_scores[friend_id] = friend_score

    sorted_friends = sorted(friends_data, key=lambda fr: friend_scores[fr['id']], reverse=True)

    return JsonResponse({"suggested_friends": sorted_friends[:5]}, status=200)
