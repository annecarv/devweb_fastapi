import os
from typing import Dict, Any, List
import httpx
from jose import jwt, jwk
from jose.utils import base64url_decode
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")
ALGORITHMS = os.environ.get("AUTH0_ALGORITHMS", "RS256").split(",")

_JWKS_CACHE: Dict[str, Any] = {}

security = HTTPBearer()

def _get_jwks():
    global _JWKS_CACHE
    if _JWKS_CACHE:
        return _JWKS_CACHE
    if not AUTH0_DOMAIN:
        raise RuntimeError("AUTH0_DOMAIN not set")
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    r = httpx.get(url, timeout=5.0)
    r.raise_for_status()
    _JWKS_CACHE = r.json()
    return _JWKS_CACHE

def _get_jwks_key(token: str):
    jwks = _get_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def decode_jwt(token: str) -> Dict[str, Any]:
    jwk_key = _get_jwks_key(token)
    if not jwk_key:
        raise HTTPException(status_code=401, detail="Appropriate JWKS key not found")
    try:
        # construct a key and verify signature
        public_key = jwk.construct(jwk_key)
        message, encoded_signature = token.rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        if not public_key.verify(message.encode('utf-8'), decoded_signature):
            raise HTTPException(status_code=401, detail="Invalid token signature")

        # decode claims without verifying signature (we already verified)
        claims = jwt.get_unverified_claims(token)

        # validate expiration
        import time
        if 'exp' in claims and time.time() > claims['exp']:
            raise HTTPException(status_code=401, detail='Token expired')

        # validate audience if configured
        if AUTH0_AUDIENCE:
            aud = claims.get('aud')
            if isinstance(aud, list):
                if AUTH0_AUDIENCE not in aud:
                    raise HTTPException(status_code=401, detail='Invalid audience')
            else:
                if aud != AUTH0_AUDIENCE:
                    raise HTTPException(status_code=401, detail='Invalid audience')

        return claims
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {str(e)}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Testing mode: accept tokens of the form `test:sub|ROLE1,ROLE2`
    if os.environ.get("TESTING") == "1" and token.startswith("test:"):
        try:
            payload = token.split(":", 1)[1]
            sub, roles_part = payload.split("|", 1) if "|" in payload else (payload, "")
            roles = [r for r in (roles_part.split(",") if roles_part else []) if r]
            return {"sub": sub, "roles": roles, "raw": {"sub": sub, "roles": roles}}
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid test token format")
    payload = decode_jwt(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing subject")
    # roles may be in multiple places; try common locations
    roles = []
    if "roles" in payload:
        roles = payload.get("roles") or []
    # Auth0 may put roles under a namespaced claim
    if not roles:
        for k, v in payload.items():
            if isinstance(k, str) and k.startswith("https://") and isinstance(v, dict):
                # nested may contain roles
                if "roles" in v:
                    roles = v.get("roles")
    if not roles:
        # try permissions or scope
        roles = payload.get("permissions") or []
    # normalize to list of strings
    if isinstance(roles, str):
        roles = [roles]
    return {"sub": sub, "roles": roles, "raw": payload}

def require_roles(*allowed_roles: str):
    def _checker(user=Depends(get_current_user)):
        user_roles = set([r.upper() for r in user.get("roles", [])])
        allowed = set([r.upper() for r in allowed_roles])
        if not user_roles.intersection(allowed):
            raise HTTPException(status_code=403, detail="Permissão faltando")
        return user
    return _checker
