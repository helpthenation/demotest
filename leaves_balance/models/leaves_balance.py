from odoo import models, fields, api, _


class LeavesBalance(models.Model):
    _name = 'leaves.balance'

    name = fields.Char(string="Name")
    job_grade = fields.Many2one('job.grade', string="Job Grade")
    uom = fields.Selection([('calendar_days', 'Calendar Days'), ('working_days', 'Working Days')],
                           string="Unit of Measure")
    yearly_balance = fields.Float(string="Yearly Balance")
    daily_balance = fields.Float(string="Daily Balance", compute='_compute_daily_balance', store=True)
    monthly_balance = fields.Float(string="Monthly Balance", compute='_compute_monthly_balance', store=True)
    contract_subgroups = fields.Many2many(
        comodel_name='hr.contract.subgroup',
        string='Contract Subgroups')

    @api.depends('yearly_balance')
    def _compute_monthly_balance(self):
        """
        @Author:Bhavesh Jadav TechUltra solution
        @Date : 19/10/2020
        @Func: For Calculate the Monthly Balance from the yearly balance
        """
        for rec in self:
            rec.monthly_balance = rec.yearly_balance / 12 or 0.0
        return True

    @api.depends('monthly_balance')
    def _compute_daily_balance(self):
        """
        @Author:Bhavesh Jadav TechUltra solution
        @Date : 19/10/2020
        @Func: For Calculate the daily Balance from the monthly  balance
        """
        for rec in self:
            rec.daily_balance = rec.monthly_balance / 30 or 0.0
        return True
