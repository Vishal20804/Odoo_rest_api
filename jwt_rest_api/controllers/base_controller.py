# -*- coding: utf-8 -*-
"""
base_controller.py
==================
Sab controllers ka base class.
Common methods:
  - _get_token_payload()  → Authorization header se token extract + verify karo
  - _success()            → Consistent success response
  - _error()              → Consistent error response
"""

import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class JwtBaseController(http.Controller):
    """
    Base controller with JWT helper methods.
    Sab JWT controllers is class ko inherit karenge.
    """

    def _success(self, data: dict, status: int = 200) -> dict:
        """
        Standard success response format:
        {
          "status": "success",
          "code": 200,
          "data": { ... }
        }
        """
        return {
            'status': 'success',
            'code'  : status,
            'data'  : data,
        }

    def _error(self, message: str, code: int = 400) -> dict:
        """
        Standard error response format:
        {
          "status": "error",
          "code": 400,
          "message": "..."
        }
        """
        _logger.warning("JWT API Error [%d]: %s", code, message)
        return {
            'status' : 'error',
            'code'   : code,
            'message': message,
        }

    def _get_token_payload(self, expected_type: str = 'access'):
        """
        Request headers se Authorization token nikalo aur verify karo.

        Returns:
            (payload_dict, None)   → success
            (None, error_response) → failure

        Usage in child controller:
            payload, error = self._get_token_payload()
            if error:
                return error
            user_id = payload['sub']
        """
        auth_header = request.httprequest.headers.get('Authorization', '')

        # Header format: "Bearer <token>"
        if not auth_header.startswith('Bearer '):
            return None, self._error(
                "Authorization header missing ya galat format hai. "
                "Expected: 'Bearer <token>'", 401
            )

        token = auth_header[len('Bearer '):].strip()

        if not token:
            return None, self._error("Token empty hai", 401)

        try:
            env     = request.env(user=1)
            payload = env['jwt.utils'].verify_token(token, expected_type=expected_type)

            # Extra check: kya yeh token DB me revoke nahi hai?
            # (Sirf access token ke liye check karte hain)
            if expected_type == 'access':
                token_record = env['jwt.token'].search([
                    ('user_id',      '=', payload['sub']),
                    ('access_token', '=', token),
                    ('is_revoked',   '=', False),
                ], limit=1)
                if not token_record:
                    return None, self._error("Token revoke ho chuka hai ya valid nahi hai", 401)

                # Last used update karo
                token_record.write({'last_used': __import__('odoo').fields.Datetime.now()})

            return payload, None

        except ValueError as ve:
            return None, self._error(str(ve), 401)
        except Exception as e:
            _logger.exception("Token verification unexpected error")
            return None, self._error("Token verification failed", 500)
