from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer


@method_decorator(never_cache, name='dispatch')
class UserRegistrationViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            token = RefreshToken.for_user(serializer.instance)

            return Response({
                "message": "User registered successfully",
                "access": str(token.access_token),
                "refresh": str(token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(never_cache, name='dispatch')
class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated,]
    queryset: CustomUser = get_user_model()
    serializer_class = UserSerializer

    def retrieve(self, request, pk):
        user = self.queryset.objects.get(pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)