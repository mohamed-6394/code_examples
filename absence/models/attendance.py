# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSD, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTM
from odoo.exceptions import UserError, ValidationError


# from odoo.tools.translate import _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    lateness_hours = fields.Float("Monthly Late Hours", compute='_compute_lateness_hours')
    over_time = fields.Float("Monthly Over Hours", compute='_compute_overTime_hours')
    late_hours = fields.Float(string="Daily Late Hours", compute='_compute_lateness_hours')
    over_hours = fields.Float(string="Daily Over Hours", compute='_compute_overTime_hours')
    monthly_worked_hours = fields.Float(string="Monthly Worked Hours", compute='_compute_workedHours_hours')
    lateHour_bool = fields.Boolean("Edit in Daily Late Hours")
    overHour_bool = fields.Boolean("Edit in Daily over Hours")
    edited_late_hours = fields.Float("Daily Late Hours")
    edited_over_hours = fields.Float("Daily Over Hours")
    total_late_deduction = fields.Float("Total late Deduction")
    late_rate = fields.Float(default=0.0)

    @api.depends('check_in', 'check_out')
    def _compute_lateness_hours(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        for rec in self:
            exact_time = 0
            total_lateness = 0
            total_late_deduction = 0
            month = datetime.datetime.now().month
            all_attendance = self.search([('employee_id', '=', rec.employee_id.id)])
            wHour = rec.employee_id.resource_calendar_id.attendance_ids
            allowed_hour = rec.employee_id.attendance_policy_id.hours
            late_policy = rec.employee_id.attendance_policy_id.late_policy
            late_times = []
            max_time = 0
            for late_py in late_policy:
                late_times.append(late_py.absence_times)
            for time in late_times:
                if int(time) > max_time:
                    max_time = int(time)
            if rec.check_in:
                check_in_convert_time_zone = datetime.datetime.strftime(
                    pytz.utc.localize(
                        datetime.datetime.strptime(str(rec.check_in), DTM)).astimezone(
                        local), "%Y-%m-%d %H:%M:%S")
                check_in_convert = datetime.datetime.strptime(str(check_in_convert_time_zone), "%Y-%m-%d %H:%M:%S")
                # print(check_in_convert)

                for line in wHour:
                    if int(rec.check_in.weekday()) == int(line.dayofweek):
                        exact_float_check_in = float((check_in_convert.hour + (check_in_convert.minute / 60)))
                        if exact_float_check_in > line.hour_from:
                            exact_time = exact_float_check_in - line.hour_from
                if not rec.employee_id.late_refuse:
                    if exact_time:
                        rec.late_rate += 1
                        if rec.check_in.month == month:
                            for lp in late_policy:
                                wage = self.env["hr.contract"].search(
                                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1).wage
                                if rec.late_rate == lp.absence_times:
                                    total_late_deduction += (wage/30) * lp.absence_rate
                                elif rec.late_rate > max_time:
                                    for lp2 in late_policy:
                                        if max_time == lp.absence_times:
                                            total_late_deduction += (wage/30) * lp2.absence_rate
                    rec.total_late_deduction = total_late_deduction
                    print(rec.total_late_deduction)

                    rec.late_hours = exact_time
                else:
                    rec.late_hours = 0
                if rec.lateHour_bool:
                    rec.late_hours = rec.edited_late_hours
                for attend in all_attendance:
                    if attend.check_in:
                        if attend.check_in.month == month:
                            total_lateness = total_lateness + attend.late_hours
                total_lateness = total_lateness - allowed_hour
                if total_lateness < 0:
                    total_lateness = 0
            else:
                rec.late_hours = 0.0
        rec.lateness_hours = total_lateness

    @api.depends('worked_hours')
    def _compute_overTime_hours(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        for rec in self:
            applyAfter = rec.employee_id.attendance_policy_id.apply_after
            work_hour = rec.employee_id.resource_calendar_id.hours_per_day + applyAfter
            # print(applyAfter)
            over_hours = 0
            worked_hour = 0
            total_overTime = 0
            month = datetime.datetime.now().month
            all_overTime = self.search([('employee_id', '=', rec.employee_id.id)])
            wHour = rec.employee_id.resource_calendar_id.attendance_ids
            if rec.check_in:
                check_in_convert_time_zone = datetime.datetime.strftime(
                    pytz.utc.localize(
                        datetime.datetime.strptime(str(rec.check_in), DTM)).astimezone(
                        local), "%Y-%m-%d %H:%M:%S")
                check_in_convert = datetime.datetime.strptime(str(check_in_convert_time_zone), "%Y-%m-%d %H:%M:%S")
                for line in wHour:
                    if int(rec.check_in.weekday()) == int(line.dayofweek):
                        exact_float_check_in = float((check_in_convert.hour + (check_in_convert.minute / 60)))
                        if exact_float_check_in >= line.hour_from:
                            worked_hour = rec.worked_hours
                        else:
                            worked_hour = rec.worked_hours - (line.hour_from - exact_float_check_in)
            if rec.worked_hours > work_hour:
                over_hours = worked_hour - work_hour
            if not rec.employee_id.over_refuse:
                rec.over_hours = over_hours
            else:
                rec.over_hours = 0
            if rec.overHour_bool:
                rec.over_hours = rec.edited_over_hours
            for over in all_overTime:
                if over.check_in:
                    if over.check_in.month == month:
                        total_overTime = total_overTime + over.over_hours
            rec.over_time = total_overTime

    @api.depends('worked_hours')
    def _compute_workedHours_hours(self):
        for rec in self:
            total_worked_hours = 0
            month = datetime.datetime.now().month
            all_worked_hours = self.search([('employee_id', '=', rec.employee_id.id)])
            if all_worked_hours:
                for wh in all_worked_hours:
                    if wh.check_in:
                        if wh.check_in.month == month:
                            total_worked_hours += wh.worked_hours
            rec.monthly_worked_hours = total_worked_hours
