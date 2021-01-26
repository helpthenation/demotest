# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    absher_flag = fields.Image(string='Absher Flag')
    pension_id_number = fields.Char(string="Pension Id Number")
    emp_military_service_start_date = fields.Date(string="Military Service Start Date")
    emp_military_service_end_date = fields.Date(string="Military Service End Date")
    emp_military_service_title = fields.Char(string="Military Service Title")
    emp_military_service_country = fields.Many2one('res.country', string="Military Service Country")
