from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import (
    UserRegistrationSerializer,
    CustomAuthTokenSerializer,
    UserLoginResponseSerializer,
    CustomUserSerializer,
    UserInfoUpdateSerializer
)
from .authentication import BearerTokenAuthentication


# Register API
@api_view(['POST'])
@permission_classes([AllowAny])
def userRegistration(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login API
@api_view(['POST'])
@permission_classes([AllowAny])
def userAuthTokenLogin(request):
    serializer = CustomAuthTokenSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    token, created = Token.objects.get_or_create(user=user)
    
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    # Determine the role based on user attributes
    if user.is_superuser:
        role = 'admin'
    else:
        role = 'customer'
    
    # Customize the response data
    response_data = {
        'access_token': token.key,
        'token_type': 'bearer',
        'expires_in': 36000,  # token expiration time (in seconds)
        'user': {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined, 
            'role': role
        }
    }

    serializer = UserLoginResponseSerializer(data=response_data)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)


# Logout API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def userLogout(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'detail': 'Authorization header is missing.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        auth_token = auth_header.split(' ')[1]
    except IndexError:
        return Response({'detail': 'Invalid authorization header format.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token = Token.objects.get(key=auth_token)
    except Token.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token.delete()

    return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)


# Password reset request API
@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetRequest(request):
    email = request.data.get('email', None)
    if email is None:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found in the database.'}, status=status.HTTP_404_NOT_FOUND)

    # Generate a random 6-digit code (simulated as a constant value here)
    code = 135246

    return Response({'detail': 'Password reset code sent to your email.'}, status=status.HTTP_200_OK)


# Password reset check code API
@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetCodeCheck(request):
    email = request.data.get('email', None)
    code = request.data.get('code', None)
    codeValue = "135246"

    if not all([email, code]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found in the database.'}, status=status.HTTP_404_NOT_FOUND)

    if code != codeValue:
        return Response({'detail': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Code is correct, Now you can change your password.'}, status=status.HTTP_200_OK)


# Password reset confirm API
@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetConfirm(request):
    email = request.data.get('email', None)
    code = request.data.get('code', None)
    password = request.data.get('password', None)
    confirm_password = request.data.get('confirm_password', None)
    codeValue = "135246"

    if not all([email, code, password, confirm_password]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found in the database.'}, status=status.HTTP_404_NOT_FOUND)

    if code != codeValue:
        return Response({'detail': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save()
    
    return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)


# User Details by token API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated]) 
def myDetails(request):
    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update user information API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def updateUserInfo(request):
    user = request.user
    data = request.data

    required_fields = ['first_name', 'last_name', 'email', 'username']
    missing_fields = [field for field in required_fields if field not in data]
    if len(missing_fields) == len(required_fields):
        return Response({'detail': 'At least one of the following fields is required: first_name, last_name, email, username'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserInfoUpdateSerializer(user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "User info updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
