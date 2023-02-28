from odoo import api, fields, models, _


class Parents(models.Model):
    _name = 'student.parent'

    name = fields.Char(readonly=True)
    person_id = fields.Char("Person Id", readonly=True)
    first_name = fields.Char("First Name")
    last_name = fields.Char("First Name")
    address = fields.Char("Address")
    town = fields.Char("Town")
    postcode = fields.Char("PostCode")
    country = fields.Char("Country")
    relationship = fields.Char("Relationship")
    email = fields.Char("Email")
    mobile = fields.Char("Mobile")
    telephone = fields.Char("Telephone")
    profession = fields.Char("Profession")
    student_ids = fields.Many2many("student.student", string="Students")
    partner_id = fields.Many2one("res.partner", string="Contact")

    @api.onchange('first_name', 'last_name')
    def onchange_name(self):
        self.name = f"{self.first_name} {self.last_name}"

    @api.model
    def create(self, values):
        values = super(Parents, self).create(values)
        if values['first_name'] and values['last_name']:
            values['name'] = f"{values['first_name']} {values['last_name']}"
        elif values['first_name']:
            values['name'] = values['first_name']
        elif values['last_name']:
            values['name'] = values['last_name']
        return values

    def open_parent(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Parent',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'student.parent',
            'target': 'current',
            'res_id': self.id,
        }
