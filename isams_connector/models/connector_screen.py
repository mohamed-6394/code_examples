# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import json
import requests


class IsamsConnector(models.Model):
    _name = 'isams.connector'

    name = fields.Char("Name")
    url = fields.Char("URL", required=True)
    api_key = fields.Char("API Key", required=True)

    def get_data(self):
        if self.url and self.api_key:
            url = f"{self.url}/api/batch/1.0/json.ashx?apiKey={self.api_key}"
            headers = {'Content-type': 'application/json'}
            answer = requests.get(url, headers=headers).json()
            pupils = answer['iSAMS']['PupilManager']['CurrentPupils'][0]['Pupil']
            parents = answer['iSAMS']['PupilManager']['Contacts']['Contact']
            if pupils:
                for pupil in pupils:
                    student = self.env['student.student'].search([('school_id', '=', pupil['SchoolId'])])
                    if not student:
                        birthdate_str = pupil['DOB'].split("T")
                        birthdate = datetime.strptime(birthdate_str[0], '%Y-%m-%d')
                        enrolment_date_str = pupil['EnrolmentDate'].split("T")
                        enrolment_date = datetime.strptime(enrolment_date_str[0], '%Y-%m-%d')
                        student_student = None
                        parent_parent = None
                        pupils_obj = {
                            'school_id': pupil['SchoolId'],
                            'first_name': pupil['Forename'],
                            'last_name': pupil['Surname'],
                            'gender': pupil['Gender'],
                            'birth_date': birthdate,
                            'nc_year': pupil['NCYear'],
                            'division': pupil['DivisionName'],
                            'enrolment_date': enrolment_date,
                            'nationality': pupil['Nationalities'],
                        }
                        if ("EnrolmentTerm" and "EnrolmentSchoolYear") in pupil:
                            pupils_obj['enrolment_term'] = pupil['EnrolmentTerm']
                            pupils_obj['enrolment_year'] = pupil['EnrolmentSchoolYear']
                            student_student = self.env['student.student'].sudo().create(pupils_obj)
                        else:
                            student_student = self.env['student.student'].sudo().create(pupils_obj)
                        if parents:
                            for parent in parents:
                                parents_obj = {
                                    'person_id': parent['@PersonId'],
                                    'first_name': parent['Forename'],
                                    'last_name': parent['Surname'],
                                    'address': parent['Address']['AddressLines']['Address1'],
                                    'town': parent['Address']['Town'],
                                    'postcode': parent['Address']['Postcode'],
                                    'relationship': parent['RelationshipRaw'],
                                    'email': parent['EmailAddress'],
                                    'telephone': parent['Telephone'],
                                    'profession': parent['Profession'],
                                }
                                if "SchoolId" in parent['Pupils']['Pupil']:
                                    if pupil['SchoolId'] == parent['Pupils']['Pupil']['SchoolId']['#text']:
                                        parent_id = self.env['student.parent'].search(
                                            [('person_id', '=', parent['@PersonId'])])
                                        if not parent_id:
                                            if "Mobile" in parent:
                                                if "Country" in parent['Address']:
                                                    parents_obj['country'] = parent['Address']['Country']
                                                    parents_obj['mobile'] = parent['Mobile']
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                                else:
                                                    parents_obj['mobile'] = parent['Mobile']
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                            else:
                                                if "Country" in parent['Address']:
                                                    parents_obj['country'] = parent['Address']['Country']
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                                else:
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                            if student_student:
                                                parent_parent.write({'student_ids': [(4, student_student.id)]})
                                                student_student.write({'parent_ids': [(4, parent_parent.id)]})
                                        else:
                                            if student_student:
                                                parent_id.write({'student_ids': [(4, student_student.id)]})
                                                student_student.write({'parent_ids': [(4, parent_id.id)]})
                                else:
                                    for student_id in parent['Pupils']['Pupil']:
                                        if pupil['SchoolId'] == student_id['SchoolId']['#text']:
                                            parent_id = self.env['student.parent'].search(
                                                [('person_id', '=', parent['@PersonId'])])
                                            if not parent_id:
                                                if "Mobile" in parent:
                                                    if "Country" in parent['Address']:
                                                        parents_obj['country'] = parent['Address']['Country']
                                                        parents_obj['mobile'] = parent['Mobile']
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                    else:
                                                        parents_obj['mobile'] = parent['Mobile']
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                else:
                                                    if "Country" in parent['Address']:
                                                        parents_obj['country'] = parent['Address']['Country']
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                    else:
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                if student_student:
                                                    parent_parent.write({'student_ids': [(4, student_student.id)]})
                                                    student_student.write({'parent_ids': [(4, parent_parent.id)]})
                                            else:
                                                if student_student:
                                                    parent_id.write({'student_ids': [(4, student_student.id)]})
                                                    student_student.write({'parent_ids': [(4, parent_id.id)]})
                    else:
                        if parents:
                            for parent in parents:
                                parents_obj = {
                                    'person_id': parent['@PersonId'],
                                    'first_name': parent['Forename'],
                                    'last_name': parent['Surname'],
                                    'address': parent['Address']['AddressLines']['Address1'],
                                    'town': parent['Address']['Town'],
                                    'postcode': parent['Address']['Postcode'],
                                    'relationship': parent['RelationshipRaw'],
                                    'email': parent['EmailAddress'],
                                    'telephone': parent['Telephone'],
                                    'profession': parent['Profession'],
                                }
                                if "SchoolId" in parent['Pupils']['Pupil']:
                                    if pupil['SchoolId'] == parent['Pupils']['Pupil']['SchoolId']['#text']:
                                        parent_id = self.env['student.parent'].search(
                                            [('person_id', '=', parent['@PersonId'])])
                                        if not parent_id:
                                            if "Mobile" in parent:
                                                if "Country" in parent['Address']:
                                                    parents_obj['country'] = parent['Address']['Country']
                                                    parents_obj['mobile'] = parent['Mobile']
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                                else:
                                                    parents_obj['mobile'] = parent['Mobile']
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                            else:
                                                if "Country" in parent['Address']:
                                                    parents_obj['country'] = parent['Address']['Country']
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                                else:
                                                    parent_parent = self.env['student.parent'].sudo().create(
                                                        parents_obj)
                                            parent_parent.write({'student_ids': [(4, student.id)]})
                                            student.write({'parent_ids': [(4, parent_parent.id)]})
                                        else:
                                            parent_id.write({'student_ids': [(4, student.id)]})
                                            student.write({'parent_ids': [(4, parent_id.id)]})
                                else:
                                    for student_id in parent['Pupils']['Pupil']:
                                        if pupil['SchoolId'] == student_id['SchoolId']['#text']:
                                            parent_id = self.env['student.parent'].search(
                                                [('person_id', '=', parent['@PersonId'])])
                                            if not parent_id:
                                                if "Mobile" in parent:
                                                    if "Country" in parent['Address']:
                                                        parents_obj['country'] = parent['Address']['Country']
                                                        parents_obj['mobile'] = parent['Mobile']
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                    else:
                                                        parents_obj['mobile'] = parent['Mobile']
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                else:
                                                    if "Country" in parent['Address']:
                                                        parents_obj['country'] = parent['Address']['Country']
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                    else:
                                                        parent_parent = self.env['student.parent'].sudo().create(
                                                            parents_obj)
                                                parent_parent.write({'student_ids': [(4, student.id)]})
                                                student.write({'parent_ids': [(4, parent_parent.id)]})
                                            else:
                                                parent_id.write({'student_ids': [(4, student.id)]})
                                                student.write({'parent_ids': [(4, parent_id.id)]})
            if parents:
                for parent in parents:
                    parent_id = self.env['student.parent'].search([('person_id', '=', parent['@PersonId'])])

                    parents_obj1 = {
                        'person_id': parent['@PersonId'],
                        'first_name': parent['Forename'],
                        'last_name': parent['Surname'],
                        'address': parent['Address']['AddressLines']['Address1'],
                        'town': parent['Address']['Town'],
                        'postcode': parent['Address']['Postcode'],
                        'relationship': parent['RelationshipRaw'],
                        'email': parent['EmailAddress'],
                        'telephone': parent['Telephone'],
                        'profession': parent['Profession'],
                    }
                    if not parent_id:
                        if "Mobile" in parent:
                            if "Country" in parent['Address']:
                                parents_obj1['country'] = parent['Address']['Country']
                                parents_obj1['mobile'] = parent['Mobile']
                                parent_parent = self.env['student.parent'].sudo().create(
                                    parents_obj1)
                            else:
                                parents_obj1['mobile'] = parent['Mobile']
                                parent_parent = self.env['student.parent'].sudo().create(
                                    parents_obj1)
                        else:
                            if "Country" in parent['Address']:
                                parents_obj1['country'] = parent['Address']['Country']
                                parent_parent = self.env['student.parent'].sudo().create(
                                    parents_obj1)
                            else:
                                parent_parent = self.env['student.parent'].sudo().create(
                                    parents_obj1)

                # I added another loop because if any parent don't have child so will be added in the above loop
                for parent in parents:
                    parent_id = self.env['student.parent'].search([('person_id', '=', parent['@PersonId'])])
                    partner_id = self.env['res.partner'].search([('person_id', '=', parent['@PersonId'])])
                    if parent_id:
                        child_ids = []
                        if parent_id.student_ids:
                            for stud in parent_id.student_ids:
                                child_ids.append((0, 0, {
                                    'company_type': 'person',
                                    'type': 'contact',
                                    'person_id': stud.school_id,
                                    'first_name': stud.first_name,
                                    'last_name': stud.last_name,
                                }))
                        partner_obj = {
                            'company_type': 'company',
                            'type': 'contact',
                            'person_id': parent['@PersonId'],
                            'first_name': parent['Forename'],
                            'last_name': parent['Surname'],
                            'street': parent['Address']['AddressLines']['Address1'],
                            'city': parent['Address']['Town'],
                            'zip': parent['Address']['Postcode'],
                            'email': parent['EmailAddress'],
                            'phone': parent['Telephone'],
                            'function': parent['Profession'],
                            'student_parent_id': parent_id.id,
                        }

                        if not partner_id:
                            if "Mobile" in parent:
                                partner_obj['mobile'] = parent['Mobile']
                                partner_obj['child_ids'] = child_ids
                                partner_parent = self.env['res.partner'].sudo().create(
                                    partner_obj)
                            else:
                                partner_obj['child_ids'] = child_ids
                                partner_parent = self.env['res.partner'].sudo().create(
                                    partner_obj)
                            parent_id.write({'partner_id': partner_parent.id})
                        else:
                            student_ids = []
                            if partner_id.child_ids:
                                for child in partner_id.child_ids:
                                    student_ids.append(child.person_id)
                            if parent_id:
                                if parent_id.student_ids:
                                    for std in parent_id.student_ids:
                                        if std.school_id not in student_ids:
                                            partner_id.write({'child_ids': [(0, 0, {
                                                'company_type': 'person',
                                                'type': 'contact',
                                                'person_id': std.school_id,
                                                'first_name': std.first_name,
                                                'last_name': std.last_name,
                                            })]})

        else:
            raise UserError("URL and API Key fields are mandatory")
