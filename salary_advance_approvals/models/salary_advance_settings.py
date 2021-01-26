from odoo import fields, models, api, _
from datetime import datetime as datetime
from odoo.exceptions import UserError, ValidationError


class SalaryAdvanceSettings(models.Model):
    _name = 'salary.advance.settings'

    name = fields.Char(string="Name")
    num_of_yearly_request = fields.Integer(string="Number of Yearly Request")
    contract_subgroup_ids = fields.Many2many('hr.contract.subgroup', string="Contract Subgroups", copy=True)
    deadline_month_day = fields.Integer(string="Request limit day of month", default=10)
    active = fields.Boolean('Active', default=True)
    bypass_employee_ids = fields.Many2many('hr.employee', string="Bypass Rule Employees", copy=True)

    @api.model
    def create(self, vals):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date: 02/10/2020
        :Func:supper all for the ir.sequence
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('salary.advance.settings') or _('New')
        res = super(SalaryAdvanceSettings, self).create(vals)
        return res

    def find_advance_salary_rule(self, contract_subgroup):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date: 02/10/2020
        :Func:This method use for the find salary rule
        base on the  employee contract subgroups and return the first salary rule
        :Return: Salary Rule or the  UserError
        """
        salary_advance_rule = self.env['salary.advance.settings']
        salary_advance_settings = self.env['salary.advance.settings'].search([])
        for salary_advance_setting in salary_advance_settings:
            for subgroup in salary_advance_setting.contract_subgroup_ids:
                if subgroup in contract_subgroup:
                    salary_advance_rule += salary_advance_setting
        if not salary_advance_rule or not salary_advance_settings:
            default_rule = salary_advance_settings.filtered(lambda s: not s.contract_subgroup_ids)
            if default_rule:
                salary_advance_rule = default_rule
        if not salary_advance_rule:
            raise UserError(_(
                "Advance Salary Settings was not found please configure the Advance Salary Settings \n"
                "Approval->Configuration-> Advance Salary Settings"))
        return salary_advance_rule[0]
