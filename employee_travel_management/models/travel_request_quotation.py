from odoo import models, fields, api, _


class EmployeeTravelRequest(models.Model):
    _name = 'travel.request.quotation'
    _description = 'Travel Request quotation'
    _order = 'id desc'

    @api.model
    def default_get(self, fields):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:25/11/2020
        :Func:For set class_of_travel when open form view
        """
        res = super(EmployeeTravelRequest, self).default_get(fields)
        if self._context.get('perdiem_rule') and 'class_of_travel' in fields:
            rule = self.env['travel.perdiem.rule'].browse(self._context.get('perdiem_rule'))
            res.update({'class_of_travel': rule.class_of_travel})
        return res

    name = fields.Char(string="Name")
    travel_request_id = fields.Many2one('employee.travel.request', string="Travel Request")
    travel_agency_id = fields.Many2one('res.partner', string="Agency")
    flight_no = fields.Char(string="Flight No.")
    boarding_time = fields.Datetime(string="Boarding Time")
    value_cost = fields.Monetary(string="Value Cost", currency_field='currency_id')
    markup_amount = fields.Monetary(string="Markup Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    car_rental_days = fields.Float(string='Car Rental Days', required=False)
    car_rental_amount = fields.Monetary(string="Car Rental Amount", currency_field='currency_id')
    hotel_accommodation_days = fields.Float(string='Hotel Accommodation Days', required=False)
    hotel_accommodation_amount = fields.Monetary(string="Hotel Accommodation Amount", currency_field='currency_id')
    class_of_travel = fields.Selection(
        selection=[('economy_class', 'Economy Class'), ('premium_economy_class', 'Premium Economy Class'),
                   ('business_class', 'Business Class')])

    @api.onchange('travel_request_id')
    def onchange_travel_agency(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        travel_agency_list = self.travel_request_id.travel_settings_id.travel_agency_ids.ids
        return {'domain': {'travel_agency_id': [('id', 'in', travel_agency_list)]}}

    @api.model
    def create(self, vals):
        """
        :Author: Bhavesh Jadav TechUltra Solutions
        :Date: 12/10/2020
        :Func: inherit for the add name of the quotation
        :Return : Result of the supper call
        """
        name = self.env['ir.sequence'].next_by_code('travel.request.quotation') or _('New')
        vals['name'] = name
        res = super(EmployeeTravelRequest, self).create(vals)
        return res
