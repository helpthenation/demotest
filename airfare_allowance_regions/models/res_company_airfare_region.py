# -*- coding: utf-8 -*-

from odoo import models, fields


class AirfareAllowanceRegions(models.Model):
    _name = 'airfare.allowance.regions'
    _description = 'Airfare Allowance Regions'

    name = fields.Char()
    country_group_ids = fields.Many2many('res.country', 'res_country_res_airfare_region_rel',
                                         'airfare_region_id', 'res_country_group_id', string='Country Groups')
    allowance = fields.One2many('airfare.allowance', 'region', string='Allowance')
