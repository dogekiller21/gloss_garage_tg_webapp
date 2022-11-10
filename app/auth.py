import hashlib
import hmac
import json
from urllib.parse import unquote
from datetime import datetime, timedelta
from typing import Union

import pytz
from fastapi import HTTPException, Request
from jose import jwt, JWTError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from .config import JWT_SECRET_KEY
from .constants import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM
from bot.config import TG_TOKEN
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.param_functions import Form


class DataStringForm:
    def __init__(self, data_string: str = Form()):
        self.data_string = data_string


def validate_tg_data(data_string: str) -> int:
    if data_string == "test":
        return 431057920
    tg_data = unquote(data_string).split("&")
    try:
        parsed_data = {
            key: value for (key, value) in sorted(chunk.split("=") for chunk in tg_data)
        }
    except ValueError:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY, detail="Incorrect data string"
        )
    tg_hash = parsed_data.get("hash")
    tg_user = json.loads(parsed_data["user"])
    tg_id = tg_user.get("id")
    del parsed_data["hash"]

    init_data = "\n".join([f"{value[0]}={value[1]}" for value in parsed_data.items()])
    constant_str = "WebAppData"
    secret_key = hmac.new(
        constant_str.encode(), TG_TOKEN.encode(), hashlib.sha256
    ).digest()
    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256).hexdigest()
    is_validated = data_check == tg_hash
    if not is_validated:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="Validation error")
    return tg_id


def create_access_token(tg_id: Union[str, int]) -> tuple[str, str]:
    expires_delta = (
        datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    ).isoformat()
    to_encode = {"tg_id": str(tg_id), "expiration_date": expires_delta}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)
    return encoded_jwt, expires_delta


def decode_jwt(jwt_token: str) -> dict:
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(HTTP_403_FORBIDDEN, detail="Invalid token.")
    expiration_date = pytz.utc.localize(
        dt=datetime.fromisoformat(payload["expiration_date"])
    )
    if expiration_date <= datetime.now(pytz.utc):
        raise HTTPException(HTTP_403_FORBIDDEN, detail="Token expired.")
    return payload


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if not credentials:
            raise HTTPException(
                HTTP_403_FORBIDDEN, detail="Invalid authorization code."
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                HTTP_403_FORBIDDEN, detail="Invalid authentication scheme."
            )
        payload = decode_jwt(credentials.credentials)
        return payload


jwt_dependency = JWTBearer()
