# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError, AccessDenied
from datetime import datetime
import json
import requests

base_url = "http://82.213.57.216:8099"
headers = {'Content-type': 'application/json'}


class SapConnector(models.Model):
    _name = 'sap.connector'

    name = fields.Char("Sap Username", required=True)
    password = fields.Char("Sap Password", required=True, copy=False)
    active_bool = fields.Boolean("Active", default=False)

    @api.constrains('active_bool')
    def unique_active(self):
        for rec in self:
            if rec.id != self.id:
                if rec.active_bool:
                    raise UserError("You Can't Active Two SAP Records")

    def login(self):
        if self.name and self.password and self.active_bool:
            login_api = f"{base_url}/api/Login"
            req_body = {
                "username": self.name,
                "password": self.password,
            }
            data = json.dumps(req_body, indent=4, ensure_ascii=False).encode('utf8')
            # try:
            answer = requests.post(login_api, data=data, headers=headers).json()
            if 'isSuccess' in answer:
                if not answer['isSuccess']:
                    raise ValidationError("Login Field Please Check Your Username and Password")

            print(answer['SessionId'])

            return answer['SessionId']

    def get_employees(self):
        session_id = self.login()

        employees_api = f"{base_url}/api/GetEmployees"
        headers['Session'] = session_id
        answer = requests.get(employees_api, headers=headers).json()
        print(answer)
        for emp in answer:
            contact = self.env['res.partner'].search([('ref', '=', emp['code'])], limit=1)
            if not contact:
                new_contact = self.env['res.partner'].sudo().create({
                    'name': emp['name'],
                    'ref': emp['code'],
                    'company_type': 'person'
                })
                new_employee = self.env['hr.employee'].sudo().create({
                    'name': emp['name'],
                    'address_id': new_contact.id,
                })
            else:
                employee = self.env['hr.employee'].search([('address_id', '=', contact.id)])
                if not employee:
                    new_employee = self.env['hr.employee'].sudo().create({
                        'name': contact.name,
                        'address_id': contact.id,
                    })
        del headers['Session']

    def get_balance(self):
        session_id = self.login()
        balance_api = f"{base_url}/api/GetAccountBalance"
        headers['Session'] = session_id
        answer = requests.get(balance_api, headers=headers).json()
        print(answer)
        for emp in answer:
            contact = self.env['res.partner'].search([('ref', '=', emp['code'])], limit=1)
            if contact:
                employee = self.env['hr.employee'].search([('address_id', '=', contact.id)], limit=1)
                if employee:
                    employee.write({'balance': emp['balance']})
                else:
                    new_employee = self.env['hr.employee'].sudo().create({
                        'name': contact.name,
                        'address_id': contact.id,
                        'balance': emp['balance']
                    })
            else:
                new_contact = self.env['res.partner'].sudo().create({
                    'name': emp['name'],
                    'ref': emp['code'],
                    'company_type': 'person'
                })
                new_employee = self.env['hr.employee'].sudo().create({
                    'name': emp['name'],
                    'address_id': new_contact.id,
                    'balance': emp['balance']
                })
        del headers['Session']

    def get_analytic_account(self):
        session_id = self.login()
        analytic_acc_api = f"{base_url}/api/GetCostCenters"
        headers['Session'] = session_id
        answer = requests.get(analytic_acc_api, headers=headers).json()
        print(answer)
        for analytic_account in answer:
            analytic_acc = self.env['account.analytic.account'].search([('code', '=', analytic_account['costingCenterCode'])], limit=1)
            if not analytic_acc:
                new_analytic_acc = self.env['account.analytic.account'].sudo().create({
                    'name': analytic_account['costingCenterName'],
                    'code': analytic_account['costingCenterCode'],
                    'dimension_code': analytic_account['dimensionCode']
                })
        del headers['Session']
