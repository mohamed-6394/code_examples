from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char()
    last_name = fields.Char()
    person_id = fields.Char("Person Id", readonly=True)
    student_parent_id = fields.Many2one("student.parent", string="Student Parent")

    @api.model
    def create(self, values):
        if values.get('first_name') and values.get('last_name'):
            values['name'] = f"{values.get('first_name')} {values.get('last_name')}"
        elif values.get('first_name'):
            values['name'] = values.get('first_name')
        elif values.get('last_name'):
            values['name'] = values.get('last_name')
        values = super(ResPartner, self).create(values)
        return values
