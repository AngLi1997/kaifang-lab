"""密码哈希与生成工具。"""

from passlib import pwd
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否与哈希匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """使用 argon2 生成密码哈希。"""
    return pwd_context.hash(password)


def generate_password() -> str:
    """生成随机密码。"""
    return pwd.genword()
