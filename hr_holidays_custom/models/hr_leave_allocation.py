# -*- coding: utf-8 -*-

from odoo.exceptions import Warning
from odoo import fields, models, api
from datetime import date
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

Religions_list = [
    ('apostolic', 'Apostolic'),
    ('baptist', 'Baptist'),
    ('buddhist', 'Buddhist'),
    ('charismatic', 'Charismatic'),
    ('evang', 'Evang'),
    ('lutheran-church', 'Lutheran Church'),
    ('evangelical', 'Evangelical'),
    ('free-church-alzey', 'Free church Alzey'),
    ('free-religion-of-the-den', 'Free religion of the den'),
    ('french-reformed', 'French reformed'),
    ('hebrew-reg-baden', 'Hebrew reg. BADEN'),
    ('hebrew-reg-wuertbg', 'Hebrew reg. WUERTBG'),
    ('hebrew-state', 'Hebrew state'),
    ('hindu', 'Hindu'),
    ('islamic', 'Islamic'),
    ('israelite', 'Israelite'),
    ("jehovah-s-witness", "Jehovah's witness"),
    ('mennonite-church', 'Mennonite Church'),
    ('jewish', 'Jewish'),
    ('mennonite-church', 'Mennonite Church'),
    ('mormon', 'Mormon'),
    ('moravian-congregation', 'Moravian Congregation'),
    ('muslim', 'Muslim'),
    ('netherl', 'Netherl'),
    ('netherl-reformed-church', 'Netherl. Reformed Church'),
    ('new-apostolic', 'New apostolic'),
    ('no-denomination', 'No denomination'),
    ('old-catholic', 'Old Catholic'),
    ('oecumenic', 'Oecumenic'),
    ('protestant', 'Protestant'),
    ('roman-catholic', 'Roman Catholic'),
    ("shia-muslim", "Shi'a Muslim"),
    ('sunni-muslim', 'Sunni Muslim'),
    ('christian', 'Christian'),
    ('christian-reformed', 'Christian Reformed'),
]


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"
    _description = "Time Off Allocation"

    grade_id = fields.Many2one('job.grade', 'Grade')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    holiday_type = fields.Selection(selection_add=[('grade', 'By Grade'), ('employees', 'By Employees'),
                                                   ('multiple_criteria', 'Multiple Criteria')])
    contract_group = fields.Many2one('hr.contract.group', string='Contract Group')
    contract_subgroup = fields.Many2one('hr.contract.subgroup', string="Contract Subgroup")
    country_id = fields.Many2one('res.country', string="Country")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    religion = fields.Selection(Religions_list, 'Religion')
    encash_leave = fields.Float(string="Encash Leave", default=0.0, readonly=True)
    is_carry_forward = fields.Boolean(string='Carry Forward', default=False)
    # add by bhavesh jadav
    state = fields.Selection(selection_add=[('expired', 'Expired')])
    allocation_from_date = fields.Date(string="From Date")
    allocation_to_date = fields.Date(string="To Date")

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL) or "
         "(holiday_type='grade' AND grade_id IS NOT NULL) or"
         "(holiday_type='employees' AND holiday_status_id IS NOT NULL) or "
         "(holiday_type='multiple_criteria' AND holiday_status_id IS NOT NULL))",
         "The employee, department, company or employee category , employee grade  of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)",
         "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]

    def action_expired(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 08/12/2020
        @Func: this method use for the expire allocation from the button also from the  carried forward cron
        @Return:True
        """
        validated_holidays = self.filtered(lambda hol: hol.state != 'expired')
        validated_holidays.write({'state': 'expired'})
        # If a category that created several holidays, expire all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests = self.env['hr.leave.allocation'].browse(linked_requests)
            linked_requests.action_expired()
        self.activity_update()
        return True

    @api.model
    def create(self, vals):
        if vals.get('holiday_type') and vals.get('holiday_type') == 'multiple_criteria':
            if not vals.get('grade_id') and not vals.get('contract_group') and not vals.get(
                    'contract_subgroup') and not vals.get('country_id') and not vals.get('gender') and not vals.get(
                'religion'):
                raise UserError('You can not create with blank criteria please select any criteria! ')
        res = super(HolidaysAllocation, self).create(vals)
        return res

    def action_approve(self):
        res = super(HolidaysAllocation, self).action_approve()
        for allocation in self:
            if allocation and allocation.employee_id and allocation.employee_id.gender:
                if self.holiday_status_id and self.holiday_status_id.category:
                    if self.holiday_status_id.category == "paternity" and self.employee_id.gender == 'female':
                        raise Warning(
                            "Allocation Can't approve for the Employee gender 'female' and time off type category"
                            " 'paternity'")
                    if self.holiday_status_id.category == "maternity" and self.employee_id.gender == 'male':
                        raise Warning(
                            "Allocation Can't approve for the Employee gender 'male' and time off type category 'maternity'")
        return res

    def _prepare_holiday_values(self, employee):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date: 08/12/2020
        @Func:this method inherit for the add from date and the to date in the child allocation base on the parent allocation
        @Return:res : result of the supper call

        """
        res = super(HolidaysAllocation, self)._prepare_holiday_values(employee)
        res.update({'allocation_to_date': self.allocation_to_date, 'allocation_from_date': self.allocation_from_date})
        return res

    def leave_encasement_and_carry_forward(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:08/12/2020
        @Func: this cron method use for the create carried forward leaves allocation for the employee and the expire the parent alocation base on the date and
            we are user only the employee regular allocation with the Time Off Type	category is annual
        @Return:NA
        """
        employee_ids = self.env['hr.employee'].search([])
        for employee_id in employee_ids:
            carry_forward_rule = self.env['carried.forward.settings']
            carry_forward_rule = self.env['carried.forward.settings'].search(
                [('employee_ids', '=', employee_id.id)])
            if not carry_forward_rule:
                carry_forward_rule = self.env['carried.forward.settings'].search(
                    [('apply_for_all_employee', '=', True)], limit=1)
            employee_allocation_ids = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', employee_id.id), ('state', '=', 'validate'), ('holiday_type', '=', 'employee'),
                 ('allocation_to_date', '<=', date.today()), ('holiday_status_id.category', '=', 'annual')])
            carry_forward_allcation_ids = self.env['hr.leave.allocation'].search(
                [('is_carry_forward', '=', True), ('holiday_type', '=', 'employee'),
                 ('employee_id', '=', employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.category', '=', 'annual'), ('allocation_type', '=', 'regular')])
            employee_allocation_ids = employee_allocation_ids + carry_forward_allcation_ids
            if not employee_allocation_ids:
                continue
            number_of_days = employee_allocation_ids.mapped('number_of_days')
            leaves_taken = employee_allocation_ids.mapped('leaves_taken')
            remain_leave = float(sum(number_of_days)) - float(sum(leaves_taken))
            if carry_forward_rule and remain_leave > 0:
                carry_forward_leave = 0
                encasement_leave = 0
                if carry_forward_rule.carry_forward == 'all':
                    carry_forward_leave = remain_leave
                elif carry_forward_rule.carry_forward == 'specific_number':
                    if remain_leave >= carry_forward_rule.num_of_leave_for_carry_forward:
                        carry_forward_leave = carry_forward_rule.num_of_leave_for_carry_forward
                    else:
                        carry_forward_leave = remain_leave
                if carry_forward_rule.encashment == 'all_remaining':
                    encasement_leave = remain_leave - carry_forward_leave
                elif carry_forward_rule.encashment == 'specific_number_of_remaining':
                    if carry_forward_leave > 0 and (
                            remain_leave - carry_forward_leave) >= carry_forward_rule.encashment_number:
                        encasement_leave = carry_forward_rule.encashment_number
                    else:
                        encasement_leave = 0.0
                elif carry_forward_rule.encashment == 'percentage_of_remaining':
                    if carry_forward_rule.encashment_percentage > 0 and carry_forward_leave > 0:
                        try:
                            encasement_leave = ((
                                                        carry_forward_rule.encashment_percentage * (
                                                        remain_leave - carry_forward_leave)) / 100)
                        except Exception as e:
                            _logger.info('Error when percentage calculate: {}'.format(e))
                            encasement_leave = 0
                name = str(employee_id.name) + '-' + 'Carried Forward Allocation'
                if carry_forward_leave > 0:
                    vals = {'name': name,
                            'holiday_status_id': employee_allocation_ids[0].holiday_status_id.id,
                            'allocation_type': 'regular',
                            'number_of_days': carry_forward_leave,
                            'number_per_interval': 1,
                            'interval_number': 1,
                            'unit_per_interval': 'days',
                            'interval_unit': 'weeks',
                            'encash_leave': encasement_leave,
                            'is_carry_forward': True,
                            'employee_id': employee_id.id}
                    try:
                        rec = self.env['hr.leave.allocation'].sudo().create(vals)
                        employee_allocation_ids.write({'state': 'expired'})
                        self._cr.commit()
                    except Exception as e:
                        _logger.info('Error when create allocation from cron : {}'.format(e))
            else:
                employee_allocation_ids.action_expired()

    def _action_validate_create_childs(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:11/12/2020
        @Func: This Method override for the override for the add new mode in allocation
        @Return:childs allocation ids
        """
        childs = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['category', 'department', 'company', 'grade',
                                                              'employees', 'multiple_criteria']:
            employees = self.env['hr.employee']
            if self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            elif self.holiday_type == 'grade':
                self.employee_id = employees = self.env['hr.employee']
                employees = self.env['hr.employee'].search([('contract_id.job_grade', '=', self.grade_id.id)])
            elif self.holiday_type == 'employees':
                self.employee_id = employees = self.env['hr.employee']
                employees = self.employee_ids
            elif self.holiday_type == 'multiple_criteria':
                self.employee_id = employees = self.env['hr.employee']
                domain = []
                if self.grade_id:
                    domain.append(('contract_id.job_grade', '=', self.grade_id.id))
                if self.contract_group:
                    domain.append(('contract_id.contract_group', '=', self.contract_group.id))
                if self.contract_subgroup:
                    domain.append(('contract_id.contract_subgroup', '=', self.contract_subgroup.id))
                if self.country_id:
                    domain.append(('country_id', '=', self.country_id.id))
                if self.gender:
                    domain.append(('gender', '=', self.gender))
                if self.religion:
                    domain.append(('religion', '=', self.religion))
                if domain:
                    employees = self.env['hr.employee'].search(domain)
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])

            for employee in employees:
                childs += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))
            # TODO is it necessary to interleave the calls?
            childs.action_approve()
            if childs and self.holiday_status_id.validation_type == 'both':
                childs.action_validate()
        return childs
