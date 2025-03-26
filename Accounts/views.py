from .models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import *

# Create your views here.

class Register(APIView):
    '''
    Api to fetch register a user
    Required params - username, password, first_name
    Constraint - The username must be unique
    Returns - A jwt refresh and access token
    '''
    def post(self,request):
        try:
            username = request.data['username']
            password = request.data['password']
            first_name = request.data['first_name']
            mobile_number = request.data.get('mobile_number', None)
            last_name = request.data.get('last_name', "")
            if len(User.objects.filter(username=username))!=0:
                return Response({'success': False, "message": "Username already exists!!"},status=status.HTTP_400_BAD_REQUEST)
            user_object = User()
            user_object.username=username
            user_object.set_password(password)
            user_object.mobile_number=mobile_number
            user_object.first_name = first_name
            user_object.last_name = last_name
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_object.save()        
            user = User.objects.get(username=username)
            refresh = RefreshToken.for_user(user)
            return Response({"success": True, "message": "Your account has been successfully created!!",
                    'payload': serializer.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)},
                    status=status.HTTP_202_ACCEPTED)
        except KeyError:
            return Response({"success": False, "message": "username,password and first_name are required for registration!!"},
                    status=status.HTTP_406_NOT_ACCEPTABLE)

class Login(APIView):
    '''
    Api to login a user
    Required params - username, password
    Returns - A jwt refresh and access token
    '''
    def get(self,request):
        try:
            username = request.data['username']
            password = request.data['password']
            user=authenticate(username=username,password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                serializer = RegisterSerializer(user)
                return Response({"success": True, "message": "Login successful",
                                'payload': serializer.data,
                                'refresh': str(refresh),
                                'access': str(refresh.access_token)},
                                status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'message':'Invalid Credentials'},status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"success": False, "message": "Please enter your username and password!!"},
                    status=status.HTTP_406_NOT_ACCEPTABLE)