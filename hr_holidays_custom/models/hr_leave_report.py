# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.osv import expression


class LeaveReport(models.Model):
    _inherit = "hr.leave.report"

    category = fields.Selection(related='holiday_status_id.category', string='Category')

    @api.model
    def action_time_off_analysis(self):
        domain = [('holiday_type', '=', 'employee')]
        domain = expression.AND([
            domain,
            [('employee_id', 'in', self.env.context.get('active_ids', []))]
        ])
        domain = expression.AND([
            domain,
            [('category', '=', 'annual')]
        ])
        return {
            'name': _('Time Off Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.report',
            'view_mode': 'tree,form,pivot',
            'search_view_id': self.env.ref('hr_holidays.view_hr_holidays_filter_report').id,
            'domain': domain,
            'context': {
                'search_default_group_type': True,
                'search_default_year': True
            }
        }
