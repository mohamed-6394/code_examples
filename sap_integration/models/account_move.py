from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref_code = fields.Char("Payslip Number")
