from odoo import fields, models, api


class UsersCustom(models.Model):
    _inherit = 'res.users'

    def archive_non_employees(self):
        users = self.search([('employee_ids', '=', False)])
        for user in users:
            if not user.has_group('security_groups.group_company_hc'):
                user.active = False
