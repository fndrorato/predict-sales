from rest_framework import permissions


class GlobalDefaultPermission(permissions.BasePermission):
    """
    Global model permissions
    """

    def has_permission(self, request, view):
        
        if request.user and request.user.is_superuser:
            return True        
        
        model_permission_codename = self.__get_model_permission_codename(request.method, view)
        if not model_permission_codename:
            return False

        return request.user.has_perm(model_permission_codename)

    def __get_model_permission_codename(self, method, view):
        try:          
            model_name = view.queryset.model._meta.model_name
            app_label = view.queryset.model._meta.app_label
            action = self.__get_action_suffix(method)

            return f"{app_label}.{action}_{model_name}"
        except AttributeError:
            return None

    def __get_action_suffix(self, method):
        method_actions = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
            'OPTIONS': 'view',
            'HEAD': 'view',
        }
        return method_actions.get(method, '')


class IsSelf(permissions.BasePermission):
    """Permissão para garantir que o usuário só pode alterar seus próprios dados"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user

class CustomOrderPermission(permissions.BasePermission):
    """
    Permissão baseada em grupo e status da ordem:
    - Comprador: pode criar e editar se status == 1
    - Analista/Supervisor: pode editar se status == 1 ou 2
    - Somente Analista pode mudar status de 1 → 2
    - Somente Supervisor pode mudar status de 2 → 3
    - Administrador tem acesso total
    - Status 3 é bloqueado para todos
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method.upper()
        status = obj.status.id if obj.status else None
        user_groups = {g.name.lower() for g in user.groups.all()}

        if user.is_superuser:
            return True

        is_comprador = 'comprador' in user_groups
        is_analista = 'analista' in user_groups
        is_supervisor = 'supervisor' in user_groups
        is_administrador = 'administrador' in user_groups
        
        print(f"User: {user.username}, Groups: {user_groups}, Method: {method}, Order Status: {status}")

        # Leitura é sempre permitida
        if method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Ordem em status 3 — ninguém pode alterar
        if status == 3:
            return False
        
        # Administrador tem acesso total
        if is_administrador:
            return True

        # POST (criação) — permitido para todos esses grupos
        if method == 'POST':
            return is_comprador or is_analista or is_supervisor

        # PUT/PATCH — atualização
        if method in ['PUT', 'PATCH']:
            # Comprador só pode alterar se status == 1
            if is_comprador and status == 1:
                return True

            # Analista pode editar status 1 e 2
            if is_analista and status in [1, 2]:
                return True

            # Supervisor pode editar status 1 e 2
            if is_supervisor and status in [1, 2]:
                return True

        # Regras específicas de transição de status devem ser verificadas no serializer
        return False
