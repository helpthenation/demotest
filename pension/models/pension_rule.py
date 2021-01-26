# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PensionRule(models.Model):
    _name = 'pension.rule'
    _description = 'Pension Rule'

    name = fields.Char('Name')
    country_id = fields.Many2one('res.country', string='Country')
    contract_subgroups_id = fields.Many2one('hr.contract.subgroup', string="Contract Subgroup")
    lines_ids = fields.One2many('pension.line.rule', 'pension_id', string='Pension Rule Lines')
    from_date = fields.Date(
        string='From Date',
        required=False)
    to_date = fields.Date(
        string='To Date',
        required=False)
