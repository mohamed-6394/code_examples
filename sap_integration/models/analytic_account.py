from odoo import api, fields, models


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    dimension_code = fields.Char("Dimension Code")
