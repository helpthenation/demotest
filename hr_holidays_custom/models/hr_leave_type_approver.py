# -*- coding: utf-8 -*-


from odoo import fields, models, api


class HrLeaveTypeApprover(models.Model):
    _name = "hr.leave.type.approver"
    _description = "Leave Type Approver"

    leave_type_id = fields.Many2one("hr.leave.type", string="Leave Type")
    sequence = fields.Integer(string='Sequence')
    user_id = fields.Many2one('res.users', string='User')
    category = fields.Char(string='Category')
    is_line_manager = fields.Boolean(string='Is Line Manager')

    @api.onchange('is_line_manager')
    def _onchange_line_manager(self):
        """
            :Author:Nimesh Jadav TechUltra Solutions
            :Date:20/10/2020
            :Func:this method use for set line manager into the category of the leave type approver
            :Return:set line manager on category
        """
        if self.is_line_manager:
            self.user_id = -1
            self.category = "Line Manager"

    def name_get(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:20/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for leave_approver in self:
            if leave_approver.leave_type_id:
                name = leave_approver.leave_type_id and leave_approver.leave_type_id.name
                result.append((leave_approver.id, name))
        return result
