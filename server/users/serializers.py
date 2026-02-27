from django.contrib.auth.models import User, Group
from django.contrib.auth import password_validation
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField(write_only=True, required=False)  # Permite definir o grupo ao criar/editar
    group_name = serializers.SerializerMethodField()  # Apenas leitura
    group_id_read = serializers.SerializerMethodField()  # Apenas leitura

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'group_id', 'group_id_read',
                  'first_name', 'last_name', 'is_active', 'group_name']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        # Verifica duplicidade de username, ignorando o próprio usuário
        if username:
            qs = User.objects.filter(username=username)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'username': 'Este nome de usuário já está em uso.'})

        # Verifica duplicidade de email, ignorando o próprio usuário
        if email:
            qs = User.objects.filter(email=email)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'email': 'Este e-mail já está em uso.'})

        # Verifica se está criando (self.instance é None) e exige senha
        if not self.instance and not data.get('password'):
            raise serializers.ValidationError({'password': 'A senha é obrigatória na criação.'})

        return data


    def get_group_name(self, obj):
        group = obj.groups.first()
        return group.name if group else None

    def get_group_id_read(self, obj):
        group = obj.groups.first()
        return group.id if group else None       

    def create(self, validated_data):
        group_id = validated_data.pop('group_id', None)  # Obtém o ID do grupo (se fornecido)
        user = User.objects.create_user(**validated_data)  # Cria o usuário

        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)  # Associa o usuário ao grupo
            except Group.DoesNotExist:
                raise serializers.ValidationError({'group_id': 'Grupo não encontrado'})

        return user

    def update(self, instance, validated_data):
        group_id = validated_data.pop('group_id', None)

        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)  # Garante que a senha seja hashada
            else:
                setattr(instance, attr, value)
        instance.save()

        if group_id is not None:
            try:
                group = Group.objects.get(id=group_id)
                instance.groups.clear()  # Remove grupos antigos
                instance.groups.add(group)  # Adiciona novo grupo
            except Group.DoesNotExist:
                raise serializers.ValidationError({'group_id': 'Grupo não encontrado'})

        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def validate(self, data):
        user_id = self.instance.id

        # Se o email estiver sendo alterado, verifica se já existe em outro usuário
        email = data.get('email')
        if email and User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Este e-mail já está em uso por outro usuário.'})

        return data

    def update(self, instance, validated_data):
        """Atualiza os dados do usuário"""
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))  # Hash da senha

        return super().update(instance, validated_data)

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A nova senha deve ter pelo menos 8 caracteres.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user