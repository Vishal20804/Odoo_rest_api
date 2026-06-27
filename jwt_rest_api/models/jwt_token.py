from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class JwtToken(models.Model):
    _name        = 'jwt.token'
    _description = 'JWT Token Store'
    _order       = 'create_date desc'
    _rec_name    = 'user_id'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
    )
    access_token = fields.Text(
        string='Access Token',
        
    )
    refresh_token = fields.Text(
        string='Refresh Token',
        required=True,
    )
    access_expires_at = fields.Datetime(
        string='Access Token Expires At',
        required=True,
    )
    refresh_expires_at = fields.Datetime(
        string='Refresh Token Expires At',
        required=True,
    )
    is_revoked = fields.Boolean(
        string='Revoked?',
        default=False,
        index=True,
    )
    last_used = fields.Datetime(
        string='Last Used',
        readonly=True,
    )
    ip_address = fields.Char(
        string='Client IP',
        readonly=True,
    )
    user_agent = fields.Char(
        string='User Agent',
        readonly=True,
    )
    secret_key = fields.Char(string="Secret Key")
    
    access_token_status = fields.Selection(
        selection=[
            ('active',  'Active'),
            ('expired', 'Expired'),
            ('revoked', 'Revoked'),
        ],
        string='Access Status',
        compute='_compute_token_status',
    )
    refresh_token_status = fields.Selection(
        selection=[
            ('active',  'Active'),
            ('expired', 'Expired'),
            ('revoked', 'Revoked'),
        ],
        string='Refresh Status',
        compute='_compute_token_status',
    )

    @api.depends('access_expires_at', 'refresh_expires_at', 'is_revoked')
    def _compute_token_status(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.is_revoked:
                rec.access_token_status  = 'revoked'
                rec.refresh_token_status = 'revoked'
            else:
                rec.access_token_status  = 'active' if rec.access_expires_at  and rec.access_expires_at  > now else 'expired'
                rec.refresh_token_status = 'active' if rec.refresh_expires_at and rec.refresh_expires_at > now else 'expired'


