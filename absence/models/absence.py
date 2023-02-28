from odoo import api, fields, models
import datetime


class HrAbsence(models.Model):
    _name = 'attendance.absence'

    name = fields.Many2one('hr.employee', "Employee")
    date = fields.Date("Date")

    @api.model
    def compute_absent_employees(self):
        today = datetime.datetime.now()
        dayweek = today.weekday()
        employees_who_should_work_today = self.env['resource.calendar.attendance'].search([
            ('dayofweek', '=', dayweek)])
        calendar_ids = employees_who_should_work_today.mapped('calendar_id')
        employee_ids = self.env['hr.employee'].search([('resource_calendar_id', 'in', calendar_ids._ids)])
        leave_ids = self.env['hr.leave'].search([
            ('request_date_from', '>=', today.date()),
            ('request_date_to', '<=', today.date()),
            ('state', '=', 'validate'),
        ])
        l_employee_ids = leave_ids.mapped('employee_id')
        attendance_ids = self.env['hr.attendance'].search([
            ('check_in', '>', today.replace(hour=8, minute=0))
        ])
        a_employee_ids = attendance_ids.mapped('employee_id')
        a_employee_ids |= l_employee_ids
        employee_ids -= a_employee_ids
        print(employee_ids)
        for employee in employee_ids:
            self.create({
                'name': employee.id,
                'date': today.date()
            })
