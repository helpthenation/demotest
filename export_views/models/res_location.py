# -*- coding: utf-8 -*-

from odoo import models, fields


class CompanyLocation(models.Model):
    _name = 'company.location'

    location_name = fields.Char(string="Name")
    company_m2o = fields.Many2one('res.company', string="Company")
    location_city_id = fields.Many2one('res.city', string="City")
    emirate_name_id = fields.Many2one('res.country.state', string="Emirate Name")
    location_country_id = fields.Many2one('res.country', string="Country")
    location_address = fields.Char(string="Address")
    location_phone = fields.Char(string='Phone Number')
    location_code = fields.Char(string='Location Code')


class ResCompany(models.Model):
    _inherit = 'res.company'

    location_ids = fields.One2many('company.location', 'company_m2o')
