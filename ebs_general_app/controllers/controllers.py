# -*- coding: utf-8 -*-
# from odoo import http


# class EbsGeneralApp(http.Controller):
#     @http.route('/ebs_general_app/ebs_general_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ebs_general_app/ebs_general_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ebs_general_app.listing', {
#             'root': '/ebs_general_app/ebs_general_app',
#             'objects': http.request.env['ebs_general_app.ebs_general_app'].search([]),
#         })

#     @http.route('/ebs_general_app/ebs_general_app/objects/<model("ebs_general_app.ebs_general_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ebs_general_app.object', {
#             'object': obj
#         })
