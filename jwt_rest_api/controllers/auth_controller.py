from odoo import http 
from odoo.http import request
import json

class AuthController(http.Controller):
    @http.route('/api/signup',type='json',auth='public',methods=['POST'],csrf=False)
    def signup(self,**kwargs):
        name = kwargs.get('name')
        login = kwargs.get('login')
        password = kwargs.get('password')

        if not name:
            return{
                'success':False,
                'message':'Name is required',
            }
        if not login:
            return {
                'success': False,
                'message': 'Login is required'
            }

        if not password:
            return {
                'success': False,
                'message': 'Password is required'
            }
        existing_user = request.env['res.users'].sudo().search(
            [('login','=',login)],
            limit=1
        )
        if existing_user:
            return{
                'success':False,
                'message':'User Already Exists'
            }
        user = request.env['res.users'].sudo().create({
            'name': name,
            'login': login,
            'password': password,
        })

        return {
            'success': True,
            'message': 'User created successfully',
            'data': {
                'user_id': user.id,
                'name': user.name,
                'login': user.login,
            }
        }
    
    @http.route('/api/login',type='json',auth='public',methods=['POST'],csrf=False)
    def login(self,**kwargs):
        login = kwargs.get('login')
        password = kwargs.get('password')

        if not login:
            return {
                'success': False,
                'message': 'Login is required'
            }

        if not password:
            return {
                'success': False,
                'message': 'Password is required'
            }
        
        try :
            auth_info = request.env['res.users'].sudo().authenticate(
                credential={
                    'login': login,
                    'password': password,
                    'type': 'password',
                },
                user_agent_env=request.httprequest.environ,
            )
            uid = auth_info['uid']
            if not uid:
                return{
                    'success':False,
                    'message':'Invalid Credentials'
                }
            user = request.env['res.users'].sudo().browse(uid)
            jwt_service = request.env['jwt.config'].sudo()
            tokens = jwt_service.generate_token_pair(user)

            request.env['jwt.token'].sudo().create({
                'user_id': user.id,
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'access_expires_at': tokens['access_expiry'],
                'refresh_expires_at': tokens['refresh_expiry'],
                'ip_address': request.httprequest.remote_addr,
                'user_agent': request.httprequest.headers.get('User-Agent'),
            })

            return {
                'success': True,
                'message': 'Login Successful',
                'data': {
                    'user_id': user.id,
                    'name': user.name,
                    'access_token': tokens['access_token'],
                    'refresh_token': tokens['refresh_token'],
                    'access_expires_at': tokens['access_expiry'],
                    'refresh_expires_at': tokens['refresh_expiry'],
                }
            }

        except Exception as e:
            return{
                'success':False,
                'message':str(e)
            }