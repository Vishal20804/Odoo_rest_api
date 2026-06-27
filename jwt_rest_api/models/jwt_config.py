from odoo import models, fields, api
from odoo.http import request
from odoo.exceptions import AccessDenied
from datetime import datetime, timedelta
import jwt
import secrets

print(jwt)
print(jwt.__file__)
print(dir(jwt))
class JWTConfig(models.Model):
    _name = 'jwt.config'
    _description = 'JWT Configuration'

    key = fields.Char(string='Key', required=True)
    value = fields.Text(string='Value', required=True)

    @api.model

    def _get_secret_key(self):

        config = self.search([('key','=','jwt_secret')],limit=1)
        if not config:
            secret = secrets.token_hex(32)
            config = self.create({
                'key':'jwt_secret',
                'value':secret
            })

        return config.value
    
    def generate_access_token(self,user):

        secret_key = self._get_secret_key()
        access_expiry = datetime.utcnow() + timedelta(minutes=15)
        payload = {
                'uid':user.id,
                'login':user.login,
                'type':'access',
                'exp':access_expiry
            }
        token = jwt.encode(
                payload,
                secret_key,
                algorithm='HS256'
            )
        return token , access_expiry
        
    def generate_refresh_token(self, user):

        secret_key = self._get_secret_key()
        refresh_expiry = datetime.utcnow() + timedelta(days=30)
        payload = {
                'uid': user.id,
                'login': user.login,
                'type': 'refresh',
                'exp': refresh_expiry,
            }

        token = jwt.encode(
                payload,
                secret_key,
                algorithm='HS256'
            )

        return token, refresh_expiry
        

    def generate_token_pair(self, user):
        access_token, access_expiry = self.generate_access_token(user)
        refresh_token, refresh_expiry = self.generate_refresh_token(user)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_expiry': access_expiry,
            'refresh_expiry': refresh_expiry,
        }
    
    def verify_access_token(self):
        authorization = request.httprequest.headers.get("Authorization")
        if not authorization:
            raise AccessDenied("Authorization header is missing.")
        if not authorization.startswith("Bearer "):
            raise AccessDenied("Invalid Authorization Header.")
        token = authorization.split(" ")[1]
        try:
            secret_key = self._get_secret_key()
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"]
            )

            if payload.get("type")!="access":
                raise AccessDenied("Invalid access token")
            user = self.env['res.users'].sudo().browse(payload.get("uid"))
            if not user.exists():
                raise AccessDenied("User not found")
            return user
        except jwt.ExpiredSignatureError:
            raise AccessDenied("Access token has expired.")

        except jwt.InvalidTokenError:
            raise AccessDenied("Invalid access token.")

        
    def verify_refresh_token(self, token):
        secret_key = self._get_secret_key()
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=['HS256']
        )

        if payload.get('type') != 'refresh':
            raise Exception('Invalid Refresh Token')

        return payload