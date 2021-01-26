# -*- coding: utf-8 -*-
from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_encash_leave(self, contract):
        """
        This method will calculate encase leave for the different employees
        :param contract: contract id of the employee
        :return: encase leave amount
        Nimesh Jadav : 25 Nov 2020
        """
        if contract:
            allocations = self.env['hr.leave.allocation'].search([('employee_id', '=', contract.employee_id.id)])
            amount = 0
            for allocation in allocations:
                for compensation in contract.related_compensation:
                    if compensation.code == '1000':
                        basic = compensation.amount
                if allocation.encash_leave > 0:
                    amount += (basic / 30 * allocation.encash_leave)
            return amount

    def action_payslip_done(self):
        """
            clear Encase leave
        """
        res = super(HrPayslip, self).action_payslip_done()
        for employee in self:
            allocations = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', employee.contract_id.employee_id.id)])
            for allocation in allocations:
                allocation.encash_leave = 0.0
        return res
