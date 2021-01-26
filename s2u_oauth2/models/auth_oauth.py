# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
import logging
import requests
import json

from odoo import fields, models, api
from odoo.http import request


_logger = logging.getLogger(__name__)


class AuthOAuthProvider(models.Model):

    _inherit = 'auth.oauth.provider'

    # Add secret_key for Microsoft
    secret_key = fields.Char(string='Secret Key')

    @api.model
    def register_token(self, token, refresh_token, expires_in_seconds, set_session=True):
        # method you can overwrite to do something with the tokens
        # returns dict {access_token, refresh_token, expiration}

        if set_session:
            request.session['msauth.id_token'] = token
            request.session['msauth.refresh_token'] = refresh_token

        res = {
            'access_token': token,
            'refresh_token': refresh_token,
        }
        if expires_in_seconds:
            expires_in = datetime.now() + timedelta(minutes=expires_in_seconds / 60)
            if set_session:
                request.session['msauth.expires_in'] = expires_in
            res['expiration'] = expires_in

        return res

    @api.model
    def refresh_token(self, refresh_token, set_session=True):
        if not request.session.get('msauth.refresh_token'):
            _logger.error('No msauth.refresh_token present')
            return False
        provider = self.sudo().search([('name', '=', 'Microsoft')], limit=1)
        if not provider:
            _logger.error('No auth.oauth.provider found for Microsoft')
            return False
        if not (provider.client_id and provider.secret_key and provider.validation_endpoint):
            _logger.error('Content auth.oauth.provider changed for Microsoft')
            return False

        post_data = {
            "grant_type": 'refresh_token',
            "refresh_token": refresh_token,
            "client_id": provider.client_id,
            "client_secret": provider.secret_key,
        }

        refresh_token_response = requests.post(provider.validation_endpoint, data=post_data, verify=False)
        refresh_token_response.raise_for_status()

        try:
            data = json.loads(refresh_token_response.content)
        except Exception as e:
            _logger.error('failed decoding JSON response from %s: %s' % (provider.validation_endpoint, json.dumps(e)))
            return False

        if 'access_token' not in data:
            _logger.error('MSAuth expected id_token to be returned from %s' % provider.validation_endpoint)
            return False

        self.register_token(data['access_token'],
                            data.get('refresh_token', False),
                            data['expires_in'],
                            set_session=set_session)

        return data.get('refresh_token', False)
