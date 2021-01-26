from odoo import models, fields, api, _


class EmployeeTravelRequest(models.Model):
    _inherit = 'employee.travel.request'

    @api.onchange('request_owner_id')
    def onchange_employee(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        if self.env.user.has_group('security_groups.group_company_hc'):
            employees = self.env['hr.employee'].search([])
            return {'domain': {'employee_id': [('id', 'in', employees.ids)]}}

        elif self.env.user.has_group('security_groups.group_company_employee'):
            if self.env.user.employee_id:
                return {'domain': {'employee_id': [('id', '=', self.env.user.employee_id.id)]}}
            else:
                return {'domain': {'employee_id': [('id', 'in', [-1])]}}
        elif self.env.user.has_group('roles_segregation.group_hc_compensation_and_benefits'):
            if self.env.user.employee_id:
                return {'domain': {'employee_id': [('id', '=', self.env.user.employee_id.id)]}}
            else:
                return {'domain': {'employee_id': [('id', 'in', [-1])]}}
        else:
            return {'domain': {'employee_id': [('id', 'in', [-1])]}}
