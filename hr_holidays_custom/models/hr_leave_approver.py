# -*- coding: utf-8 -*-


from odoo import fields, models, api


class HrLeaveApprover(models.Model):
    _name = "hr.leave.approver"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Leave Approver"
    _rec_name = 'time_off_id'

    time_off_id = fields.Many2one('hr.leave', string='TimeOff')
    approver = fields.Many2one('res.users', string='Approver')
    decision_date = fields.Datetime(string='Decision Date')
    status = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
         ('rejected', 'Rejected'), ('withdraw_approved', 'Withdraw Approved')], string='Status', default='draft')
    rejection_reason = fields.Char(string='Reject Reason')
    state = fields.Selection(related='time_off_id.state')
    sequence = fields.Integer('Sequence', default=1)
    approve_tag = fields.Boolean(default=False)

    # def _create_activity(self):
    #     for approver in self:
    #         approver.activity_schedule(
    #             'hr_holidays_custom.mail_activity_data_time_off_request',
    #             user_id=approver.approver.id)
