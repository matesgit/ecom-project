from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
# from .models import realuser


# class CustomJWTAuthentication(JWTAuthentication):
#     def get_user(self, validated_token):
#         try:
#             user_id = validated_token.get('user_id')
            
#             if user_id is None:
#                 raise AuthenticationFailed('Token contained no recognizable user identification')
            
#             user = realuser.objects.get(id=user_id)
            
#             return user
            
#         except realuser.DoesNotExist:
#             raise AuthenticationFailed('User not found')
#         except Exception as e:
#             raise AuthenticationFailed(f'Authentication failed: {str(e)}')