import datetime
import jwt
from django.conf import settings


def generate_access_token(user):
    '''
    generates the token for JWT auhentication
    '''

    access_token_payload = {
        'user_name': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(
            days=1, minutes=5),
        'iat': datetime.datetime.utcnow(),
    }

    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256')
    return access_token


def token_decoder(token):
    '''
    Decodes the token to return the payload
    '''

    # Removing Bearer flag from token
    access_token = token.split(' ')[1]
    # Decoding token
    payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=["HS256"]
    )
    return payload


# Extract username from JWT
def get_username(request):
    '''
    returns the username from the payload
    '''

    # Getting token from request object
    authorization_header = request.headers.get('Authorization')
    # Decoding token
    decoded_token = token_decoder(authorization_header)
    # Extracting username from token
    username = decoded_token['user_name']

    return username
