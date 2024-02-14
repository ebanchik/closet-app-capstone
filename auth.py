import jwt
import os
import logging

def get_user_id_from_jwt(token):
    # Retrieve the secret key from the environment variable
    secret_key = os.environ.get('SECRET_KEY')

    # Log the token before attempting to decode it
    # logging.info(f"Attempting to decode token: {token}")

    try:
        # Decode the JWT token with the secret key and specified algorithm
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        # logging.info(f"Token decoded successfully. User ID: {user_id}")
        # logging.info(f"token: {token}")
        return user_id
    except jwt.DecodeError:
        # Handle case where the token is malformed
        logging.error("Token is malformed.")
        raise
    except jwt.ExpiredSignatureError:
        # Handle case where the token has expired
        logging.error("Token has expired.")
        raise
    except jwt.InvalidSignatureError:
        # Handle case where the signature is invalid (e.g., the token was tampered with)
        logging.error("Invalid token signature.")
        raise
    except Exception as e:
        # Catch any other unexpected exceptions
        logging.error(f"An unexpected error occurred: {str(e)}")
        
