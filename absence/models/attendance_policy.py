from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AttendancePolicy(models.Model):
    _name = 'attendance.policy'

    name = fields.Char()
    hours = fields.Integer("Allowed Late Hours Per Month ", required=True)
    active_bool = fields.Boolean("Active")
    rate = fields.Float("Rate")
    apply_after = fields.Float("Apply After")
    absence_policy = fields.One2many("absence.policy", "absence_One2many")
    late_policy = fields.One2many("absence.policy", "absence_One2many")
    start_month = fields.Integer("Start Month", default= 1)

    @api.constrains('start_month')
    def constrains_start_month(self):
        if self.start_month == 0 or self.start_month > 31:
            raise UserError(_("Invalid Day"))

    @api.constrains('active_bool')
    def constrains_active(self):
        active_bool = self.search([('active_bool', '=', True)])
        print(len(active_bool))
        if len(active_bool) > 1:
            raise ValidationError("You Can't active this policy because there is another policy active")


class AbsencePolicy(models.Model):
    _name = 'absence.policy'

    absence_times = fields.Char("Times")
    absence_rate = fields.Float("Rate")
    absence_One2many = fields.Many2one('attendance.policy')