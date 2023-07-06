from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.sessions import CookieMiddleware, SessionMiddleware

User = get_user_model()

class WebSocketAuthMiddleware:
    def __init__(self, inner):
        # Store the inner application or middleware
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Authenticate the WebSocket connection
        user = await self.authenticate_socket(scope)
        # Add the authenticated user to the scope
        scope['user'] = user

        # Call the inner application or middleware
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def authenticate_socket(self, scope):
        try:
            jwt_auth = JWTAuthentication()
            # token_string = scope["query_string"].decode('utf-8')

            # Split the string on '=' and get the second part
            # token = token_string.split('=')[1]
            # raw_token = scope['query_string']
            # print(token)
            # raw_token = scope['cookies'].get('token')
            raw_token = self.get_token_from_scope(scope)
            validated_token = jwt_auth.get_validated_token(raw_token)
            user = jwt_auth.get_user(validated_token)
            return user
        except Exception:
            return None

    def get_token_from_scope(self, scope):
        # headers = dict(scope['headers'])
        raw_token = scope.get('query_string', None).decode('utf-8')
        if raw_token:
            token_prefix = 'token='
            token_start_index = raw_token.find(token_prefix)
            if token_start_index != -1:
                token_start_index += len(token_prefix)
                token_end_index = raw_token.find(';', token_start_index)
                if token_end_index == -1:
                    token_end_index = None
                return raw_token[token_start_index:token_end_index]
        return None

def TokenAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(WebSocketAuthMiddleware(inner)))