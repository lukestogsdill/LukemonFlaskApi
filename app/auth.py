from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from .models import User
from flask import g

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

# Basic Auth Funtionality
@basic_auth.verify_password
def verify_password(email, password):
    #check if the user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user = user
    return user.check_hash_password(password)

#Verify Token Functionality
@token_auth.verify_token
def verify_token(token):
    user = User.check_token(token)
    if not user:
        return False
    g.current_user = user
    return user