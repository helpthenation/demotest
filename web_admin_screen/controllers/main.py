# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


#
# _logger = logging.getLogger(__name__)


class WebAdminScreen(http.Controller):

    @http.route('/web/admin', type='http', auth="none", website=True)
    def web_admin_login(self, redirect=None, **kw):

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        if values.get('login'):
            login = values.get('login')
            user = request.env['res.users'].search([('login', '=', login)])
            if user:
                if not user.employee_id and not user.has_group('security_groups.group_company_hc'):
                    values['error'] = _(
                        "You are not allowed to access this database. Please contact the system's administrator.")
                    response = http.request.render('web_admin_screen.web_admin', values)
                    return response
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')
        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = http.request.render('web_admin_screen.web_admin', values)
        response.qcontext.update(self.get_auth_signup_config())
        # response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _login_redirect(self, uid, redirect=None):
        return redirect if redirect else '/web'

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
        }
