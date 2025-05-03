import json
from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser

User = get_user_model()

# Helper function for JWT tokens (optional, not used here for consistency)
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# User Registration View
class Register(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")
            if CustomUser.objects.filter(email=email).exists():
                return Response({
                    "error": "Email already exists.",
                    "details": "The provided email is already in use."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = UserRegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)  # Use TokenAuthentication
            return Response({
                "message": "User registered successfully",
                "user": serializer.data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# User Login View
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user": {"email": user.email, "id": user.id, "username": user.username},
            "token": token.key
        }, status=status.HTTP_200_OK)
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# User Logout View
class Logout(APIView):
    def post(self, request):
        try:
            # For TokenAuthentication, you could delete the token here if desired
            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)