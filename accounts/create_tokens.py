from rest_framework_simplejwt.tokens import RefreshToken

def create_tokens_for_user(user):
    """
    Generate JWT tokens for the given user
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
