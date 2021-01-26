from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import date


class EducationRequest(models.Model):
    _name = 'education.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Education Request"
    _order = 'id'
    _rec_name = 'name'

    @api.model
    def _read_group_request_status(self, stages, domain, order):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:21/11/2020
        @Func:This method se for get string of the selection value
        @Return: list of the string of selection
        """
        request_status_list = dict(self._fields['request_status'].selection).keys()
        return request_status_list

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    academic_year = fields.Many2one('education.academic.year', string="Academic Year")
    education_eligibility_id = fields.Many2one('education.eligibility',
                                               string="Eligibility Rule")
    request_owner_id = fields.Many2one('res.users', string="Request Owner", default=lambda self: self.env.user)
    request_lines = fields.One2many('education.request.line', 'education_request_id', string="Children Lines")
    employee_job_grade = fields.Many2one('job.grade', string="Job Grade", compute='_compute_job_grade',
                                         store=True)
    employee_job_title = fields.Many2one('job.title', string="Job Title", compute='_compute_job_title',
                                         store=True)
    claim_date = fields.Date(string="Claim Date", help="Submission Date")
    claim_number = fields.Char(string="Claim Number",
                               help="auto-generated number + employee system-id + submission date")

    note = fields.Text(string="Description")

    read_only_user = fields.Boolean(default=False, compute='_get_user_group')

    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_user_status")

    request_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'Submitted'),
        ('under_approval', 'Under Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], default="new", compute="_compute_request_status", store=True, compute_sudo=True,
        group_expand='_read_group_request_status')

    approver_ids = fields.One2many('education.request.approver', 'request_id', string="Approvers")

    education_settings_id = fields.Many2one('education.request.settings', string="Education Setting", required=True,
                                            compute='_compute_education_settings_id')

    approval_minimum = fields.Integer(related="education_settings_id.approval_minimum")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

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

    @api.onchange('education_settings_id', 'employee_id')
    def _onchange_education_settings_id(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:18/11/2020
        @Func:This onchnage method use for the set approval line in
        the request screen and also add the manager approver and the higher manager apporver base on the settings of
        the education and the employee id
        @Return:N/A
        """
        if self.employee_id:
            self.approver_ids = self.env['education.request.approver']
            current_users = []
            if self.education_settings_id:
                new_approvals_ordered = self.education_settings_id.approval_sequence.sorted(lambda x: x.sequence)
            else:
                new_approvals_ordered = self.env['res.users']

            manager_approver = []
            if self.education_settings_id.is_manager_approver:
                if self.employee_id.parent_id:
                    manager_approver.append(self.employee_id.parent_id.user_id)
                    if self.education_settings_id.is_higher_manager_approver:
                        if self.employee_id.parent_id.parent_id:
                            manager_approver.append(self.employee_id.parent_id.parent_id.user_id)
            if manager_approver:
                if self.approver_ids:
                    approver_ids = self.approver_ids.sorted(lambda x: x.sequence)
                    last_sequence = approver_ids[-1].sequence
                else:
                    last_sequence = 0
                self.create_approver_line(user_list=manager_approver, last_sequence=last_sequence,
                                          current_users=current_users, is_manager_approval=True)

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

    def create_approver_line(self, user_list, last_sequence, current_users, user_category={},
                             is_manager_approval=False):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:22/11/2020
        @Func:This method use for the create education.request.approver line in request screen
        @Return:N/A
        """
        counter = 0
        for user in user_list:
            if user.id not in current_users:
                counter += 1
                last_sequence += 10
                approver_ids_vals = {'sequence': last_sequence,
                                     'user_id': user.id,
                                     'request_id': self.id,
                                     'status': 'new'}
                if is_manager_approval:
                    approver_ids_vals.update({'approval_category': 'LM' + '-' + str(counter)})
                else:
                    approver_ids_vals.update({'approval_category': user_category.get(user.id) or ''})

                self.approver_ids += self.env['education.request.approver'].new(approver_ids_vals)

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

    @api.depends('request_owner_id')
    def _compute_education_settings_id(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:10/11/2020
        @Func:This compute method use for the set education_settings_id in request screen for the set appover line
        @Return:N/A
        """
        education_settings_id = self.env['education.request.settings'].search([], limit=1)
        for rec in self:
            rec.education_settings_id = education_settings_id

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

    def action_submit_request(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:19/11/2020
        @Func:This method use for the submit request and
        the validation and set claim date and auto generate number and call _create_activity() for the approver user
        @Return:True
        """
        if not self.request_lines:
            raise UserError(_('Please add children information'))
        self.claim_date = datetime.datetime.now()
        self.claim_number = self.env['ir.sequence'].next_by_code(
            'claim.number') + self.employee_id.system_id + datetime.datetime.now().strftime('%m%d%Y')
        if not self.education_settings_id:
            raise UserError(
                _('Please configure the education settings properly  (configuration -> education settings )'))
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
        for request_line in self.request_lines:
            if request_line.terms_fees_line_ids.filtered(lambda line: line.approve_amount <= 0):
                raise UserError(_('Please add approve amount in terms and fees line'))
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            ).filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
        if len(approver) > 0:
            approver[0].write({'status': 'approved', 'approval_date': datetime.datetime.now()})
        activity = self.env.ref('child_education.mail_activity_data_education_request').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver[0].status == 'new').sorted(
            'sequence')

        if len(approvers) > 0:
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
        else:
            self.approval_date = datetime.datetime.now()

    def _get_user_approval_activities(self, user, activity_type_id):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:19/11/2020
        @Func:This method use for the get approval activities
        @Return:activities
        """
        domain = [
            ('res_model', '=', 'education.request'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    def action_cancel(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:23/11/2020
        @Func:This method use for the when request cancel
        and by the user or appover and the done pending activity and change state of the request
        @Return:N/A
        """
        activity = self.env.ref('child_education.mail_activity_data_education_request').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).unlink()
        self.mapped('approver_ids').write({'status': 'cancel'})

    @api.depends('employee_id')
    def _compute_job_title(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:21/11/2020
        @Func:This compute method use for the set employee job base on the employee id
        @Return:N/A
        """
        for rec in self:
            rec.employee_job_title = rec.employee_id.contract_id.job_title.id

    @api.depends('employee_id')
    def _compute_job_grade(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:21/11/2020
        @Func:This compute method use for the set employee grade base on the employee id
        @Return:N/A
        """
        for rec in self:
            rec.employee_job_grade = rec.employee_id.contract_id.job_grade.id

    @api.onchange('request_owner_id')
    def onchange_employee(self):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date:  17/09/2020
        @Func: for apply dynamic domain and set the employee id base on the current user employee
        @Return: domain
        """
        if self.env.user.has_group('security_groups.group_company_hc'):
            employees = self.env['hr.employee'].search([])
            self.employee_id = self.env.user.employee_id.id
            self._onchange_education_settings_id()
            return {'domain': {'employee_id': [('id', 'in', employees.ids)]}}

        elif self.env.user.has_group('security_groups.group_company_employee'):
            if self.env.user.employee_id:
                self.employee_id = self.env.user.employee_id.id
                self._onchange_education_settings_id()
                return {'domain': {'employee_id': [('id', '=', self.env.user.employee_id.id)]}}
            else:
                # if the login user are not employee and the is in employee group then its blank
                return {'domain': {'employee_id': [('id', 'in', [-1])]}}
        else:
            return {'domain': {'employee_id': [('id', 'in', [-1])]}}

    @api.onchange('academic_year', 'employee_id')
    def onchange_education_eligibility(self):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date:  17/09/2020
        @Func:This method use for the set education eligibility rule base on the employee and the academic_year
        @Return:N/A
        """
        if self.employee_id and self.academic_year:
            country_id = self.env['res.country'].search([('code', '=', 'AE')])
            if self.employee_id.country_id == country_id:
                is_uae = True
            else:
                is_uae = False
            rule = self.get_education_eligibility_rule(is_uae=is_uae, employee_id=self.employee_id,
                                                       academic_year=self.academic_year)
            if rule:
                self.education_eligibility_id = rule[0]
            else:
                raise UserError(
                    _(
                        "Warning! eligibility rule not found for the employee,please configure the eligibility Rule "
                        "properly "))

        else:
            self.education_eligibility_id = self.env['education.eligibility']

    def get_education_eligibility_rule(self, is_uae, employee_id, academic_year):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 18/11/2020
        @Func: this method use for the find rule for the eduction request base on the employee id
                # first search specific_per_child rule
                # if specific_per_child rule not found then  search exception rule
                # if specific_per_child rule and exception rule not found then search no_exception rule
                # Check priority of the rule if employee job grade matches withe rule job grade then gives
                # priority else find the rule with out job grade
        @Return: education eligibility rule
        """
        today = date.today()
        rule = False
        rule = self.env['education.eligibility'].search(
            [('exception', '=', 'specific_per_child'),
             ('employee_id', '=', employee_id.id),
             ('academic_year_id', '=', academic_year.id), ('valid_from_date', '<', today),
             ('valid_to_date', '>', today)])
        if not rule:
            exception_rule = self.env['education.eligibility'].search(
                [('exception', '=', 'exception'), ('academic_year_id', '=', academic_year.id),
                 ('valid_from_date', '<', today), ('valid_to_date', '>', today)])
            exception_rule = exception_rule.filtered(lambda rule: employee_id.id in rule.employee_ids.ids)
            if exception_rule:
                rule = exception_rule
            if not rule:
                job_grade = employee_id.contract_id.job_grade.id
                contract_subgroup = employee_id.contract_id.contract_subgroup.id
                eligibility_rule = self.env['education.eligibility'].search(
                    [('exception', '=', 'no_exception'), ('is_uae_nationals', '=', is_uae),
                     ('academic_year_id', '=', academic_year.id), ('valid_from_date', '<', today),
                     ('valid_to_date', '>', today)])
                eligibility_rule = eligibility_rule.filtered(
                    lambda rule: contract_subgroup in rule.contract_subgroup.ids)
                if eligibility_rule:
                    without_job_grade_rule = eligibility_rule.filtered(
                        lambda rule: not rule.job_grades)
                    with_job_grade_rule = eligibility_rule - without_job_grade_rule
                    if with_job_grade_rule:
                        rule = with_job_grade_rule.filtered(
                            lambda rule: job_grade in eligibility_rule.job_grades.ids)
                        if not rule:
                            rule = without_job_grade_rule
                    else:
                        rule = without_job_grade_rule
        return rule

    @api.model
    def create(self, vals):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 21/11/2020
        @Func:This method inherit for the add validation and athe set name of the request
        @Return:Result of the supper call
        """
        if vals.get('employee_id'):
            previous_pending_request = self.env['education.request'].search(
                [('employee_id', '=', vals.get('employee_id')),
                 ('request_status', 'in', ['pending', 'under_approval'])])
            if previous_pending_request:
                raise UserError(
                    _(
                        'You have already one pending request so you can bot allowed to create a new request please '
                        'process the pending request first '))

        if not vals.get('request_lines'):
            raise UserError(
                _('Please Add Children Information'))

        if vals.get(
                'request_lines') and self.education_eligibility_id and self.education_eligibility_id.number_of_child > vals.get(
            'request_lines'):
            raise UserError(
                _(
                    'You can only {child} Children Education Assistance if you wanna add more Children then please  '
                    'contact your higher authority').format(
                    _('child:'), self.education_eligibility_id.number_of_child))

        vals['name'] = self.env['ir.sequence'].next_by_code('education.request') or _('New')
        res = super(EducationRequest, self).create(vals)
        return res

    @api.onchange('employee_id')
    def onchange_delete_child_line(self):
        if self.employee_id and self.request_lines:
            self.request_lines.unlink()

    def print_report(self):
        return self.env.ref('child_education.child_education_print').report_action(self)


class EducationRequestLine(models.Model):
    _name = 'education.request.line'
    _description = "Education Request Line"
    _order = 'id'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    child_id = fields.Many2one('res.partner')
    child_birthdate = fields.Date(string="Date Of Birth", compute='_compute_child_birthdate')
    child_age = fields.Integer(string="Child Age", compute='_compute_child_age')
    eligibility_amount = fields.Monetary(compute='_compute_eligibility_amount', string="Eligibility Amount")
    approved_amount = fields.Monetary(compute='_compute_approved_amount', string="Approved Amount")
    balance_amount = fields.Monetary(compute='_compute_balance_amount', string="Balance Amount")
    education_request_id = fields.Many2one('education.request', string="Request Id")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    # School info
    school = fields.Many2one('schools', string="School")
    school_grade = fields.Many2one('school.grades', string='School Grade')
    reference_no = fields.Char(string="Reference No")
    reference_date = fields.Date(string="Reference Date")
    total_claimed_amount = fields.Monetary(string="Total Claimed Amount",
                                           compute='_compute_total_claimed_amount')
    paid_to_school = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Paid To School", default="yes", required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')

    terms_fees_line_ids = fields.One2many('education.terms.fees.line', 'request_line_id', 'Terms Fees')

    # request_status = fields.Selection(related="education_request_id.request_status")

    @api.depends('child_birthdate')
    def _compute_child_age(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 21/11/2020
        @Func: This compute method use for the set child age base on the birth date of the child
        @Return:N/A
        """
        for rec in self:
            if rec.child_birthdate:
                today = date.today()
                age = today.year - rec.child_birthdate.year - (
                        (today.month, today.day) < (rec.child_birthdate.month, rec.child_birthdate.day))
                rec.child_age = age
            else:
                rec.child_age = 0.0

    @api.depends('child_id')
    def _compute_child_birthdate(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 23/11/2020
        @Func:This method use for the set birthdate of the child base on the child id
        @Return:N/A
        """
        for rec in self:
            if rec.child_id:
                rec.child_birthdate = rec.child_id.date
            else:
                rec.child_birthdate = False

    @api.depends('terms_fees_line_ids')
    def _compute_total_claimed_amount(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 23/11/2020
        @Func:This compute method use for the calculate the  total claimed amount base on the terms and fees amount
        @Return:N/A
        """
        for rec in self:
            if rec.terms_fees_line_ids:
                rec.total_claimed_amount = sum(rec.terms_fees_line_ids.mapped('claimed_amount'))
            else:
                rec.total_claimed_amount = 0.0

    def write(self, vals):
        if vals.get('child_id') and self.education_request_id.request_lines and vals.get(
                'child_id') in self.education_request_id.request_lines.mapped('child_id').ids:
            raise UserError(_(
                'You have multiple Children Information  line  with the same child please add one child one '
                'time'))
        res = super(EducationRequestLine, self).write(vals)
        if not self.terms_fees_line_ids:
            raise UserError(
                _('Please add Schools Terms and Fees claim line'))
        if self.total_claimed_amount and self.balance_amount and self.total_claimed_amount > self.balance_amount:
            raise UserError(
                _(
                    'Your claim amount is more than the balance amount please add the proper claim amount in terms '
                    'and fees line '))
        if self.child_age and self.education_request_id.education_eligibility_id and self.education_request_id.education_eligibility_id.exception in [
            'no_exception', 'exception']:
            if self.education_request_id.education_eligibility_id.child_max_age < self.child_age:
                raise UserError(
                    _('Your child is over age for the Education Assistance please contact your higher authority'))
            if self.education_request_id.education_eligibility_id.child_min_age > self.child_age:
                raise UserError(
                    _('Your child is under age for the Education Assistance please contact your higher authority'))
        return res

    @api.model
    def create(self, vals):
        if vals.get('education_request_id'):
            education_request_id = self.env['education.request'].browse(vals.get('education_request_id'))
            if education_request_id.request_lines:
                child_ids = education_request_id.request_lines.mapped('child_id')
                if vals.get('child_id') in child_ids.ids:
                    raise UserError(_(
                        'You have multiple Children Information  line  with the same child please add one child one '
                        'time'))

        if not vals.get('terms_fees_line_ids'):
            raise UserError(
                _('Please add Schools Terms and Fees claim line'))

        if vals.get('total_claimed_amount') and vals.get('balance_amount') and vals.get(
                'total_claimed_amount') > vals.get('balance_amount'):
            raise UserError(
                _(
                    'Your claim amount is more than the balance amount please add the proper claim amount in terms '
                    'and fees line '))
        if vals.get('child_age'):
            education_eligibility_id = self.env['education.request'].browse(
                vals.get('education_request_id')).education_eligibility_id
            if education_eligibility_id and education_eligibility_id.exception in ['no_exception', 'exception']:
                if education_eligibility_id.child_max_age < vals.get('child_age'):
                    raise UserError(
                        _('Your child is over age for the Education Assistance please contact your higher authority'))
                if education_eligibility_id.child_min_age > vals.get('child_age'):
                    raise UserError(
                        _('Your child is under age for the Education Assistance please contact your higher authority'))

        vals['name'] = self.env['ir.sequence'].next_by_code('education.request.line') or _('New')
        res = super(EducationRequestLine, self).create(vals)
        return res

    @api.depends('child_id')
    def _compute_eligibility_amount(self):
        for rec in self:
            if rec.education_request_id.education_eligibility_id:
                if rec.education_request_id.education_eligibility_id.exception in ['no_exception', 'exception']:
                    rec.eligibility_amount = rec.education_request_id.education_eligibility_id.per_child_amount
                elif rec.education_request_id.education_eligibility_id.exception == 'specific_per_child':
                    child_line = rec.education_request_id.education_eligibility_id.specific_child_education_eligibility_line_ids.filtered(
                        lambda line: line.child_id.id == rec.child_id.id)
                    if child_line:
                        rec.eligibility_amount = child_line.specific_amount_for_child
                    else:
                        rec.eligibility_amount = 0.0
            else:
                rec.eligibility_amount = 0.0

    @api.depends('eligibility_amount', 'child_id')
    def _compute_approved_amount(self):
        for rec in self:
            approved_amount = 0.0
            employee_id = rec.education_request_id.employee_id
            academic_year = rec.education_request_id.academic_year
            previous_requests = self.env['education.request'].search(
                [('employee_id', '=', employee_id.id), ('academic_year', '=', academic_year.id),
                 ('request_status', '=', 'approved')])
            if previous_requests:
                for previous_request in previous_requests:
                    child_request_line = previous_request.request_lines.filtered(
                        lambda line: line.child_id == rec.child_id)
                    approved_amount += sum(child_request_line.terms_fees_line_ids.mapped(
                        'approve_amount'))
            rec.approved_amount = approved_amount

    @api.depends('eligibility_amount', 'approved_amount')
    def _compute_balance_amount(self):
        for rec in self:
            rec.balance_amount = rec.eligibility_amount - rec.approved_amount

    @api.onchange('child_id')
    def onchange_child_id(self):
        if self.education_request_id.employee_id.dependents:
            contact_relation_types = self.env['contact.relation.type'].search(
                [('name', 'in', ['Son', 'Child', 'Daughter'])])
            children = self.env['res.partner']
            children = self.education_request_id.employee_id.dependents.filtered(
                lambda x: x.contact_relation_type_id.id in contact_relation_types.ids)
            return {'domain': {'child_id': [('id', 'in', children.ids)]}}
        else:
            return {'domain': {'child_id': [('id', '=', -1)]}}
