from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import User


@ratelimit(key='ip', rate=RATE_LIMIT_REGISTER, method='POST', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user (USER or BRAND role)
    
    POST /api/auth/register/
    
    Request Body:
        email: User email (required)
        password: User password (required)
        password2: Password confirmation (required)
        first_name: First name (optional)
        last_name: Last name (optional)
        phone_number: Phone number (optional)
        role: USER or BRAND (required)
    
    Returns:
        Response: User data and JWT tokens
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return success_response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, message='User registered successfully', status_code=status.HTTP_201_CREATED)
    
    return error_response('Invalid registration data', errors=serializer.errors)


@ratelimit(key='ip', rate=RATE_LIMIT_LOGIN, method='POST', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and get JWT tokens
    
    POST /api/auth/login/
    
    Request Body:
        email: User email (required)
        password: User password (required)
    
    Returns:
        Response: User data and JWT tokens
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return error_response('Email and password are required')
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        return unauthorized_response('Invalid email or password')
    
    if not user.is_active:
        return unauthorized_response('User account is disabled')
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    logger.info(f"User logged in: {user.email}")
    
    return success_response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, message='Login successful')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current logged-in user details
    
    GET /api/auth/me/
    
    Returns:
        Response: Current user data
    """
    serializer = UserSerializer(request.user)
    return success_response({
        'user': serializer.data
    })
