# -*- coding: utf-8 -*-
from odoo import http

# class QiaTheme(http.Controller):
#     @http.route('/qia_theme/qia_theme/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/qia_theme/qia_theme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('qia_theme.listing', {
#             'root': '/qia_theme/qia_theme',
#             'objects': http.request.env['qia_theme.qia_theme'].search([]),
#         })

#     @http.route('/qia_theme/qia_theme/objects/<model("qia_theme.qia_theme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('qia_theme.object', {
#             'object': obj
#         })