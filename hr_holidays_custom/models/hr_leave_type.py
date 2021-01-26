# -*- coding: utf-8 -*-


from odoo import fields, models


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"
    _description = "Leave Type"

    approver_ids = fields.One2many('hr.leave.type.approver', 'leave_type_id', string='Approvers')
    category = fields.Selection(
        [('sick', 'Sick'), ('annual', 'Annual'), ('maternity', 'Maternity'), ('paternity', 'Paternity')],
        string='Category')
    validation_type = fields.Selection(selection_add=[('static_approvers', 'Static Approvers')])
    attachment_required = fields.Boolean(string="Attachment Required")
