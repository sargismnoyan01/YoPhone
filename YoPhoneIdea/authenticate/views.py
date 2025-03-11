import redis
from django.db import IntegrityError
from django.db.models import F
from datetime import timedelta
from django.utils import timezone
import threading
import time
from datetime import timezone
from pprint import pprint
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from datetime import datetime
from django_user_agents.utils import get_user_agent
from .serializers import RegisterUserSerializer, LoginUserSerializer
from .models import *
from .utils import *
from django.conf import settings

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)


class LogoutAllDevicesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        tokens = OutstandingToken.objects.filter(user=user)

        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return Response({'message': 'Logged out from all devices'}, status=status.HTTP_200_OK)


class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            obj = CustomUser(**serializer.validated_data)
            obj.is_verified = False
            obj.save()
            redis_client.setex(f"pending_user:{obj.pk}", 40, obj.pk)
            uid = urlsafe_base64_encode(force_bytes(obj.pk))
            token = default_token_generator.make_token(obj)
            verification_link = f"{request.scheme}://{request.get_host()}{reverse('verify-email', kwargs={'uidb64': uid, 'token': token})}"
            print(verification_link)
            subject = "Verify Your Email"
            message = f"Hi {obj.username},\nClick the link below to verify your email:\n{verification_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [obj.email])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def Email_code(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(CustomUser, pk=uid)
        if redis_client.exists(f"pending_user:{user.pk}"):
            if default_token_generator.check_token(user, token):
                if request.method == 'POST':
                    password = request.data.get('password')
                    user.set_password(password)
                    user.is_verified = True
                    user.save()

                    redis_client.delete(f"pending_user:{user.pk}")

                    return Response({"message": "Email successfully verified!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Email not successfully verified!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.delete()
            return Response({"error": "Token expired. User data deleted."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Welcome to Block Django!"})

    def post(self, request):
        form = LoginUserSerializer(data=request.data)
        if form.is_valid():
            username = form.validated_data.get('username')
            password = form.validated_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                user_agent = get_user_agent(request)
                device = user_agent.device.family
                os = user_agent.os.family
                browser = user_agent.browser.family
                user_email = user.email
                subject = "Hi {}".format(username)
                timee = datetime.now(timezone.utc)
                # logout_url = request.build_absolute_uri(reverse('logout-all-devices'))
                logout_url = 'http://localhost:5173/logout/'

                message = f"""
                <html>
                <head>
                    <style>
                        .container {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            padding: 20px;
                            text-align: center;
                        }}
                        .button-container {{
                            margin: 20px 0;
                        }}
                        .btn {{
                            display: inline-block;
                            padding: 14px 28px;
                            font-size: 16px;
                            font-weight: bold;
                            color: white;
                            background-color: #ff4d4d;
                            text-decoration: none;
                            border-radius: 6px;
                            text-align: center;
                            transition: background-color 0.3s;
                        }}
                        .btn:hover {{
                            background-color: #cc0000;
                        }}
                        .info {{
                            text-align: left;
                            margin: 20px auto;
                            max-width: 500px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <p class="info">Your page was accessed at {timee}, with this device type:</p>
                        <ul class="info">
                            <li><strong>Device:</strong> {device}</li>
                            <li><strong>OS:</strong> {os}</li>
                            <li><strong>Browser:</strong> {browser}</li>
                        </ul>
                        <p class="info">If it wasn't you, click the button below to log out from all devices immediately:</p>
                        <div class="button-container">
                            <a href="{logout_url}" class="btn">Logout from All Devices</a>
                        </div>
                        <p class="info">If this was you, you can safely ignore this email.</p>
                    </div>
                </body>
                </html>
                """

                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user_email],
                    fail_silently=False,
                    html_message=message  # Send email as HTML
                )

                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
