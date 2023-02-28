from odoo import api, fields, models,_
import datetime


class EmployeeTaxes(models.Model):
    _inherit = 'hr.contract'

    yearly_taxes = fields.Float('Yearly Taxes', compute="_compute_employee_taxes")
    monthly_taxes = fields.Float('Monthly Taxes', compute="_compute_employee_taxes")

    def _compute_employee_taxes(self):
        for rec in self:
            # deduction = self.env["hr.payslip"].search([('employee_id', '=', rec.employee_id.id)])
            month = datetime.datetime.now().month
            emp_wage = rec.wage - rec.employee_share
            # if rec.medical_information:
            #     emp_wage -= rec.medical_information_amount
            # for compute in deduction:
            #     if compute.date_from.month == month:
            #         if compute.state == "done":
            #             for table in compute.line_ids:
            #                 if table.category_id.name == "Deduction":
            #                     emp_wage -= (table.quantity * table.amount)
            yearly_wage = emp_wage * 12
            yearly_wage -= 9000
            if yearly_wage <= 15000:
                rec.yearly_taxes = rec.monthly_taxes = 0
            elif yearly_wage <= 30000:
                rec.yearly_taxes = (yearly_wage - 15000) * 0.025
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 45000:
                rec.yearly_taxes = ((yearly_wage - 30000) * 0.1) + 375
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 60000:
                rec.yearly_taxes = ((yearly_wage - 45000) * 0.15) + 375 + 1500
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 200000:
                rec.yearly_taxes = ((yearly_wage - 60000) * 0.2) + 375 + 1500 + 2250
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 400000:
                rec.yearly_taxes = ((yearly_wage - 200000) * 0.225) + 375 + 1500 + 2250 + 28000
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 600000:
                rec.yearly_taxes = ((yearly_wage - 400000) * 0.25) + 375 + 1500 + 2250 + 28000 + 45000
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 700000:
                rec.yearly_taxes = ((yearly_wage - 600000) * 0.25) + 750 + 1500 + 2250 + 28000 + 45000 + 50000
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 800000:
                rec.yearly_taxes = ((yearly_wage - 600000) * 0.25) + 4500 + 2250 + 28000 + 45000 + 50000
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 900000:
                rec.yearly_taxes = ((yearly_wage - 600000) * 0.25) + 9000 + 28000 + 45000 + 50000
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage <= 1000000:
                rec.yearly_taxes = ((yearly_wage - 600000) * 0.25) + 40000 + 45000 + 50000
                rec.monthly_taxes = rec.yearly_taxes / 12
            elif yearly_wage > 1000000:
                rec.yearly_taxes = ((yearly_wage - 600000) * 0.25) + 90000 + 50000
                rec.monthly_taxes = rec.yearly_taxes / 12
