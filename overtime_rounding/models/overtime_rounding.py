# -*- coding: utf-8 -*-
from odoo.exceptions import Warning

from odoo import models, fields, api


class OvertimeRounding(models.Model):
    _name = 'overtime.rounding'
    _description = 'Overtime Rounding'
    _rec_name = 'from_minute'

    from_minute = fields.Float(string="From Minute")
    to_minute = fields.Float(string="To Minute")
    rounded_off = fields.Float(string="Rounded Off to", compute="_compute_rounded_off_to")

    @api.depends('from_minute', 'to_minute')
    def _compute_rounded_off_to(self):
        for rec in self:
            if rec.from_minute and rec.to_minute:
                if not rec.from_minute < rec.to_minute:
                    raise Warning('To Minutes time must be greater then From minutes time')
                to_minute = str(rec.to_minute).split('.')
                if len((to_minute[1])) == 1:
                    to_minute = int(str(to_minute[1] + "0"))
                else:
                    to_minute = int(to_minute[1][:2])
                if to_minute <= 12:
                    rec.rounded_off = 0.0
                elif to_minute >= 13 and to_minute <= 38:
                    rec.rounded_off = 0.25
                elif to_minute >= 40 and to_minute <= 62:
                    rec.rounded_off = 0.50
                elif to_minute >= 63 and to_minute <= 89:
                    rec.rounded_off = 0.75
                elif to_minute >= 90 and to_minute <= 100:
                    rec.rounded_off = 1.00
            else:
                rec.rounded_off = 0.0

