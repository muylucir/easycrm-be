import json
import time
from typing import Dict, Any

import requests
from jose import jwk, jwt
from jose.utils import base64url_decode
from datetime import datetime, timedelta
from typing import Any, Union
from passlib.context import CryptContext
from app.core.config import settings


# JWKS URL
JWKS_URL = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"

# JWKS를 가져오고 캐시하는 함수
def get_jwks():
    response = requests.get(JWKS_URL)
    jwks = response.json()
    return {key["kid"]: jwk.construct(key) for key in jwks["keys"]}

# JWKS 캐시
jwks_cache = get_jwks()

def verify_cognito_token(token: str) -> Dict[str, Any]:
    # 토큰의 헤더를 디코딩
    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]

    # 토큰 서명에 사용된 키 찾기
    key = jwks_cache.get(kid)
    if not key:
        # 키가 캐시에 없으면 JWKS를 다시 가져옴
        jwks_cache.update(get_jwks())
        key = jwks_cache.get(kid)
        if not key:
            raise ValueError("Public key not found in JWKS")

    # 토큰 검증
    message, encoded_signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    if not key.verify(message.encode(), decoded_signature):
        raise ValueError("Signature verification failed")

    # 클레임 검증
    claims = jwt.get_unverified_claims(token)
    if time.time() > claims["exp"]:
        raise ValueError("Token is expired")

    # 여기에 추가적인 클레임 검증 로직을 넣을 수 있습니다
    # 예: 발행자(iss) 확인, 대상(aud) 확인 등

    return claims

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    JWT 액세스 토큰 생성
    :param subject: 토큰의 주체 (일반적으로 사용자 ID)
    :param expires_delta: 토큰 만료 시간
    :return: 생성된 JWT 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호 비교
    :param plain_password: 평문 비밀번호
    :param hashed_password: 해시된 비밀번호
    :return: 비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱
    :param password: 평문 비밀번호
    :return: 해시된 비밀번호
    """
    return pwd_context.hash(password)