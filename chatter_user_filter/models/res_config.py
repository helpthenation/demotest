# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    model_ids = fields.Many2many(comodel_name='ir.model', string="Models")

    def set_values(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:03/09/2020
        Func: for set config parameter
        :return:
        """
        super(ResConfigSettings, self).set_values()
        select_type = self.env['ir.config_parameter'].sudo()
        if self.model_ids:
            select_type.set_param('res.config.settings.model_ids', self.model_ids.ids)
        else:
            select_type.set_param('res.config.settings.model_ids', 'False')

    @api.model
    def get_values(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:03/09/2020
        Func: for get config parameter
        :return:
        """
        res = super(ResConfigSettings, self).get_values()
        select_type = self.env['ir.config_parameter'].sudo()
        model_ids = select_type.get_param('res.config.settings.model_ids')
        if model_ids != False:
            res.update({'model_ids': [(6, 0, eval(model_ids) or [])]})
        return res

    def clear_models(self):
        select_type = self.env['ir.config_parameter'].sudo()
        select_type.set_param('res.config.settings.model_ids', 'False')
