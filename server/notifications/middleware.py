from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # debug opcional:
        # print("[JWT-MW] chamado; qs=", scope.get("query_string"))

        scope["user"] = AnonymousUser()
        qs = parse_qs(scope.get("query_string", b"").decode())
        token = (qs.get("token") or [None])[0]

        if token:
            auth = JWTAuthentication()
            try:
                validated = auth.get_validated_token(token)
                user = await database_sync_to_async(auth.get_user)(validated)
                scope["user"] = user
            except (InvalidToken, AuthenticationFailed, Exception):
                pass
        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    # mantém suporte a sessão/cookies também
    from channels.auth import AuthMiddlewareStack
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
