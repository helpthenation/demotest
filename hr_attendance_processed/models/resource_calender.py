# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from odoo.exceptions import Warning
import pytz


class ResourceCalenderVariant(models.Model):
    _name = 'resource.calendar.variant'
    _description = "Resource Calendar Variant"

    code = fields.Char(string='Code')
    name = fields.Char()
    related_resource_calender = fields.Many2one('resource.calendar', string='Related Resource Calendar')
    Duration = fields.Float(string='Duration')


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    resource_variant_id = fields.Many2one('resource.calendar.variant', string='Resource Calendar Variant')


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    break_time = fields.Float(string='Break')
    net_hours = fields.Float(string='Net Hours', compute='_compute_net_hours')

    def _compute_net_hours(self):
        for rec in self:
            rec.net_hours = rec.hour_to - rec.hour_from - rec.break_time


class HrEmployeeShift(models.Model):
    _name = 'hr.employee.shift'
    _description = "Employee Shift"

    related_employee = fields.Many2one('hr.employee', string='Related Employee')
    resource_calender = fields.Many2one('resource.calendar', string='Monthly Shift')
    resource_calender_attendance = fields.Many2one('resource.calendar.attendance',
                                                   string="Weekly Shift")
    resource_calender_variant = fields.Many2one('resource.calendar.variant',
                                                string="Resource Calendar Variant")
    active = fields.Boolean(string='Active', default=True)

    def name_get(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:12/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for employee in self:
            if employee.related_employee:
                name = employee.related_employee.name
                result.append((employee.id, name))
        return result


class Planning(models.Model):
    _inherit = 'planning.slot'

    resource_calender = fields.Many2one('resource.calendar', string='Monthly Shift')
    resource_calender_attendance = fields.Many2one('resource.calendar.attendance',
                                                   string="Weekly Shift")
    resource_calender_variant = fields.Many2one('resource.calendar.variant',
                                                string="Weekly Shift")

    starttime = fields.Float(string="Start Time")
    endtime = fields.Char(string="End Time")

    template_id = fields.Many2one(store=True)

    @api.onchange('start_datetime', 'end_datetime')
    def onchange_date(self):
        self.starttime = self.template_id.start_time
        self.endtime = (
                self.template_id.start_time + self.template_id.duration) if self.template_id.start_time + self.template_id.duration < 24 else self.template_id.start_time + self.template_id.duration - 24

    def create_planning_slot_rec(self):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  02/10/2020
            Func: Calculate attendances
            :return:
        """
        utc = pytz.utc
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            if employee.contract_id.resource_calendar_id:
                resource_calender = self.env['resource.calendar'].search(
                    [('id', '=', employee.contract_id.resource_calendar_id.id)])
                if resource_calender:
                    month = (datetime.now() + relativedelta(months=1)).month
                    year = (datetime.now() + relativedelta(months=1)).year
                    total_month_days = calendar.mdays[month]

                    for day in range(total_month_days):
                        start_time = 0.0
                        end_time = 0.0
                        date = str(year) + str(month) + str(day + 1)
                        date = datetime.strptime(date, '%Y%m%d').date()
                        planning = self.env['planning.slot'].search([('start_datetime', '=', date)])
                        if not len(planning) >= 1:
                            day = date.strftime('%A')
                            attendance_id = ''
                            shift_tag = True
                            for attendance in resource_calender.attendance_ids:
                                att_day = attendance.name.split(' ')[0]
                                if att_day == day:
                                    if shift_tag:
                                        attendance_id = attendance
                                        start_time = attendance.hour_from
                                        shift_tag = False
                                        end_time = attendance.hour_to
                            if len(attendance_id) >= 1:
                                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                                # formats = '%Y-%m-%d %H:%M:%S %Z%z'

                                # # Added Random dates cuz of get the timezone value
                                # tz_val = user_tz.localize(datetime(2020, 10, 12, 6, 0, 0)).strftime(formats).split(' ')
                                # if tz_val:
                                #     tz_val = tz_val[2][4:]
                                #     tz_val = float(tz_val) / 100
                                #     tz_val = float(self.convert_datetime_to_float(str(tz_val)))

                                hours_from = self.convert_float_to_datetime(
                                    str(start_time))
                                hours_to = self.convert_float_to_datetime(
                                    str(end_time))

                                hours_from = str(hours_from).split('.')
                                hours_to = str(hours_to).split('.')
                                if len(hours_from[0]) <= 1:
                                    hours_from[0] = "0" + hours_from[0]
                                if len(hours_from[1]) <= 1:
                                    hours_from[1] = "0" + hours_from[1]
                                hours_from = hours_from[0] + ':' + hours_from[1]
                                if len(hours_to[0]) <= 1:
                                    hours_to[0] = "0" + hours_to[0]
                                if len(hours_to[1]) <= 1:
                                    hours_to[1] = "0" + hours_to[1]
                                hours_to = hours_to[0] + ':' + hours_to[1]

                                start_datetime = str(date) + " " + hours_from + ":00"
                                end_datetime = str(date) + " " + hours_to + ":00"
                                planning_slot_val = {'resource_calender': resource_calender.id or '',
                                                     'employee_id': employee.id or '',
                                                     'resource_calender_attendance': attendance_id.id or '',
                                                     'resource_calender_variant': resource_calender.resource_variant_id.id or '',
                                                     'start_datetime': (user_tz.localize(
                                                         datetime.strptime(start_datetime,
                                                                           '%Y-%m-%d %H:%M:%S')).astimezone(
                                                         utc)).replace(tzinfo=None) or '',
                                                     'end_datetime': (user_tz.localize(
                                                         datetime.strptime(end_datetime,
                                                                           '%Y-%m-%d %H:%M:%S')).astimezone(
                                                         utc)).replace(tzinfo=None) or '',
                                                     }
                                try:
                                    planning_slot = self.env['planning.slot'].search(
                                        [('employee_id', '=', employee.id), ('start_datetime', '=', start_datetime),
                                         ('end_datetime', '=', end_datetime)])
                                    if not len(planning_slot) >= 1:
                                        planning_slot.create(planning_slot_val)
                                        self._cr.commit()

                                except Exception as e:
                                    raise Warning(e)

    @api.model
    def find_weekday(self, day):
        date = datetime.today()
        while True:
            if date.strftime('%A') == day:
                break
            else:
                date = date + timedelta(days=1)
                continue
        return date

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
            time = date.split('.')
            if len(time) >= 2:
                float_val = float("0" + "." + time[1])
                time[1] = str(round((float_val % 1) * 165))
            time = ".".join(time)
        return time

    @api.model
    def convert_float_to_datetime(self, date):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  09/10/2020
            Func: convert float to hours,minute datetime
            :return: datetime
        """
        time = '0.0'
        if date:
            time = date.split('.')
            if len(time) >= 2:
                float_val = float("0" + "." + time[1])
                time[1] = str(round((float_val % 1) * 60))
            time = ".".join(time)
        return time
