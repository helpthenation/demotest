# -*- coding: utf-8 -*-
from odoo import models, fields, api
import pytz


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    processed = fields.Boolean(string="Processed", readonly=True)


class HrAttendanceProcessed(models.Model):
    _name = 'hr.attendance.processed'

    employee = fields.Many2one('hr.employee', string='Employee')
    company_employee_id = fields.Char(related='employee.company_employee_id', string="Employee Company Id")
    date = fields.Date(string="Date", readonly=True)
    weekday = fields.Selection(
        [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
         ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], string="WeekDay", readonly=True)
    emp_grade = fields.Many2one(related='employee.contract_id.job_grade', string="Employee Grade")
    shift = fields.Many2one('resource.calendar', string='Shift')
    variant = fields.Many2one('resource.calendar.variant', string='Variant')
    first_in = fields.Float(string='First In')
    last_out = fields.Float(string='Last Out')
    total_work_hours = fields.Float(string="Total Work Hours")
    day_status = fields.Selection(
        [('Pending', 'Pending'), ('Approval', 'Approval'), ('Approved', 'Approved'), ('Leave', 'Leave'),
         ('Single Swipe', 'Single Swipe'), ('Wrong Shift', 'Wrong Shift'), ('Action Required', 'Action Required')],
        default='Pending')
    early_leave = fields.Float(string='Early Leave')
    late_leave = fields.Float(string='Late Leave')
    mid_shift = fields.Float(string='Mid Shift')
    early_coming = fields.Float(string="Early Coming")
    late_coming = fields.Float(string="Late Coming")
    in_1 = fields.Float(string='In-1')
    out_1 = fields.Float(string='Out-1')
    in_2 = fields.Float(string='In-2')
    out_2 = fields.Float(string='Out-2')
    in_3 = fields.Float(string='In-3')
    out_3 = fields.Float(string='Out-3')
    in_4 = fields.Float(string='In-4')
    out_4 = fields.Float(string='Out-4')
    line_manager = fields.Many2one(related='employee.parent_id', string='Line Manager')
    line_manager_company_id = fields.Char(related='employee.parent_id.company_employee_id', string="Line Manager Company Id")
    contract_subgroup = fields.Many2one(related='employee.contract_id.contract_subgroup', string="Contract Subgroup")
    nationality = fields.Many2one(related='employee.country_id', string="Nationality")
    group = fields.Many2one(related='employee.contract_id.group', string='Group')
    department = fields.Many2one(related='employee.contract_id.department', string="Department")
    section = fields.Many2one(related='employee.contract_id.section', string='Section')
    sub_section = fields.Many2one(related='employee.contract_id.subsection', string='Sub Section')
    job_title = fields.Many2one(related='employee.contract_id.job_id.job_title', string='Job Title')
    company_name = fields.Many2one(related='employee.company_id', string="Company Name")

    def calculate_work(self):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  02/10/2020
            Func: Calculate attendances
            :return:
        """

        attendances = self.env['hr.attendance'].search([('processed', '=', False)])
        if attendances:
            for attendance in attendances:
                employee_res = self.env['hr.attendance'].search(
                    [('processed', '=', False), ('employee_id', '=', attendance.employee_id.id)])
                if employee_res:
                    for employee in employee_res:
                        create_date = self.env['hr.attendance'].search(
                            [('processed', '=', False), ('employee_id', '=', employee_res[0].employee_id.id),
                             ('check_in', '>=', employee.check_in.date()),
                             ('check_out', '<=', employee.check_in.date())], order='check_in')
                        if create_date:
                            if len(create_date) <= 1:
                                weekday = create_date.check_in.strftime('%A')
                                plan_slot = self.env['planning.slot'].search(
                                    [('employee_id', '=', create_date.employee_id.id),
                                     ('start_datetime', '>=', create_date.check_in.date()),
                                     ('start_datetime', '<=', create_date.check_out.date())], limit=1)
                                late_coming = ''
                                early_coming = ''
                                late_leave = ''
                                early_leave = ''
                                shift = ''
                                variant = ''
                                if plan_slot:
                                    variant = plan_slot.resource_calender_variant.id
                                    shift = plan_slot.resource_calender.id
                                    if plan_slot.start_datetime.time() < create_date.check_in.time():
                                        late_coming = create_date.check_in - plan_slot.start_datetime
                                        late_coming = late_coming.seconds / 60 / 60
                                    elif plan_slot.start_datetime.time() > create_date.check_in.time():
                                        early_coming = plan_slot.start_datetime - create_date.check_in
                                        early_coming = early_coming.seconds / 60 / 60
                                    if plan_slot.end_datetime.time() < create_date.check_out.time():
                                        late_leave = create_date.check_out - plan_slot.end_datetime
                                        late_leave = late_leave.seconds / 60 / 60
                                    elif plan_slot.end_datetime.time() > create_date.check_out.time():
                                        early_leave = plan_slot.end_datetime - create_date.check_out
                                        early_leave = early_leave.seconds / 60 / 60

                                if not create_date.processed:
                                    first_in = self.convert_datetime_to_float(
                                        self.convert_utc_time(create_date.check_in).strftime("%H-%M"))
                                    last_out = self.convert_datetime_to_float(
                                        self.convert_utc_time(create_date.check_out).strftime("%H-%M"))
                                    in_1 = first_in
                                    out_1 = last_out
                                    attendance_val = {'employee': create_date.employee_id.id,
                                                      'date': create_date.check_in.date(),
                                                      'last_out': last_out,
                                                      'first_in': first_in,
                                                      'weekday': weekday,
                                                      'in_1': in_1,
                                                      'out_1': out_1,
                                                      'total_work_hours': create_date.worked_hours,
                                                      'variant': variant,
                                                      'shift': shift,
                                                      'late_coming': late_coming,
                                                      'early_coming': early_coming,
                                                      'late_leave': late_leave,
                                                      'early_leave': early_leave}
                                    self.create([attendance_val])
                                    create_date.write({'processed': True})
                                    self._cr.commit()
                            else:
                                attendance_val = {}
                                tag = 1
                                mid_shift_1 = 0.0
                                mid_shift_2 = 0.0
                                mid_shift_3 = 0.0
                                total_work_hours = 0.0
                                for rec in create_date:
                                    if not rec.processed:
                                        plan_slot = self.env['planning.slot'].search(
                                            [('employee_id', '=', rec.employee_id.id),
                                             ('start_datetime', '>=', rec.check_in.date()),
                                             ('start_datetime', '<=', rec.check_out.date())], limit=1)
                                        if tag == 1:
                                            late_coming = ''
                                            early_coming = ''
                                            late_leave = ''
                                            early_leave = ''
                                            shift = ''
                                            variant = ''
                                            if plan_slot:
                                                variant = plan_slot.resource_calender_variant.id
                                                shift = plan_slot.resource_calender.id
                                                if plan_slot.start_datetime.time() < rec.check_in.time():
                                                    late_coming = rec.check_in - plan_slot.start_datetime
                                                    late_coming = late_coming.seconds / 60 / 60
                                                elif plan_slot.start_datetime.time() > rec.check_in.time():
                                                    early_coming = plan_slot.start_datetime - rec.check_in
                                                    early_coming = early_coming.seconds / 60 / 60
                                                if plan_slot.end_datetime.time() < rec.check_out.time():
                                                    late_leave = rec.check_out - plan_slot.end_datetime
                                                    late_leave = late_leave.seconds / 60 / 60
                                                elif plan_slot.end_datetime.time() > rec.check_out.time():
                                                    early_leave = plan_slot.end_datetime - rec.check_out
                                                    early_leave = early_leave.seconds / 60 / 60

                                            first_in = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_in).strftime("%H-%M"))
                                            in_1 = first_in
                                            out_1 = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_out).strftime("%H-%M"))
                                            last_out = out_1
                                            mid_shift_1 = rec.check_out
                                            weekday = rec.check_in.strftime('%A')
                                            total_work_hours += rec.worked_hours
                                            attendance_val.update({'employee': rec.employee_id.id,
                                                                   'date': rec.check_in.date(),
                                                                   'weekday': weekday,
                                                                   'first_in': first_in,
                                                                   'last_out': last_out,
                                                                   'in_1': in_1,
                                                                   'out_1': out_1,
                                                                   'total_work_hours': total_work_hours,
                                                                   'variant': variant,
                                                                   'shift': shift,
                                                                   'late_coming': late_coming or '',
                                                                   'early_coming': early_coming or '',
                                                                   'early_leave': early_leave or '',
                                                                   'late_leave': late_leave or '',
                                                                   })
                                            rec.write({'processed': True})
                                            tag += 1
                                        elif tag == 2:
                                            plan_slot = self.env['planning.slot'].search(
                                                [('employee_id', '=', rec.employee_id.id),
                                                 ('start_datetime', '>=', rec.check_in.date()),
                                                 ('start_datetime', '<=', rec.check_out.date())], limit=1)
                                            late_leave = ''
                                            early_leave = ''
                                            if plan_slot:
                                                if plan_slot.end_datetime.time() < rec.check_out.time():
                                                    late_leave = rec.check_out - plan_slot.end_datetime
                                                    late_leave = late_leave.seconds / 60 / 60
                                                elif plan_slot.end_datetime.time() > rec.check_out.time():
                                                    early_leave = plan_slot.end_datetime - rec.check_out
                                                    early_leave = early_leave.seconds / 60 / 60
                                            last_out = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_out).strftime("%H-%M"))
                                            in_2 = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_in).strftime("%H-%M"))
                                            out_2 = last_out
                                            mid_shift_1 = self.convert_utc_time(mid_shift_1)
                                            check_in = self.convert_utc_time(rec.check_in)
                                            mid_shift_1 = check_in - mid_shift_1
                                            mid_shift_1 = mid_shift_1.seconds / 60
                                            mid_shift_2 = rec.check_out
                                            total_work_hours += rec.worked_hours
                                            attendance_val.update({'last_out': last_out,
                                                                   'in_2': in_2,
                                                                   'out_2': out_2,
                                                                   'mid_shift': mid_shift_1 / 60,
                                                                   'total_work_hours': total_work_hours,
                                                                   'late_leave': late_leave or '',
                                                                   'early_leave': early_leave or '',
                                                                   }),

                                            rec.write({'processed': True})
                                            tag += 1
                                        elif tag == 3:
                                            plan_slot = self.env['planning.slot'].search(
                                                [('employee_id', '=', rec.employee_id.id),
                                                 ('start_datetime', '>=', rec.check_in.date()),
                                                 ('start_datetime', '<=', rec.check_out.date())], limit=1)
                                            late_leave = ''
                                            early_leave = ''
                                            if plan_slot:
                                                if plan_slot.end_datetime.time() < rec.check_out.time():
                                                    late_leave = rec.check_out - plan_slot.end_datetime
                                                    late_leave = late_leave.seconds / 60 / 60
                                                elif plan_slot.end_datetime.time() > rec.check_out.time():
                                                    early_leave = plan_slot.end_datetime - rec.check_out
                                                    early_leave = early_leave.seconds / 60 / 60
                                            last_out = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_out).strftime("%H-%M"))
                                            in_3 = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_in).strftime("%H-%M"))
                                            out_3 = last_out
                                            mid_shift_2 = self.convert_utc_time(mid_shift_2)
                                            check_in = self.convert_utc_time(rec.check_in)
                                            mid_shift_2 = check_in - mid_shift_2
                                            mid_shift_2 = mid_shift_2.seconds / 60
                                            mid_shift_3 = rec.check_out
                                            total_work_hours += rec.worked_hours
                                            attendance_val.update({'last_out': last_out,
                                                                   'in_3': in_3,
                                                                   'out_3': out_3,
                                                                   'mid_shift': (mid_shift_2 + mid_shift_1) / 60,
                                                                   'total_work_hours': total_work_hours,
                                                                   'late_leave': late_leave or '',
                                                                   'early_leave': early_leave or '',
                                                                   }),
                                            rec.write({'processed': True})
                                            tag += 1
                                        elif tag == 4:

                                            plan_slot = self.env['planning.slot'].search(
                                                [('employee_id', '=', rec.employee_id.id),
                                                 ('start_datetime', '>=', rec.check_in.date()),
                                                 ('start_datetime', '<=', rec.check_out.date())], limit=1)
                                            late_leave = ''
                                            early_leave = ''
                                            if plan_slot:
                                                if plan_slot.end_datetime.time() < rec.check_out.time():
                                                    late_leave = rec.check_out - plan_slot.end_datetime
                                                    late_leave = late_leave.seconds / 60 / 60
                                                elif plan_slot.end_datetime.time() > rec.check_out.time():
                                                    early_leave = plan_slot.end_datetime - rec.check_out
                                                    early_leave = early_leave.seconds / 60 / 60
                                            last_out = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_out).strftime("%H-%M"))
                                            in_4 = self.convert_datetime_to_float(
                                                self.convert_utc_time(rec.check_in).strftime("%H-%M"))
                                            out_4 = last_out
                                            mid_shift_3 = self.convert_utc_time(mid_shift_3)
                                            check_in = self.convert_utc_time(rec.check_in)
                                            mid_shift_3 = check_in - mid_shift_3
                                            mid_shift_3 = mid_shift_3.seconds / 60
                                            mid_shift = (mid_shift_1 + mid_shift_2 + mid_shift_3) / 60
                                            total_work_hours += rec.worked_hours
                                            attendance_val.update({'last_out': last_out,
                                                                   'in_4': in_4,
                                                                   'out_4': out_4,
                                                                   'mid_shift': mid_shift,
                                                                   'total_work_hours': total_work_hours,
                                                                   'late_leave': late_leave or '',
                                                                   'early_leave': early_leave or '',
                                                                   }),
                                            rec.write({'processed': True})
                                            tag += 1
                                self.create([attendance_val])
                                self._cr.commit()
        return True

    @api.model
    def convert_datetime_to_float(self, date):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  09/10/2020
            Func: convert time hours,minute into the float
            :return: float time
        """
        time = '0.0'
        if date:
            time = date.split('-')
            if len(time) >= 2:
                float_val = float("0" + "." + time[1])
                time[1] = str(round((float_val % 1) * 167))
                if len(time[1]) < 2:
                    time[1] = str('0' + time[1])
            time = ".".join(time)
        return time

    @api.model
    def convert_utc_time(self, time):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  09/10/2020
            Func: convert local time to utc time
            :return: local time
        """
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        time = pytz.utc.localize(time).astimezone(user_tz)
        return time

    def name_get(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:12/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for employee in self:
            if employee.employee:
                name = employee.employee.name
                result.append((employee.id, name))
        return result
