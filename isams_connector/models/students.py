from odoo import api, fields, models, _


class Student(models.Model):
    _name = 'student.student'

    name = fields.Char(readonly=True)
    school_id = fields.Char("School ID", readonly=True)
    first_name = fields.Char("First Name")
    last_name = fields.Char("Last Name")
    gender = fields.Selection([('M', 'Male'), ('F', 'Female')], string="Gender")
    birth_date = fields.Date("BirthDate")
    nc_year = fields.Char("NC Year")
    division = fields.Char("Division")
    enrolment_date = fields.Date("Enrolment Date")
    enrolment_term = fields.Char("Enrolment Term")
    enrolment_year = fields.Char("Enrolment Year")
    nationality = fields.Char("Nationality")
    parent_ids = fields.Many2many("student.parent")

    @api.onchange('first_name', 'last_name')
    def onchange_name(self):
        self.name = f"{self.first_name} {self.last_name}"

    @api.model
    def create(self, values):
        values = super(Student, self).create(values)
        if values['first_name'] and values['last_name']:
            values['name'] = f"{values['first_name']} {values['last_name']}"
        elif values['first_name']:
            values['name'] = values['first_name']
        elif values['last_name']:
            values['name'] = values['last_name']
        return values

    def open_student(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Student',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'student.student',
            'target': 'current',
            'res_id': self.id,
        }
