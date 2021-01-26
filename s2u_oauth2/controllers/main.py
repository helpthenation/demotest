# -*- coding: utf-8 -*-

from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
import logging
import werkzeug.urls
import werkzeug.utils
import requests
from odoo import http, _
from odoo.http import request

import json
import base64
import random
from passlib.context import CryptContext

_logger = logging.getLogger(__name__)


#############################
# Authentication Controller #
#############################


class MSLogin(OAuthLogin):

    # Function overwriten for OAuthLogin
    def list_providers(self):
        providers = super(MSLogin, self).list_providers()
        for provider in providers:
            if provider['name'] != 'Microsoft':
                continue
            msauth_state = base64.b64encode(request.session.db.encode())
            params = dict(
                scope=provider['scope'],
                response_type='code',
                client_id=provider['client_id'],
                redirect_uri=request.httprequest.url_root.replace('http:', 'https:') + 'auth_oauth/microsoft',
                state=msauth_state
            )
            provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))
        return providers

    @http.route('/auth_oauth/microsoft', type='http', auth='public', website=True)
    def signin(self, **kw):
        msauth_state = base64.b64encode(request.session.db.encode())
        if request.params.get('state').encode() != msauth_state:
            return request.render('http_routing.http_error', {
                'status_code': _('Bad Request'),
                'status_message': _('State check failed (1). Try again.')
            })

        if not request.params.get('code'):
            return request.render('http_routing.http_error', {
                'status_code': _('Bad Request'),
                'status_message': _(
                    'Expected "code" param in URL, but its not there. Try again. Or contact Administrator')
            })

        code = request.params.get('code')
        profile = self._validate(code)

        if not profile:
            return request.render('http_routing.http_error', {
                'status_code': _('Bad Request'),
                'status_message': _('Profile validation failed. Try again. Or contact Administrator')
            })

        # sure the user is authentic, but do they have a login for this DB? --> If user not exist in DB --> user is not allowed
        if 'userPrincipalName' not in profile:
            return request.render('http_routing.http_error', {
                'status_code': _('msauth'),
                'status_message': _('Your profile does not have an email')
            })

        # Set User login name
        login = profile['userPrincipalName']
        # Generate temp password so user can login
        password = self._ensure_password(login)

        # Check if password was set
        if not password:
            _logger.error("User %s tried to login but failed " % profile['userPrincipalName'])
            return request.render('http_routing.http_error', {
                'status_code': _('Bad Request'),
                'status_message': _(
                    'You (%s) are not authorized to access this page' % profile['userPrincipalName'])
            })

        # User has login and password, try to loggin
        login_uid = request.session.authenticate(request.session.db, login, password)
        if login_uid is False:
            return request.render('http_routing.http_error', {
                'status_code': _('Bad Request'),
                'status_message': _('You are not authorized to access this page')
            })

        # User logged in, set users token and refresh token
        request.env['auth.oauth.provider'].register_token(profile['access_token'],
                                                          profile.get('refresh_token', False),
                                                          profile['expires_in'])

        return set_cookie_and_redirect('/web')

    @http.route('/web/session/logout', type='http', auth="user")
    def logout(self, redirect='/web'):
        if 'msauth.id_token' in request.session:
            request.session.logout(keep_db=True)
            return http.local_redirect(
                "https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=" +
                request.httprequest.url_root + "/web"
            )
        else:
            request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    def _validate(self, authorization_code):
        # lookup the secret for the provider
        provider = request.env['auth.oauth.provider'].sudo().search([('name', '=', 'Microsoft')], limit=1)
        if not provider:
            _logger.error('No auth.oauth.provider found for Microsoft')
            return False
        # config may have changed during login process so we make sure we still have values we need
        if not (provider.client_id and provider.secret_key and provider.validation_endpoint):
            _logger.error('Content auth.oauth.provider changed for Microsoft')
            return False
        # exchange the authorization code for an access token
        post_data = {
            "grant_type": 'authorization_code',
            "code": authorization_code,
            "client_id": provider.client_id,
            "client_secret": provider.secret_key,
            "redirect_uri": request.httprequest.url_root.replace('http:', 'https:') + 'auth_oauth/microsoft'
        }

        access_token_response = requests.post(provider.validation_endpoint, data=post_data, verify=False)
        access_token_response.raise_for_status()

        try:
            data_oauth = json.loads(access_token_response.content)
        except Exception as e:
            _logger.error('failed decoding JSON response from %s: %s'
                          % (provider.validation_endpoint, json.dumps(e)))
            return False

        if 'access_token' not in data_oauth:
            _logger.error('MSAuth expected id_token to be returned from %s' % provider.validation_endpoint)
            _logger.error(data_oauth)
            return False

        # we have a token we can now use
        # call method which can be used by other modules to do something with the tokens
        # # Call this after!! --> Otherwise Public user gets the token and refresh_token. And not the user who is trying to login.
        # request.env['auth.oauth.provider'].register_token(data['access_token'],
        #                                                   data.get('refresh_token', False),
        #                                                   data['expires_in'])

        graph_data = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': 'Bearer ' + data_oauth['access_token']})
        data_me = json.loads(graph_data.content)

        if 'error' in data_me:
            _logger.error('Error returned in json response: %s' % data_me.get('error'))
            return False

        # Create data record of the retruned data of MS So, if the users is able to login, data is stored with the correct user
        data = {'access_token': data_oauth.get('access_token', False),
                'expires_in': data_oauth.get('expires_in', False),
                'refresh_token': data_oauth.get('refresh_token', False),
                'userPrincipalName': data_me.get('userPrincipalName', False)}
        return data

    def _ensure_password(self, login):
        # get the id as variant value for the encrypted password
        # this way we also ensure the user's login even exists
        odoo_user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        if not odoo_user:
            param = request.env['ir.config_parameter'].sudo().search(
                [('key', '=', 's2u_msaccount')], limit=1)

            if param and param.value.lower() == 'true':
                # Creating user (no password yet)
                user_vals = {
                    'name': login,
                    'login': login
                }
                odoo_user = request.env['res.users'].sudo().create(user_vals)
                employee = request.env['hr.employee'].sudo().search([('work_email', 'ilike', login)], limit=1)
                if employee:
                    employee.user_id = odoo_user.id
                else:
                    if not odoo_user.has_group('security_groups.group_company_hc'):
                        return False
            else:
                return False
        if odoo_user:
            if not odoo_user.employee_id and not odoo_user.has_group('security_groups.group_company_hc'):
                _logger.error("You are not authorized to access this page")
                return False

        # generate a temporary hashed password and set it in the database
        tmp_password = '%032x' % random.getrandbits(128)
        # paradigm from odoo.addons.auth_crypt.models.res_users
        encrypted = CryptContext(['pbkdf2_sha512']).encrypt(tmp_password)
        request.env.cr.execute(
            "UPDATE res_users SET password=%s WHERE id=%s",
            (encrypted, odoo_user.id))
        request.env.cr.commit()
        # we can now login with this temporary password
        return tmp_password
