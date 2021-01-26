# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ReportRequest(models.Model):
    _inherit = 'report.request'

    @api.onchange('company_id')
    def onchange_employee(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        if self.env.user.has_group('security_groups.group_hc_employee'):
            employees = self.env['hr.employee'].search([])
            self.employee_id = self.env.user.employee_id.id
            self.bank_id = self.env.user.employee_id.current_bank_name.id
            return {'domain': {'employee_id': [('id', 'in', employees.ids)]}}

        elif self.env.user.has_group('security_groups.group_company_employee') or self.env.user.has_group(
                'roles_segregation.group_hc_compensation_and_benefits'):
            if self.env.user.employee_id:
                self.employee_id = self.env.user.employee_id.id
                self.bank_id = self.env.user.employee_id.current_bank_name.id
                return {'domain': {'employee_id': [('id', '=', self.env.user.employee_id.id)]}}
            else:
                # if the login user are not employee and the is in employee group then its blank
                return {'domain': {'employee_id': [('id', 'in', [-1])]}}
        else:
            return {'domain': {'employee_id': [('id', 'in', [-1])]}}
