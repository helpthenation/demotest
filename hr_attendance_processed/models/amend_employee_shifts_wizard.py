from odoo import fields, models, api
from datetime import datetime
from datetime import date, timedelta
import pytz


class AmendEmployeeShifts(models.TransientModel):
    _name = 'amend.shifts'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    template_id = fields.Many2one(comodel_name='planning.slot.template', string='Daily Shift', required=True)
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Employees', required=True)

    def amend_employee_shifts(self):
        utc = pytz.utc
        employees = self.employee_ids
        from_date = self.from_date
        to_date = self.to_date
        initial_from = from_date
        delta = timedelta(days=1)
        template_id = self.template_id
        old_shifts = self.env['planning.slot'].search([('employee_id', 'in', employees.ids)])
        for old_shift in old_shifts:
            if from_date <= old_shift.start_datetime.date() <= to_date:
                old_shift.unlink()
        for employee in employees:
            from_date = initial_from
            while from_date <= to_date:
                start_time = 0.0
                end_time = 0.0
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)

                hours_from = self.convert_float_to_datetime(str(template_id.start_time))
                add_day = False
                if template_id.start_time + template_id.duration < 24:
                    hours_to = self.convert_float_to_datetime(str((template_id.start_time + template_id.duration)))
                else:
                    hours_to = self.convert_float_to_datetime(str((template_id.start_time + template_id.duration - 24)))
                    add_day = True

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

                start_datetime = str(from_date) + " " + hours_from + ":00"
                if not add_day:
                    end_datetime = str(from_date) + " " + hours_to + ":00"
                else:
                    end_datetime = str(from_date + timedelta(days=1)) + " " + hours_to + ":00"

                planning_slot_val = {'resource_calender': employee.contract_id.resource_calendar_id.id or '',
                                     'employee_id': employee.id or '',
                                     'template_id': template_id.id or '',
                                     # 'resource_calender_attendance': attendance_id.id or '',
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
                        new_slot = planning_slot.create(planning_slot_val)
                        new_slot.onchange_date()
                        self._cr.commit()

                except Exception as e:
                    raise Warning(e)
                from_date += delta

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
