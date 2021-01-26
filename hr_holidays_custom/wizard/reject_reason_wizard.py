from odoo import fields, models


class HrLeaveRefuseRequestWizard(models.TransientModel):
    _name = 'hr.leave.refuse.reason.wizard'
    _description = 'Reject Request'

    reject_reason = fields.Char('Reason', required=True)

    def process_to_reject(self):
        active_id = self._context.get('active_id')
        leave_refuse = self.env['hr.leave'].browse(active_id)
        if leave_refuse:
           return leave_refuse.with_context({'reason':self.reject_reason}).action_refuse()
