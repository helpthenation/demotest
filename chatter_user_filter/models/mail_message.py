from odoo import _, api, fields, models, modules, tools


class Message(models.Model):
    _inherit = 'mail.message'

    def message_format(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:03/09/2020
        Func: This method use for the hide log note base on the group and the configuration of general setting
        :return:res
        """
        employee_group = False
        select_type = self.env['ir.config_parameter'].sudo()
        model_ids = select_type.get_param('res.config.settings.model_ids') and self.env['ir.model'].browse(
            eval(select_type.get_param('res.config.settings.model_ids')))
        for message in self:
            if model_ids and message.model in model_ids.mapped('model'):
                if self.env.user.has_group('security_groups.group_company_employee'):
                    employee_group = True
                elif self.env.user.has_group('security_groups.group_hc_employee'):
                    employee_group = False
                if employee_group and message.author_id != self.env.user.partner_id:
                    self = self - message
        res = super(Message, self).message_format()
        return res
