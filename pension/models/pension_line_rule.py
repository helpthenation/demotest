# -*- coding: utf-8 -*-

from odoo import models, fields


class PensionLineRule(models.Model):
    _name = 'pension.line.rule'
    _description = 'Pension Line Rule'
    _rec_name = 'pension_id'

    pension_id = fields.Many2one('pension.rule', string='Pension')
    share = fields.Selection([('employee', 'Employee'), ('company', 'Company')], string='Share')
    percentage = fields.Float(string='Percentage')
    detail = fields.Selection(
        [('fixed_amount', 'Fixed Amount'), ('total_salary', 'Total Salary'), ('component', 'Component')],
        string='Details')
    fixed_amount = fields.Float(string='Fixed Amount')
    component = fields.Many2one('hr.compensation.pay.component', string='Component')
    component_name = fields.Char(related='component.description')
    component_percentage = fields.Float(string='Component Percentage')
