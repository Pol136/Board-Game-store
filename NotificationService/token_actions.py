from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

import jwt

SECRET_KEY = "89C314947595C82FCA6B7EFC86FE8F2FFF4DE6A071A5489633AD73DBEDAF3324"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/token')


def create_access_token(id: int, username: str, email: str, role: str, expires_delta: timedelta):
    encode = {'name': username, 'id': id, 'email': email, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('name')
        user_id: int = payload.get('id')
        user_email: str = payload.get('email')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate user")
        return {'username': username, 'user_id': user_id, 'email': user_email, 'role': user_role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate user") from e


async def get_user_if_admin(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('name')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if role is None:
            raise HTTPException(status_code=401, detail="Could not validate user")
        if role != 'admin':
            raise HTTPException(status_code=401, detail="You don't have the rights to use this feature")
        return {'username': username, 'user_id': user_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate user") from e
