# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class WebsiteConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    app_stop_subscribe = fields.Boolean('Stop Odoo Subscribe(Performance Improve)',
                                        help=u"Check to stop Odoo Subscribe function")

    def set_values(self):
        super(WebsiteConfig, self).set_values()
        select_type = self.env['ir.config_parameter'].sudo()
        if self.app_stop_subscribe:
            select_type.set_param('res.config.settings.app_stop_subscribe', self.app_stop_subscribe)
        else:
            select_type.set_param('res.config.settings.app_stop_subscribe', False)

    @api.model
    def get_values(self):
        res = super(WebsiteConfig, self).get_values()
        select_type = self.env['ir.config_parameter'].sudo()
        app_stop_subscribe = select_type.get_param('res.config.settings.app_stop_subscribe')

        res.update({'app_stop_subscribe': app_stop_subscribe})
        return res
