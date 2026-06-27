import json
import hmac
import hashlib
import base64
import secrets
import time
import logging

from odoo import models, api

_logger = logging.getLogger(__name__)

SECRET_KEY_PARAM       = 'jwt_rest_api.secret_key'
ACCESS_TOKEN_EXPIRY    = 15 * 60          # 15 minutes  (seconds)
REFRESH_TOKEN_EXPIRY   = 7 * 24 * 60 * 60 # 7 days      (seconds)


def _b64url_encode(data: bytes) -> str:
    pass

def _b64url_decode(s: str) -> bytes:
    pass

class JwtUtils(models.AbstractModel):

    _name = 'jwt.utils'
    _description = 'JWT Utility Helper'

    @api.model
    def get_or_create_secret_key(self) -> str:
        pass

    @api.model
    def rotate_secret_key(self) -> str:
        pass
    @api.model
    def _build_jwt(self, payload: dict, secret: str) -> str:
        pass

    @api.model
    def generate_access_token(self, user_id: int, login: str) -> str:
        pass

    @api.model
    def generate_refresh_token(self, user_id: int, login: str) -> str:
        pass

    @api.model
    def verify_token(self, token: str, expected_type: str = 'access') -> dict:
        pass