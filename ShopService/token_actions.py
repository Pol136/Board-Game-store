from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt

SECRET_KEY = "89C314947595C82FCA6B7EFC86FE8F2FFF4DE6A071A5489633AD73DBEDAF3324"
ALGORITHM = "HS256"

def create_access_token(id: int, username: str, email: str, role: str, expires_delta: timedelta):
    encode = {'name': username, 'id': id, 'email': email, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        username: str = payload.get('name')
        user_id: int = payload.get('id')
        if username is None and user_id is None:
            raise  HTTPException(status_code=401, detail="Could not validate user")

        return {'username': username, 'user_id': user_id}
    except:
        raise HTTPException(status_code=401, detail="Could not validate user")