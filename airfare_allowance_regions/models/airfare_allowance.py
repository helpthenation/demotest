# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AirfareAllowanceRegions(models.Model):
    _name = 'airfare.allowance'
    _description = 'Airfare Allowance'
    _rec_name = 'region'

    grade_ids = fields.Many2many('job.grade', string="Grades")
    type = fields.Selection([('adult', 'Adult'), ('child', 'Child'), ('infant', 'Infant')], string='Type')
    yearly_amount = fields.Float(string='Yearly Amount')
    monthly_amount = fields.Float(string='Monthly Amount', compute='_compute_monthly_amount')
    region = fields.Many2one('airfare.allowance.regions', string='Region')
    class_of_travel = fields.Selection(
        selection=[('economy_class', 'Economy Class'), ('premium_economy_class', 'Premium Economy Class'),
                   ('business_class', 'Business Class')])

    @api.depends('yearly_amount')
    def _compute_monthly_amount(self):
        for rec in self:
            if rec.yearly_amount:
                rec.monthly_amount = rec.yearly_amount / 12
            else:
                rec.monthly_amount = 0.0
