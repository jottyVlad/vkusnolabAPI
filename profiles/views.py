from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .serializers import ProfileSerializer, PasswordChangeSerializer


@method_decorator(never_cache, name='dispatch')
class ProfileView(RetrieveUpdateAPIView):
    """
    View for retrieving and updating user profiles.
    GET: Returns user profile with their recipes
    PATCH: Updates user profile (email, bio, profile_picture) or changes password
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = get_user_model().objects.all()
    lookup_field = 'username'

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if this is a password change request
        if 'old_password' in request.data and 'new_password' in request.data:
            serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            instance.set_password(serializer.validated_data['new_password'])
            instance.save()
            return Response({'message': 'Password successfully updated'}, status=status.HTTP_200_OK)
        
        # Regular profile update
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class ProfileByUsernameView(RetrieveAPIView):
    """
    View for retrieving user profiles by username.
    GET: Returns user profile with their recipes
    """
    serializer_class = ProfileSerializer
    queryset = get_user_model().objects.all()
    lookup_field = 'username'
