# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class Employee(models.Model):
    _inherit = "hr.employee"

    current_leave_state = fields.Selection(
        selection_add=[('withdraw', 'Withdraw'), ('approve_withdraw', 'Approve Withdraw'),
                       ('under_approval', 'Under Approval')])


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"
    _description = "Time Off"

    attachment = fields.Binary(string="Attachment")
    file_name = fields.Char(string="Attachment Name")
    diagnosis = fields.Char(string='Diagnosis')
    hospital_name = fields.Char(string="Hospital Name")
    reference_no = fields.Char(string="Reference No")
    _sql_constraints = [('leave_reference_unique', 'unique(reference_no)', 'Reference No already exits')]

    approvers_ids = fields.One2many('hr.leave.approver', 'time_off_id', string='Approvers')
    category = fields.Selection(related='holiday_status_id.category', string="Category")
    attachment_required = fields.Boolean(related="holiday_status_id.attachment_required", string="Attachment Required")



    state = fields.Selection(selection_add=[('withdraw', 'Withdraw'), ('approve_withdraw', 'Approve Withdraw'),
                                            ('under_approval', 'Under Approval')], default='draft',
                             compute='_compute_request_status')
    approver_status = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
         ('rejected', 'Rejected'), ('withdraw', 'Withdraw'), ('withdraw_approved', 'Withdraw Approved')],
        string='Status',
        compute='_compute_approver_status')

    all_approved = fields.Boolean('All Approved', compute='compute_get_all_approved')
    company_employee_id = fields.Char(related='employee_id.company_employee_id')
    leave_type_code = fields.Char(related='holiday_status_id.code')

    @api.depends('approvers_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approvers_ids.status')
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'

                elif status_lst.count('refused'):
                    status = 'refuse'
                elif status_lst.count('withdraw'):
                    status = 'withdraw'
                elif status_lst.count('withdraw_approved'):
                    status = 'approve_withdraw'
                elif status_lst.count('draft') and not status_lst.count('pending') and not status_lst.count('approved'):
                    status = 'draft'
                elif 0 < status_lst.count('approved') < len(status_lst):
                    status = 'under_approval'
                elif status_lst.count('approved') == len(status_lst):
                    status = 'validate'
                else:
                    status = 'confirm'
            else:
                status = 'draft'
            request.state = status

    @api.depends('approvers_ids.status')
    def _compute_approver_status(self):
        for approval in self:
            approvers = approval.approvers_ids.filtered(
                lambda approver: approver.approver == self.env.user).filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
            if len(approvers) > 0:
                approval.approver_status = approvers[0].status
            else:
                approval.approver_status = False

    def action_refuse(self):
        """
            :Author:Nimesh Jadav TechUltra Solutions
            :Date:20/10/2020
            :Func:this method use for open wizard for the reject reason
            :Return:set reject reason for the refuse time off
        """
        if not self._context.get('reason'):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reject Reason',
                'res_model': 'hr.leave.refuse.reason.wizard',
                'view_mode': 'form',
                'target': 'new',
                'view_id': self.env.ref('hr_holidays_custom.hr_leave_refuse_reason_wizard_view_form').id,
                'context': {
                    'related_name': self._name,
                    'active_id': self.id
                }
            }
        else:
            if self.approvers_ids:
                self.approvers_ids.write({'rejection_reason': self._context.get('reason')})
            result = super(HolidaysRequest, self).action_refuse()
            tag = True
            for approver in self.approvers_ids:
                if tag:
                    approver.status = 'rejected'
                    tag = False
            return result

    def action_withdraw(self):
        tag = True
        for approver in self.approvers_ids:
            if tag:
                approver.status = 'to_approve'
                tag = False
            else:
                approver.status = 'draft'

        self.state = 'withdraw'

    def action_approve_withdraw(self):
        for approver in self.approvers_ids:
            approver.status = 'approve_withdraw'
        self.state = 'approve_withdraw'

    @api.depends('approvers_ids')
    def compute_get_all_approved(self):
        """
            :Author:Nimesh Jadav TechUltra Solutions
            :Date:20/10/2020
            :Func:this method use for get total approves
            :Return: set true or false
        """
        result = True
        for rec in self:
            for appr in self.approvers_ids:
                if appr.status != 'Approved':
                    result = False
            rec.all_approved = result

    @api.onchange('holiday_status_id')
    def onchange_time_off_validation(self):
        """
            :Author:Nimesh Jadav TechUltra Solutions
            :Date:20/10/2020
            :Func:this method use for set approvers based on validation
            :Return:set value for the approver
        """
        if self.holiday_status_id.validation_type == 'hr':
            self.approvers_ids = [(6, 0, [])]
            if self.holiday_status_id and self.holiday_status_id.responsible_id:
                resposible_id = self.holiday_status_id.responsible_id.id
                rec = self.env['hr.leave.approver'].search([('approver', '=', resposible_id), ('status', '=', 'draft')],
                                                           limit=1)
                if not rec:
                    rec = rec.create({'approver': resposible_id, 'status': 'draft'})
                self.approvers_ids = [(6, 0, rec.ids)]


        elif self.holiday_status_id.validation_type == 'manager':
            self.approvers_ids = [(6, 0, [])]
            if self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.user_id:
                parent_id = self.employee_id.parent_id.user_id.id
                rec = self.env['hr.leave.approver'].search([('approver', '=', parent_id), ('status', '=', 'draft')],
                                                           limit=1)
                if not rec:
                    rec = rec.create({'approver': parent_id, 'status': 'draft'})
                self.approvers_ids = [(6, 0, rec.ids)]

        elif self.holiday_status_id.validation_type == 'both':
            self.approvers_ids = [(6, 0, [])]
            if self.employee_id and self.employee_id.parent_id and self.employee_id.parent_id.user_id:
                parent_id = self.employee_id.parent_id.user_id.id
                rec = self.env['hr.leave.approver'].search([('approver', '=', parent_id), ('status', '=', 'draft')],
                                                           limit=1)
                if not rec:
                    rec = rec.create({'approver': parent_id, 'status': 'draft'})
                self.approvers_ids = [(6, 0, rec.ids)]

            if self.holiday_status_id and self.holiday_status_id.responsible_id:
                resposible_id = self.holiday_status_id.responsible_id.id
                rec = self.env['hr.leave.approver'].search([('approver', '=', resposible_id), ('status', '=', 'draft')],
                                                           limit=1)
                if not rec:
                    rec = rec.create({'approver': resposible_id, 'status': 'draft'})
                self.approvers_ids = [(6, 0, rec.ids)]

    @api.model
    def create(self, val):
        """
            :Author:Nimesh Jadav TechUltra Solutions
            :Date:21/10/2020
            :Func:this method use for set state draft for the new request
            :Return: request val(dict)
        """
        res = super(HolidaysRequest, self).create(val)
        if res:
            res.state = 'draft'
            res.approvers_ids.write({'status': 'draft'})
        return res

    def action_confirm(self):
        """
                :Author:Nimesh Jadav TechUltra Solutions
                :Date:21/10/2020
                :Func:this method use for the change request into the approve state
                :Return: request res(dict)
        """
        context = dict(self.env.context)
        context.update({'is_confirm_timeoff_approver': True})
        res = super(HolidaysRequest, self.with_context(context)).action_confirm()
        tag = True
        # activity = self.env.ref('hr_holidays_custom.mail_activity_data_time_off_request').id
        # self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
        for approver in self.approvers_ids:
            if tag:
                approver.status = 'to_approve'
                # approver[0]._create_activity()
                approver.approve_tag = True
                tag = False
            else:
                approver.status = 'pending'
        return res

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        if self._context.get('is_confirm_timeoff_approver', False) and act_values.get('user_id',
                                                                                      False) and self.approvers_ids:
            act_values.update({'user_id': self.approvers_ids[0].approver.id})

        if self._context.get('is_approve_timeoff_approver', False) and act_values.get('user_id',
                                                                                      False) and self.approvers_ids:
            approver = self.mapped('approvers_ids').filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
            if len(approver) > 1:
                act_values.update({'user_id': approver[1].approver.id})
        res = super(HolidaysRequest, self).activity_schedule(act_type_xmlid=act_type_xmlid, date_deadline=date_deadline,
                                                             summary=summary, note=note, **act_values)
        return res

    def action_approve(self):
        """
                :Author:Nimesh Jadav TechUltra Solutions
                :Date:21/10/2020
                :Func:this method use for the change request into the approve state
                :Return: request res(dict)
        """
        if any(holiday.state not in ['confirm', 'under_approval'] for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        # Post a second message, more verbose than the tracking message
        for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
            holiday.message_post(
                body=_('Your %s planned on %s has been accepted' % (
                    holiday.holiday_status_id.display_name, holiday.date_from)),
                partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()
        # activity = self.env.ref('hr_holidays_custom.mail_activity_data_time_off_request').id
        # self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()

        approver = self.mapped('approvers_ids').filtered(
            lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
        if len(approver) > 0:
            # approver[0]._create_activity()
            approver[0].write({'status': 'approved'})
        if len(approver) > 1:
            approver[1].write({'status': 'to_approve'})

        return True

    def _get_user_approval_activities(self, user, activity_type_id):
        domain = [
            ('res_model', '=', 'hr.leave'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    # Overwrite cuz of statement change
    def action_validate(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['confirm', 'under_approval', 'validate1'] for holiday in self):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})
        self.filtered(lambda holiday: holiday.validation_type == 'both').write(
            {'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type != 'both').write(
            {'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
            if holiday.holiday_type == 'category':
                employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'company':
                employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            else:
                employees = holiday.department_id.member_ids

            conflicting_leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True
            ).search([
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('state', 'not in', ['cancel', 'refuse']),
                ('holiday_type', '=', 'employee'),
                ('employee_id', 'in', employees.ids)])

            if conflicting_leaves:
                # YTI: More complex use cases could be managed in master
                if holiday.leave_type_request_unit != 'day' or any(
                        l.leave_type_request_unit == 'hour' for l in conflicting_leaves):
                    raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

                for conflicting_leave in conflicting_leaves:
                    if conflicting_leave.leave_type_request_unit == 'half_day' and conflicting_leave.request_unit_half:
                        conflicting_leave.action_refuse()
                        continue
                    # Leaves in days
                    split_leaves = self.env['hr.leave']
                    target_state = conflicting_leave.state
                    conflicting_leave.action_refuse()
                    if conflicting_leave.date_from < holiday.date_from:
                        before_leave_vals = conflicting_leave.copy_data({
                            'date_from': conflicting_leave.date_from.date(),
                            'date_to': holiday.date_from.date() + timedelta(days=-1),
                        })[0]
                        before_leave = self.env['hr.leave'].new(before_leave_vals)
                        before_leave._onchange_request_parameters()
                        if before_leave.date_from < before_leave.date_to:
                            split_leaves |= self.env['hr.leave'].with_context(
                                tracking_disable=True,
                                mail_activity_automation_skip=True,
                                leave_fast_create=True
                            ).create(before_leave._convert_to_write(before_leave._cache))
                    if conflicting_leave.date_to > holiday.date_to:
                        after_leave_vals = conflicting_leave.copy_data({
                            'date_from': holiday.date_to.date() + timedelta(days=1),
                            'date_to': conflicting_leave.date_to.date(),
                        })[0]
                        after_leave = self.env['hr.leave'].new(after_leave_vals)
                        after_leave._onchange_request_parameters()
                        if after_leave.date_from < after_leave.date_to:
                            split_leaves |= self.env['hr.leave'].with_context(
                                tracking_disable=True,
                                mail_activity_automation_skip=True,
                                leave_fast_create=True
                            ).create(after_leave._convert_to_write(after_leave._cache))
                    for split_leave in split_leaves:
                        if target_state == 'draft':
                            continue
                        if target_state == 'confirm':
                            split_leave.action_confirm()
                        elif target_state == 'validate1':
                            split_leave.action_confirm()
                            split_leave.action_approve()
                        elif target_state == 'validate':
                            split_leave.action_confirm()
                            split_leave.action_validate()

            values = [holiday._prepare_holiday_values(employee) for employee in employees]
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
            ).create(values)
            leaves.action_approve()
            # FIXME RLi: This does not make sense, only the parent should be in validation_type both
            if leaves and leaves[0].validation_type == 'both':
                leaves.action_validate()
        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        return True
