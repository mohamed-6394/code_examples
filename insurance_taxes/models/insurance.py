from odoo import api, fields, models
import datetime
import math


class EmployeeCompanyInsurance(models.Model):
    _inherit = 'hr.contract'

    employee_share = fields.Float('Employee Share', compute="_compute_employee_company_share")
    company_share = fields.Float('Company Share', compute="_compute_employee_company_share")

    # def current_range (year):
    #     start_year = 2020
    #     start = 1000
    #     end = 7000
    #     if year >= 2020 and year <= 2026:
    #         for yr in range(start_year, year):
    #             start += start * 0.15
    #             end += end * 0.15
    #     return range(start, end)

    def roundup(self, x):
        return int(math.ceil(x / 100.0)) * 100

    def _compute_employee_company_share(self):
        for rec in self:
            year = datetime.datetime.now().year
            start_year = 2020
            start = 1000
            end = 7000
            if year >= 2020 and year <= 2026:
                for yr in range(start_year, year):
                    start += start * 0.15
                    end += end * 0.15
                    start = self.roundup(start)
                    end = self.roundup(end)
            current_salary_range = range(int(start), int(end))
            print("start", self.roundup(start))
            print("end", self.roundup(end))

            if rec.wage in current_salary_range:
                rec.employee_share = rec.wage * (11/100)
                rec.company_share = rec.wage * (18.75/100)
            elif rec.wage > end:
                rec.employee_share = end * (11/100)
                rec.company_share = end * (18.75 / 100)
            elif rec.wage < start:
                rec.employee_share = start * (11/100)
                rec.company_share = start * (18.75 / 100)
