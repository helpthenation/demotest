# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    xls_cron_path = fields.Char(
        string='Cron output files path',
        required=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        select_type = self.env['ir.config_parameter'].sudo()
        if self.xls_cron_path:
            select_type.set_param('res.config.settings.xls_cron_path', self.xls_cron_path)
        else:
            select_type.set_param('res.config.settings.xls_cron_path', False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        select_type = self.env['ir.config_parameter'].sudo()
        xls_cron_path = select_type.get_param('res.config.settings.xls_cron_path')
        if xls_cron_path != False:
            res.update({'xls_cron_path': xls_cron_path})
        return res
