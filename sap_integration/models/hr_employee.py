from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError, AccessDenied


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    balance = fields.Float("Balance")
    analytic_account_ids = fields.Many2many("account.analytic.account", string="Analytic Accounts")

    @api.constrains('analytic_account_ids')
    def check_analytic_account_ids(self):
        if len(self.analytic_account_ids) > 4:
            raise UserError("You Can't Add more than 4 analytic accounts")
