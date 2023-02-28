from odoo import api, fields, models
import datetime


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    monthly_lateHours = fields.Float('Monthly Late Hours', compute='_get_monthly_late_hours')
    monthly_overHours = fields.Float('Monthly Over Hours', compute='_get_monthly_late_hours')
    monthly_worked_hours = fields.Float(string="Monthly Worked Hours", compute='_get_monthly_late_hours')
    total_late_deduction = fields.Float("Total late Deduction", compute='_get_monthly_late_hours')
    absent_days = fields.Integer(string="Absent Days", compute="_get_absent_days")
    has_insurance = fields.Boolean(string="Has Insurance?")
    over_refuse = fields.Boolean("Un compute Over Hours")
    late_refuse = fields.Boolean("Un compute Late Hours")
    attendance_policy_id = fields.Many2one('attendance.policy', string="Attendance Policy", required=True)

    def _get_absent_days(self):
        for rec in self:
            absent_creation = self.env['attendance.absence'].search([('name.id', '=', rec.id)])

            days = 0
            if absent_creation:
                month = datetime.datetime.now().month
                year = datetime.datetime.now().year
                for absent in absent_creation:
                    if year == absent.date.year:
                        if month == absent.date.month:
                            days += 1
                rec.absent_days = days
            else:
                rec.absent_days = 0

    def _get_monthly_late_hours(self):
        for rec in self:
            emp_id = self.env['hr.attendance'].search([('employee_id', '=', rec.id)], limit=1)
            rec.monthly_lateHours = emp_id.lateness_hours
            rec.monthly_overHours = emp_id.over_time
            rec.monthly_worked_hours = emp_id.monthly_worked_hours
            rec.total_late_deduction = emp_id.total_late_deduction



class EmployeePublicInherit(models.Model):
    _inherit = 'hr.employee.public'

    has_insurance = fields.Boolean(string="Has Insurance?")
