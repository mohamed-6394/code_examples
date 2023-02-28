# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
# from datetime import datetime
import datetime
from datetime import date


class LoansConfigPayroll(models.Model):
    _name = 'loans.config'
    name = fields.Char()
    company_max_loans_checkbox = fields.Boolean(
        'Determine Maximum Company Loans')
    company_max_loans = fields.Float('Company Maximum Loans')
    max_schedule_loans = fields.Integer('Determine Maximum number of Months to schedule')
    max_valid_loans_checkbox = fields.Boolean(
        'Maximum employee Loans per salary')
    max_valid_loans = fields.Float('number of months to multiple in salary')
    active_bo = fields.Boolean("Active")
    loans_creation = fields.Many2one('loans.creation')

    @api.constrains('active_bo')
    def constrains_active(self):
        active_bo = self.search([('active_bo', '=', True)])
        print(len(active_bo))
        if len(active_bo) > 1:
            raise ValidationError(
                "You Can't active this loans configuration because there is another loans active")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_loans_configuration(self):
        loans_configuration = self.env['loans.config'].search(
            [('active_bo', '=', True)], limit=1)
        return loans_configuration

    loans_configuration_id = fields.Many2one('loans.config', string="Loans Configuration",
                                             default=get_loans_configuration)
    loans_monthly_amount = fields.Float(string="Loans Monthly Amount", compute="get_loans_monthly_amount")

    def get_loans_monthly_amount(self):
        for rec in self:
            loans_creation = self.env['loans.creation'].search([('name', '=', self.name),
                                                                ('state', '=', 'approved')])
            amount = 0.0
            if loans_creation:
                month = datetime.datetime.now().month
                year = datetime.datetime.now().year
                for lines in loans_creation.loans_details:
                    if year == lines.monthly_payOff_dates.year:
                        if month == lines.monthly_payOff_dates.month:
                            amount = lines.monthly_payOff_amount
                rec.loans_monthly_amount = amount
            else:
                rec.loans_monthly_amount = 0.0


class EmployeePublicInherit(models.Model):
    _inherit = 'hr.employee.public'

    loans_configuration_id = fields.Many2one('loans.config', string="Loans Configuration")


class Loans_main_menu(models.Model):
    _name = 'loans.creation'

    name = fields.Many2one('hr.employee', string='Employee Name', required=True)
    loans_amount = fields.Float('Loans Amount', required=True)
    request_date = fields.Date('Request Date')
    start_dateOf_loans = fields.Date('Loans Payoff Start Date', required=True)
    loans_period = fields.Integer('Loans months Period', required=True)
    loans_end_date = fields.Date(
        'Loans End Date', compute="_compute_loans_end_date")
    loans_details = fields.One2many(
        'loans.details', 'loans_creation', string="Payoff Details", readonly=True)
    loans_monthly_amount = fields.Float(compute="get_loans_details")
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('cancel', 'Cancelled')],
                             required=True, default='draft')
    account_debit = fields.Many2one("account.account", string="Debit Account", required=True)
    account_credit = fields.Many2one("account.account", string="Credit Account", required=True)
    bank_journal = fields.Many2one("account.journal", string="Journal", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)

    def button_approve(self):
        self.write({'state': 'approved'})

        ################################################################################
        # creating journal entry for the loans amount with the debit and credit accounts
        ################################################################################
        today = date.today()

        loan_journal = self.env['account.move'].sudo().create({
            'date': today,
            'journal_id': self.bank_journal.id,
            'currency_id': self.currency_id.id
        })

        debit = {'move_id': loan_journal.id,
                 'account_id': self.account_debit.id,
                 'partner_id': self.env.user.partner_id.id,
                 'date': today,
                 'currency_id': self.currency_id.id,
                 'debit': self.loans_amount,
                 'credit': 0.0,
                 'analytic_account_id': False}
        credit = {'move_id': loan_journal.id,
                  'account_id': self.account_credit.id,
                  'partner_id': self.env.user.partner_id.id,
                  'date': today,
                  'currency_id': self.currency_id.id,
                  'debit': 0.0,
                  'credit': self.loans_amount,
                  'analytic_account_id': False}

        loan_journal.write({'line_ids': [(0, 0, debit), (0, 0, credit)]})

    def button_cancel(self):
        self.state = 'cancel'

    @api.constrains('loans_period', 'loans_amount')
    def _create_loans_with_config(self):
        for rec in self:
            # loans_config = self.env['loans.config'].search([('active', '=', True)], limit=1)
            total_emp_loans = 0
            loans_config = rec.name.loans_configuration_id
            contracts = self.env['hr.contract'].search(
                [('employee_id', '=', rec.name.id)], limit=1)
            wage = contracts.wage

            if rec.loans_period > loans_config.max_schedule_loans:
                raise ValidationError(
                    "Your Payoff Period is bigger than the Standard")

                # this if for company budget

            if loans_config.company_max_loans_checkbox == True:
                for line in rec.name:
                    total_emp_loans = total_emp_loans + rec.loans_amount
                    if total_emp_loans > loans_config.company_max_loans:
                        raise ValidationError(
                            "Loans Amount is bigger than the company budget")

                        # this if for employee budget

            if loans_config.max_valid_loans_checkbox == True:
                if rec.loans_amount > (wage * loans_config.max_valid_loans):
                    raise ValidationError(
                        "Loans Amount is bigger than your budget")

    def _compute_loans_end_date(self):
        for rec in self:
            if rec.start_dateOf_loans and rec.loans_period:
                rec.loans_end_date = rec.start_dateOf_loans + \
                                     relativedelta(months=rec.loans_period)
            else:
                rec.loans_end_date = False

    @api.model
    def schaduel_get_loan_details(self):
        records = self.search([])
        for rec in records:
            rec.get_loans_details()
        return True

    def get_loans_details(self):
        cur_date = self.start_dateOf_loans
        end = self.loans_end_date
        today = date.today()
        monthly_payOff_amount = self.loans_amount / self.loans_period
        self.loans_monthly_amount = monthly_payOff_amount
        lst = []
        id_lst = []
        for i in range(1, self.loans_period + 1):
            if today > end:
                self.loans_monthly_amount = 0.0
            if cur_date <= today:
                loans_status = 'paidOff'
            else:
                loans_status = 'notPaid'
            if cur_date.month != 2:
                cur_date += relativedelta(day=self.start_dateOf_loans.day)
            loan_detail = self.env['loans.details'].create({'monthly_payOff_dates': cur_date,
                                                            'monthly_payOff_amount': monthly_payOff_amount,
                                                            'loans_status': loans_status,
                                                            'loans_creation': self.id
                                                            }).id
            id_lst.append(loan_detail)
            cur_date = cur_date + relativedelta(months=1)

        self.update({'loans_details': [(6, 0, id_lst)]})


class Loans_Details(models.Model):
    _name = 'loans.details'

    # loans details table

    loans_status = fields.Selection(
        [('paidOff', 'Paid off'), ('notPaid', 'Not Paid')])
    monthly_payOff_dates = fields.Date('Pay Off Dates', )
    monthly_payOff_amount = fields.Float('Pay Off Amount', )
    loans_creation = fields.Many2one('loans.creation')
