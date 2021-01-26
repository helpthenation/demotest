from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # iban = fields.Char(string="IBAN NO.")
    current_account_number = fields.Char(string='Current Account Number', compute='_compute_bank_details',
                                         readonly=True)
    current_bank_name = fields.Many2one('res.bank', string='Current Bank Name', readonly=True,
                                        compute='_compute_bank_details')
    iban = fields.Char(string="IBAN NO.", compute='_compute_bank_details')

    def _compute_bank_details(self):
        details = self.bank_history_ids
        if details:
            if len(details) == 1:
                self.current_bank_name = details.current_bank_name.id or ''
                self.iban = details.current_iban or ''
                self.current_account_number = details.current_account_number or ''
            elif len(details) > 1:
                last_rec = (len(details) - 1)
                self.current_bank_name = details[last_rec].current_bank_name.id or ''
                self.iban = details[last_rec].current_iban or ''
                self.current_account_number = details[last_rec].current_account_number or ''
        else:
            self.current_account_number = ''
            self.iban = ''
            self.current_bank_name = False
            return
