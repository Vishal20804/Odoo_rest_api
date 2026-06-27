# -*- coding: utf-8 -*-
"""
crud_controller.py
==================
Protected CRUD REST API — res.partner pe operate karta hai.
Sab routes JWT access token se protected hain.

Endpoints:
  GET    /api/v1/partners          → Sab partners list karo
  GET    /api/v1/partners/<id>     → Ek partner dekho
  POST   /api/v1/partners          → Naya partner banao
  PUT    /api/v1/partners/<id>     → Partner update karo
  DELETE /api/v1/partners/<id>     → Partner delete karo
"""

import logging
from odoo import http
from odoo.http import request
from .base_controller import JwtBaseController

_logger = logging.getLogger(__name__)


class PartnerCrudController(JwtBaseController):
    """Protected CRUD endpoints for res.partner."""

    # ─── LIST (GET ALL) ──────────────────────────────────────────────────────
    @http.route(
        '/api/v1/partners',
        type='json',
        auth='none',
        methods=['GET'],
        csrf=False,
        cors='*',
        save_session=False,
    )
    def list_partners(self, **kwargs):
        """
        Sab partners fetch karo (paginated).
        Query params: ?limit=10&offset=0&name=<search>
        Header: Authorization: Bearer <access_token>
        """
        try:
            payload, error = self._get_token_payload()
            if error:
                return error

            env = request.env(user=1)

            # Query params
            params = request.httprequest.args
            limit  = min(int(params.get('limit',  20)), 100)  # Max 100
            offset = int(params.get('offset', 0))
            name   = params.get('name', '').strip()

            domain = [('is_company', 'in', [True, False])]
            if name:
                domain.append(('name', 'ilike', name))

            partners = env['res.partner'].search(domain, limit=limit, offset=offset)
            total    = env['res.partner'].search_count(domain)

            data = []
            for p in partners:
                data.append({
                    'id'     : p.id,
                    'name'   : p.name,
                    'email'  : p.email  or '',
                    'phone'  : p.phone  or '',
                    'mobile' : p.mobile or '',
                    'street' : p.street or '',
                    'city'   : p.city   or '',
                    'country': p.country_id.name if p.country_id else '',
                    'company': p.is_company,
                })

            return self._success({
                'total'    : total,
                'limit'    : limit,
                'offset'   : offset,
                'partners' : data,
            })

        except Exception as e:
            _logger.exception("List Partners Error")
            return self._error(str(e), 500)

    # ─── GET ONE ─────────────────────────────────────────────────────────────
    @http.route(
        '/api/v1/partners/<int:partner_id>',
        type='json',
        auth='none',
        methods=['GET'],
        csrf=False,
        cors='*',
        save_session=False,
    )
    def get_partner(self, partner_id: int, **kwargs):
        """
        Ek specific partner fetch karo by ID.
        Header: Authorization: Bearer <access_token>
        """
        try:
            payload, error = self._get_token_payload()
            if error:
                return error

            env     = request.env(user=1)
            partner = env['res.partner'].browse(partner_id)

            if not partner.exists():
                return self._error(f"Partner id={partner_id} nahi mila", 404)

            return self._success({
                'id'          : partner.id,
                'name'        : partner.name,
                'email'       : partner.email        or '',
                'phone'       : partner.phone        or '',
                'mobile'      : partner.mobile       or '',
                'street'      : partner.street       or '',
                'street2'     : partner.street2      or '',
                'city'        : partner.city         or '',
                'zip'         : partner.zip          or '',
                'country'     : partner.country_id.name if partner.country_id else '',
                'is_company'  : partner.is_company,
                'website'     : partner.website      or '',
                'comment'     : partner.comment      or '',
            })

        except Exception as e:
            _logger.exception("Get Partner Error")
            return self._error(str(e), 500)

    # ─── CREATE ──────────────────────────────────────────────────────────────
    @http.route(
        '/api/v1/partners',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False,
        cors='*',
        save_session=False,
    )
    def create_partner(self, **kwargs):
        """
        Naya partner create karo.
        Body:
        {
          "name": "ABC Company",
          "email": "abc@test.com",
          "phone": "9876543210",
          "is_company": true,
          "city": "Ahmedabad"
        }
        Header: Authorization: Bearer <access_token>
        """
        try:
            payload, error = self._get_token_payload()
            if error:
                return error

            data = request.get_json_data()
            name = data.get('name', '').strip()

            if not name:
                return self._error("name required hai", 400)

            env = request.env(user=1)

            vals = {
                'name'      : name,
                'email'     : data.get('email',      ''),
                'phone'     : data.get('phone',      ''),
                'mobile'    : data.get('mobile',     ''),
                'street'    : data.get('street',     ''),
                'city'      : data.get('city',       ''),
                'zip'       : data.get('zip',        ''),
                'website'   : data.get('website',    ''),
                'comment'   : data.get('comment',    ''),
                'is_company': data.get('is_company', False),
            }

            # Country handle karo
            country_name = data.get('country', '').strip()
            if country_name:
                country = env['res.country'].search([('name', 'ilike', country_name)], limit=1)
                if country:
                    vals['country_id'] = country.id

            partner = env['res.partner'].create(vals)
            _logger.info("JWT CRUD: Partner created id=%d by user_id=%d", partner.id, payload['sub'])

            return self._success({
                'message'   : 'Partner successfully create ho gaya!',
                'partner_id': partner.id,
                'name'      : partner.name,
            }, 201)

        except Exception as e:
            _logger.exception("Create Partner Error")
            return self._error(str(e), 500)

    # ─── UPDATE ──────────────────────────────────────────────────────────────
    @http.route(
        '/api/v1/partners/<int:partner_id>',
        type='json',
        auth='none',
        methods=['PUT'],
        csrf=False,
        cors='*',
        save_session=False,
    )
    def update_partner(self, partner_id: int, **kwargs):
        """
        Existing partner update karo.
        Body: JSON with fields to update (partial update supported)
        Header: Authorization: Bearer <access_token>
        """
        try:
            payload, error = self._get_token_payload()
            if error:
                return error

            env     = request.env(user=1)
            partner = env['res.partner'].browse(partner_id)

            if not partner.exists():
                return self._error(f"Partner id={partner_id} nahi mila", 404)

            data          = request.get_json_data()
            allowed_fields = [
                'name', 'email', 'phone', 'mobile',
                'street', 'street2', 'city', 'zip',
                'website', 'comment', 'is_company',
            ]

            vals = {k: v for k, v in data.items() if k in allowed_fields}

            # Country
            country_name = data.get('country', '').strip()
            if country_name:
                country = env['res.country'].search([('name', 'ilike', country_name)], limit=1)
                if country:
                    vals['country_id'] = country.id

            if not vals:
                return self._error("Update karne ke liye koi valid field nahi di", 400)

            partner.write(vals)
            _logger.info("JWT CRUD: Partner id=%d updated by user_id=%d", partner_id, payload['sub'])

            return self._success({
                'message'   : 'Partner update ho gaya!',
                'partner_id': partner.id,
            })

        except Exception as e:
            _logger.exception("Update Partner Error")
            return self._error(str(e), 500)

    # ─── DELETE ──────────────────────────────────────────────────────────────
    @http.route(
        '/api/v1/partners/<int:partner_id>',
        type='json',
        auth='none',
        methods=['DELETE'],
        csrf=False,
        cors='*',
        save_session=False,
    )
    def delete_partner(self, partner_id: int, **kwargs):
        """
        Partner delete karo.
        Header: Authorization: Bearer <access_token>
        """
        try:
            payload, error = self._get_token_payload()
            if error:
                return error

            env     = request.env(user=1)
            partner = env['res.partner'].browse(partner_id)

            if not partner.exists():
                return self._error(f"Partner id={partner_id} nahi mila", 404)

            partner_name = partner.name
            partner.unlink()

            _logger.info("JWT CRUD: Partner '%s' (id=%d) deleted by user_id=%d",
                         partner_name, partner_id, payload['sub'])

            return self._success({
                'message': f"Partner '{partner_name}' delete ho gaya!",
            })

        except Exception as e:
            _logger.exception("Delete Partner Error")
            return self._error(str(e), 500)
