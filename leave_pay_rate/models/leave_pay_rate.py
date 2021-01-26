from odoo import models, fields, api, _


class LeavePayRate(models.Model):
    _name = 'leave.pay.rate'

    name = fields.Char(string="Name")
    days = fields.Integer(string="Days")
    # uom = fields.Many2one('uom.uom', 'Unit of Measure')
    uom = fields.Selection([('calendar_days', 'Calendar Days'), ('working_days', 'Working Days')],
                           string="Unit of Measure")
    pay_rate = fields.Selection([
        ('full_pay', 'Full Pay'),
        ('half_pay', 'Half Pay'), ('no_pay', 'No Pay')], string="Pay Rate", default="full_pay", required=True)
