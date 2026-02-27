from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers import (
    UserSerializer, 
    UserUpdateSerializer,
    PasswordChangeSerializer,
)
from app.permissions import GlobalDefaultPermission, IsSelf


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, GlobalDefaultPermission, ]


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, GlobalDefaultPermission, ]  # Apenas usuários autenticados podem acessar


class UserUpdateView(UpdateAPIView):
    """Permite ao usuário autenticado atualizar seus próprios dados"""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsSelf, ]

    def get_object(self):
        return self.request.user  # Retorna o usuário autenticado


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated, IsSelf, ]

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
