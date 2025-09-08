from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_decode_token(token):
    if token != "admin":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": "admin"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    return fake_decode_token(token)
