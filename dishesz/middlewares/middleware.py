from urllib.parse  import parse_qs 


from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections


from channels.auth import AuthMiddleware
from channels.db import database_sync_to_async
from channels.sessions import CookieMiddleware, SessionMiddleware


from rest_framework_simplejwt.tokens import AccessToken 


user_model = get_user_model() 
current_user = None 



@database_sync_to_async
def get_user(scope): 

    # close old connections 
    close_old_connections() 

    # retrieve query string from url scope 
    query_string = parse_qs(scope['query_string'].decode())

    # get token from decoded query string 
    token = query_string.get('token')

    if not token: 
        return AnonymousUser() 

    # retrieve user from token 
    try: 
        access_token = AccessToken(token[0])
        user = user_model.objects.get(id=access_token['user_id'])
    except user_model.DoesNotExist: 
        return AnonymousUser()
    except Exception: 
        return AnonymousUser() 

    
    if not user.is_active: 
        return AnonymousUser() 

    return user 



class TokenAuthMiddleware(AuthMiddleware): 
    async def resolve_scope(self, scope):
        scope['user']._wrapped = await get_user(scope)


def TokenAuthMiddlewareStack(inner): 
    return CookieMiddleware(SessionMiddleware(TokenAuthMiddleware(inner)))