# -*- coding: utf-8 -*-
{
    'name': 'JWT REST API Authentication',
    'version': '19.3.1.0.0',
    'category': 'Technical',
    'summary': 'Inbound REST API with JWT Auth - Login, Signup, CRUD, Token Refresh',
    'author': 'Vishal Sharma',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/jwt_token_views.xml',
        'views/jwt_menu.xml',
        'data/jwt_secret_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
