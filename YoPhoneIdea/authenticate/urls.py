from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('verify-email/<uidb64>/<token>/', Email_code, name='verify-email'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # For frontend
    path('logout-all/', LogoutAllDevicesAPIView.as_view(), name='logout-all-devices'),

]

# Frontend form
# POST /api/token/refresh/
# Content-Type: application/json
#
# {
#     "refresh": "your_refresh_token_here"
# }