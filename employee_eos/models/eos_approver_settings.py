from odoo import models, fields, api, _
import datetime
import calendar
from dateutil.relativedelta import relativedelta


class EOSSettings(models.Model):
    _name = 'eos.request.settings'
    _description = "End of Service Approval Settings"
    _order = 'id desc'

    name = fields.Char(string="Name")
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    approver_ids = fields.Many2many('res.users', 'eos_request_settings_user_rel', 'user_id', 'approver_id')
    approval_sequence = fields.One2many('eos.approval.sequence', 'related_eos_setting', 'Approval Sequence')
