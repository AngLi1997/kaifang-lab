"""JWT 签发工具。"""

import jwt

from app.schemas.login import JWTPayload
from app.settings.config import settings


def create_access_token(*, data: JWTPayload):
    """用 `settings.SECRET_KEY` 签发包含 `data` 的访问令牌。"""
    payload = data.model_dump().copy()
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
