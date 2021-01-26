from odoo import models, fields, api, _


class EOSRequestApprover(models.Model):
    _name = 'eos.request.approver'
    _description = 'End of service  request approver'

    user_id = fields.Many2one('res.users', string="User", required=True)

    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new")

    end_of_service_id = fields.Many2one('end.of.service', string="Request", ondelete='cascade')
    reject_reason = fields.Char('Rejection Reason')
    sequence = fields.Integer('Sequence', default=10)
    approval_date = fields.Datetime(
        string='Approval Date',
        required=False, readonly=True)
    approval_category = fields.Char(string="Category")

    @api.onchange('user_id')
    def _onchange_approver_ids(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:18/11/2020
        :Func: for apply dynamic domain
        :return: domain dict
        """
        return {'domain': {'user_id': [('id', 'not in', self.end_of_service_id.approver_ids.mapped(
            'user_id').ids + self.end_of_service_id.request_owner_id.ids)]}}

    def _create_activity(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 18/11/2020
        :Func: this method use for the create schedule activity
        :Return: N/A
        """
        for approver in self:
            approver.end_of_service_id.activity_schedule(
                'employee_eos.mail_activity_data_employee_eos',
                user_id=approver.user_id.id)

    def _get_user_approval_activities(self, user, res_ids, activity_type_id):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 18/11/2020
        :Func: this method use for the  find activities
        :Return: activities
        """
        domain = [
            ('res_model', '=', 'end.of.service'),
            ('res_id', 'in', res_ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities


class EOSApprovalSequence(models.Model):
    _name = 'eos.approval.sequence'
    sequence = fields.Integer('Sequence', default=10)
    user_id = fields.Many2one('res.users', 'Approver')
    related_eos_setting = fields.Many2one('eos.request.settings', 'Related End Of Service Setting')
    approval_category = fields.Char(string="Category")
