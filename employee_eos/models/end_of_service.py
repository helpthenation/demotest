from odoo import models, fields, api, _
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

Month_Selection_Value = [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                         ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                         ('09', 'September'), ('10', 'October'), ('11', 'November'),
                         ('12', 'December')]


class EndOfService(models.Model):
    _name = 'end.of.service'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "End of Service"
    _order = 'id'

    @api.model
    def _read_group_request_status(self, stages, domain, order):
        request_status_list = dict(self._fields['request_status'].selection).keys()
        return request_status_list

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")

    job_position = fields.Many2one('hr.job', string="Position", compute='_get_job_position')
    job_grade = fields.Many2one('job.grade', string="Grade", compute='_get_job_grade')
    date_of_joining = fields.Date(string="Date of Joining", compute='_get_date_of_joining')  #
    last_working_date = fields.Date(string="Last Working Date")
    number_of_unpaid_days = fields.Float(string="Number of Unpaid days", compute='_get_number_of_unpaid_days')
    leaving_reason = fields.Selection(
        [('resignation', 'Resignation'), ('termination', 'Termination'), ('end_of_contract', ' End of Contract'),
         ('absconded', 'Absconded')],
        string='Leaving Reason')
    service_years = fields.Integer(string="Service Years", compute='_get_service_years')
    service_month = fields.Integer(string="Service Months", compute='_get_service_months')
    service_day = fields.Integer(string="Service Days", compute='_get_service_days')
    last_working_month_for_payslip = fields.Selection(selection=Month_Selection_Value,
                                                      compute='_get_last_working_month_for_payslip')
    notice_pay_amount = fields.Float(string="Notice Pay", help="last month salary if it is not payed.",
                                     compute='_get_notice_pay_amount')
    gratuity_payments_amount = fields.Float(string="Gratuity Payments", compute="_get_gratuity_payments_amount")
    leave_deduction = fields.Float(string="Leave Deduction")
    request_owner_id = fields.Many2one('res.users', string="Request Owner", default=lambda self: self.env.user)
    gratuity_setting_ids = fields.Many2many('hr.gratuity', string="Gratuity Settings",
                                            compute="_get_gratuity_setting_ids")

    remaining_leave_days = fields.Float(string="Remaining Leave Days", compute='_get_remaining_leave_days')
    read_only_user = fields.Boolean(default=False, compute='_get_user_group')
    eos_setting_id = fields.Many2one('eos.request.settings', compute='_compute_eos_setting_id',
                                     string="End Of service setting")

    approver_ids = fields.One2many('eos.request.approver', 'end_of_service_id', string="Approvers")

    submitted_date = fields.Date(string="Submitted Date", help="Request Submit Date")

    reference_num = fields.Char(string="Reference No")

    request_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'Submitted'),
        ('under_approval', 'Under Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], default="new", compute="_compute_request_status", store=True,
        group_expand='_read_group_request_status', compute_sudo=True)

    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_user_status")

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    leave_encashment = fields.Float(string="Leave Encashment", compute="_compute_leave_encashment")

    @api.depends('remaining_leave_days', 'employee_id')
    def _compute_leave_encashment(self):
        for rec in self:
            if rec.remaining_leave_days > 0 and rec.employee_id:
                basic = self.get_related_compensation(employee_id=rec.employee_id, basic=True)
                housing = self.get_related_compensation(employee_id=rec.employee_id, housing=True)
                try:
                    rec.leave_encashment = rec.remaining_leave_days * (basic.amount + housing.amount / 30)
                except:
                    rec.leave_encashment = 0.0

            else:
                rec.leave_encashment = 0.0

    def get_related_compensation(self, employee_id, basic=False, housing=False):
        compensation = False
        if employee_id and housing:
            housing = employee_id.contract_id.related_compensation.filtered(
                lambda compensation: compensation.name.component_type == 'housing_allowance')
            if not housing:
                raise UserError(
                    _('Housing Allowance not found of the employee Compensations Component'))
            if len(housing) > 1:
                raise UserError(_('Multiple Allowance Salary  found of the employee'))
            else:
                compensation = housing
        if employee_id and basic:
            basic = employee_id.contract_id.related_compensation.filtered(
                lambda compensation: compensation.name.component_type == 'basic_pay')
            if not basic:
                raise UserError(
                    _('Basic Salary not found of the employee please set Compensations Component'))
            if len(basic) > 1:
                raise UserError(_('Multiple Basic Salary  found of the employee'))
            else:
                compensation = basic
        return compensation

    @api.depends('leaving_reason', 'employee_id', 'date_of_joining', 'last_working_date')
    def _get_gratuity_setting_ids(self):
        for rec in self:
            if rec.leaving_reason and rec.employee_id and rec.date_of_joining and rec.last_working_date:
                gratuity_setting_ids = self.env['hr.gratuity']
                if rec.employee_id and rec.employee_id.contract_id and rec.last_working_date and rec.date_of_joining and rec.leaving_reason:
                    if rec.leaving_reason == 'absconded':
                        gratuity_setting_id = self.env['hr.gratuity'].search([('reason', '=', rec.leaving_reason)])
                        if gratuity_setting_id:
                            rec.gratuity_setting_ids = gratuity_setting_id[0]
                            continue
                service_time = relativedelta(rec.last_working_date, rec.date_of_joining)
                if service_time.months == 0 and service_time.days == 0:
                    service_years = service_time.years
                else:
                    service_years = service_time.years + 1
                if rec.employee_id.contract_id.employment_status == 'permanent':
                    gratuity_setting_ids = self.env['hr.gratuity'].search(
                        [('from_year', '<=', service_years), ('reason', '=', rec.leaving_reason),
                         ('contract_type', '=', rec.employee_id.contract_id.employment_status)])
                else:
                    gratuity_setting_id = self.env['hr.gratuity'].search(
                        [('contract_type', '=', rec.employee_id.contract_id.employment_status),
                         ('from_year', '<', service_years), ('to_year', '>=', service_years),
                         ('reason', '=', rec.leaving_reason),
                         ('contract_type', '=', rec.employee_id.contract_id.employment_status)])
                    if gratuity_setting_id:
                        gratuity_setting_ids = gratuity_setting_id
                rec.gratuity_setting_ids = gratuity_setting_ids
            else:
                rec.gratuity_setting_ids = self.env['hr.gratuity']

    @api.depends('request_owner_id')
    def _get_user_group(self):
        """
        @Author: Bhavesh Jadav TechUltra Solutions
        @Date:23/11/2020
        @Func:This method use for the set read_only_user boolean True or false base on the group
        """
        user = self.env.user
        for rec in self:
            rec.read_only_user = True
            if user.has_group('security_groups.group_company_hc'):
                rec.read_only_user = False

    @api.depends('employee_id')
    def _get_remaining_leave_days(self):
        for rec in self:
            if rec.employee_id:
                employee_allocation_ids = self.env['hr.leave.allocation'].search([('holiday_type', '=', 'employee'),
                                                                                  ('employee_id', '=',
                                                                                   rec.employee_id.id),
                                                                                  ('state', '=', 'validate'),
                                                                                  ('holiday_status_id.category', '=',
                                                                                   'annual')])
                number_of_days = employee_allocation_ids.mapped('number_of_days')
                leaves_taken = employee_allocation_ids.mapped('leaves_taken')
                remain_leave = float(sum(number_of_days)) - float(sum(leaves_taken))
                rec.remaining_leave_days = remain_leave
            else:
                rec.remaining_leave_days = 0

    @api.depends('date_of_joining', 'last_working_date')
    def _get_service_years(self):
        for rec in self:
            if rec.date_of_joining and rec.last_working_date:
                service_time = relativedelta(rec.last_working_date, rec.date_of_joining)
                rec.service_years = service_time.years
            else:
                rec.service_years = 0

    @api.depends('date_of_joining', 'last_working_date')
    def _get_service_months(self):
        for rec in self:
            if rec.date_of_joining and rec.last_working_date:
                service_time = relativedelta(rec.last_working_date, rec.date_of_joining)
                rec.service_month = service_time.months
            else:
                rec.service_month = 0

    @api.depends('date_of_joining', 'last_working_date')
    def _get_service_days(self):
        for rec in self:
            if rec.date_of_joining and rec.last_working_date:
                service_time = relativedelta(rec.last_working_date, rec.date_of_joining)
                rec.service_day = service_time.days
            else:
                rec.service_day = 0

    def print_report(self):
        return self.env.ref('employee_eos.end_of_service_pdf_report').report_action(self)

    # @api.onchange('request_owner_id')
    # def onchange_employee(self):
    #     """
    #     @Author:Bhavesh Jadav TechUltra solutions
    #     @Date:  04/12/2020
    #     @Func: for apply dynamic domain and set the employee id base on the employment_status
    #     @Return: domain
    #     """
    #     employee_ids = self.env['hr.employee'].search([])
    #     contractor_ids = employee_ids.filtered(lambda emp: emp.contract_id.employment_status == 'contractor')
    #     if contractor_ids:
    #         return {'domain': {'employee_id': [('id', 'in', contractor_ids.ids)]}}
    #     else:
    #         return {'domain': {'employee_id': [('id', 'in', [])]}}

    # @api.depends('leaving_reason', 'employee_id', 'date_of_joining', 'last_working_date')
    # def _get_gratuity_setting_id(self):
    #     for rec in self:
    #         if rec.employee_id and rec.employee_id.contract_id and rec.last_working_date and rec.date_of_joining and rec.leaving_reason:
    #             if rec.leaving_reason == 'absconded':
    #                 gratuity_setting_id = self.env['hr.gratuity'].search_read([('reason', '=', rec.leaving_reason)],
    #                                                                           ['id'])
    #                 if gratuity_setting_id:
    #                     rec.gratuity_setting_id = gratuity_setting_id[0].get('id')
    #                     continue
    #
    #             service_time = relativedelta(rec.last_working_date, rec.date_of_joining)
    #             if service_time.months == 0 and service_time.days == 0:
    #                 service_years = service_time.years
    #             else:
    #                 service_years = service_time.years + 1
    #             gratuity_setting_id = self.env['hr.gratuity'].search_read(
    #                 [('contract_type', '=', rec.employee_id.contract_id.employment_status),
    #                  ('from_year', '<', service_years), ('to_year', '>=', service_years),
    #                  ('reason', '=', rec.leaving_reason),
    #                  ('contract_type', '=', rec.employee_id.contract_id.employment_status)], ['id'])
    #             if gratuity_setting_id:
    #                 rec.gratuity_setting_id = gratuity_setting_id[0].get('id')
    #             else:
    #                 rec.gratuity_setting_id = self.env['hr.gratuity']
    #         else:
    #             rec.gratuity_setting_id = self.env['hr.gratuity']

    @api.depends('employee_id')
    def _get_date_of_joining(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.contract_id:
                rec.date_of_joining = rec.employee_id.contract_id.date_start
            else:
                rec.date_of_joining = False

    @api.depends('last_working_date')
    def _get_number_of_unpaid_days(self):
        for rec in self:
            if rec.last_working_date:
                last_day_of_month = calendar.monthrange(rec.last_working_date.year, rec.last_working_date.month)[1]
                if rec.last_working_date.day == last_day_of_month:
                    rec.number_of_unpaid_days = 0
                else:
                    rec.number_of_unpaid_days = rec.last_working_date.day
            else:
                rec.number_of_unpaid_days = 0

    @api.depends('gratuity_setting_ids', 'employee_id')
    def _get_gratuity_payments_amount(self):
        for rec in self:
            if rec.gratuity_setting_ids and rec.date_of_joining and rec.last_working_date:
                basic = self.get_related_compensation(employee_id=rec.employee_id, basic=True)
                if rec.employee_id.contract_id.employment_status == 'permanent':
                    gratuity = 0.0
                    service_time = relativedelta(rec.last_working_date, rec.date_of_joining)
                    service_year = service_time.years
                    counter = 0
                    for rule in rec.gratuity_setting_ids:
                        counter += 1
                        remaining_year = int(service_year) - int(rule.to_year)
                        if remaining_year > 0:
                            actual_year = int(rule.to_year)
                        else:
                            actual_year = service_year
                        service_year = int(service_year) - int(rule.to_year)
                        gratuity += ((basic.amount * actual_year) * rule.multiplier)
                        if counter == len(rec.gratuity_setting_ids):
                            wage = rec.employee_id.contract_id.wage
                            gratuity += (((wage / 12) * int(service_time.months)) * rule.multiplier) + (
                                    (((wage / 12) / 30) * int(service_time.days)) * rule.multiplier)
                            # gratuity += ((((wage / 12) / 30) * int(service_time.days)) * rule.multiplier)
                    rec.gratuity_payments_amount = gratuity
                else:
                    gratuity_payments_amount = ((((
                                                          (
                                                                  rec.last_working_date - rec.date_of_joining).days + 1) / 365) *
                                                 rec.gratuity_setting_ids[0].number_of_days) * (
                                                        basic.amount * (12 / 365)))
                    rec.gratuity_payments_amount = gratuity_payments_amount
            else:
                rec.gratuity_payments_amount = 0.0

    @api.depends('last_working_month_for_payslip', 'last_working_date', 'employee_id', 'leaving_reason')
    def _get_notice_pay_amount(self):
        for rec in self:
            if rec.leaving_reason == 'absconded':
                rec.notice_pay_amount = 0.0
                continue
            if rec.last_working_date and rec.last_working_month_for_payslip and rec.employee_id:
                if rec.employee_id.contract_id:
                    last_day_of_month = calendar.monthrange(rec.last_working_date.year, rec.last_working_date.month)[1]
                    basic = self.get_related_compensation(employee_id=rec.employee_id, basic=True)
                    wage = basic.amount
                    one_day_wage = wage / last_day_of_month
                    if rec.number_of_unpaid_days > 0:
                        rec.notice_pay_amount = round(one_day_wage * rec.number_of_unpaid_days)
                    else:
                        rec.notice_pay_amount = 0.0
                else:
                    rec.notice_pay_amount = 0.0
            else:
                rec.notice_pay_amount = 0.0

    @api.depends('last_working_date')
    def _get_last_working_month_for_payslip(self):
        for rec in self:
            if rec.last_working_date:
                rec.last_working_month_for_payslip = rec.last_working_date.strftime("%m")
            else:
                rec.last_working_month_for_payslip = False

    @api.depends('employee_id')
    def _get_job_position(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.contract_id and rec.employee_id.contract_id.job_id:
                rec.job_position = rec.employee_id.contract_id.job_id.id
            else:
                rec.job_position = False

    @api.depends('employee_id')
    def _get_job_grade(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.contract_id and rec.employee_id.contract_id.job_grade:
                rec.job_grade = rec.employee_id.contract_id.job_grade.id
            else:
                rec.job_grade = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('end.of.service') or _('New')
        res = super(EndOfService, self).create(vals)
        return res

    @api.depends('request_owner_id')
    def _compute_eos_setting_id(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:10/11/2020
        @Func:This compute method use for the set education_settings_id in request screen for the set appover line
        @Return:N/A
        """
        eos_setting_id = self.env['eos.request.settings'].search([], limit=1)
        for rec in self:
            rec.eos_setting_id = eos_setting_id

    # approval methods

    def _get_user_approval_activities(self, user, activity_type_id):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:19/11/2020
        @Func:This method use for the get approval activities
        @Return:activities
        """
        domain = [
            ('res_model', '=', 'end.of.service'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    @api.depends('approver_ids.status')
    def _compute_user_status(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:11/11/2020
        @Func:This compute method use for the set user status  of the approver in request status
        @Return: N/A
        """
        for approval in self:
            approvers = approval.approver_ids.filtered(
                lambda approver: approver.user_id == self.env.user).filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
            if len(approvers) > 0:
                approval.user_status = approvers[0].status
            else:
                approval.user_status = False

    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:10/11/2020
        @Func:This method use for the set request status base on the user status
        @Return:N/A
        """
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new') and not status_lst.count('pending') and not status_lst.count('approved'):
                    status = 'new'
                elif 0 < status_lst.count('approved') < len(status_lst):
                    status = 'under_approval'
                elif status_lst.count('approved') == len(status_lst):
                    status = 'approved'
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status

    @api.onchange('eos_setting_id')
    def _onchange_eos_setting_id(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:18/11/2020
        @Func:This onchnage method use for the set approval line in
        the request screen and also add the manager approver and the higher manager apporver base on the settings of
        the education and the employee id
        @Return:N/A
        """
        self.approver_ids = self.env['eos.request.approver']
        current_users = []
        if self.eos_setting_id:
            new_approvals_ordered = self.eos_setting_id.approval_sequence.sorted(lambda x: x.sequence)
        else:
            new_approvals_ordered = self.env['res.users']
        new_users = []
        user_category = {}
        for approval in new_approvals_ordered:
            if approval.user_id:
                new_users.append(approval.user_id)
                key = approval.user_id.id
                value = approval.approval_category
                user_category[key] = value
        if self.approver_ids:
            approver_ids = self.approver_ids.sorted(lambda x: x.sequence)
            last_sequence = approver_ids[-1].sequence
        else:
            last_sequence = 0
        self.create_approver_line(user_list=new_users, last_sequence=last_sequence,
                                  current_users=current_users, user_category=user_category)

    def create_approver_line(self, user_list, last_sequence, current_users, user_category={}):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:22/11/2020
        @Func:This method use for the create eos.request.approver line in request screen
        @Return:N/A
        """
        counter = 0
        for user in user_list:
            if user.id not in current_users:
                counter += 1
                last_sequence += 10
                approver_ids_vals = {'sequence': last_sequence,
                                     'user_id': user.id,
                                     'end_of_service_id': self.id,
                                     'status': 'new'}
                approver_ids_vals.update({'approval_category': user_category.get(user.id) or ''})

                self.approver_ids += self.env['eos.request.approver'].new(approver_ids_vals)

    def action_submit_request(self):
        if not self.eos_setting_id:
            raise UserError(
                _(
                    'Please configure the EOS Approver(s) Settings properly  (configuration ->EOS Approver(s) '
                    'Settings )'))

        self.submitted_date = datetime.datetime.now()
        reference = str(self.env['ir.sequence'].next_by_code('end.of.service.reference')) + str(
            self.employee_id.system_id) + str(self.submitted_date.strftime('%m%d%Y'))
        self.reference_num = reference
        requests = \
            self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new').sorted('sequence')[
                0]
        requests._create_activity()
        requests.write({'status': 'pending'})
        return True

    def action_approve(self, approver=None):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:19/11/2020
        @Func:This method use for the approve button and
        add approval date and the create next approver activity with done current approval activity
        @Return:N/A
        """
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            ).filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
        if len(approver) > 0:
            approver[0].write({'status': 'approved', 'approval_date': datetime.datetime.now()})
        activity = self.env.ref('employee_eos.mail_activity_data_employee_eos').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver[0].status == 'new').sorted(
            'sequence')

        if len(approvers) > 0:
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
        else:
            self.approval_date = datetime.datetime.now()

    def action_cancel(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:23/11/2020
        @Func:This method use for the when request cancel
        and by the user or appover and the done pending activity and change state of the request
        @Return:N/A
        """
        activity = self.env.ref('employee_eos.mail_activity_data_employee_eos').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).unlink()
        self.mapped('approver_ids').write({'status': 'cancel'})
