from odoo import models, api, fields, _
import json
import requests
import datetime

from odoo.exceptions import ValidationError


class WhatsappSendMessage(models.TransientModel):
    _name = 'whatsapp.message.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="message", required=True)

    def __init__(self):
        self.token = None
        self.APIUrl = None
        self.json = None

    def send_requests(self, method, data):
        self.json = json
        self.APIUrl = 'https://api.chat-api.com/instance240449/'
        self.token = 'yzn9nkx3lxuhr0m4'
        url = f"{self.APIUrl}{method}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + ' '
            message_string = message_string[:(len(message_string))]
            data = {"phone": self.user_id.mobile,
                    "body": message_string}
            answer = self.send_requests('sendMessage', data)
            print(answer)
            return answer


class WhatsappSendMessagelead(models.TransientModel):
    _name = 'whatsapp.message.wizard.lead'

    lead_id = fields.Many2one('crm.lead', string="Recipient")
    mobile = fields.Char(related='lead_id.mobile', required=True)
    message = fields.Text(string="message", required=True)

    def __init__(self):
        self.token = None
        self.APIUrl = None
        self.json = None

    def send_requests(self, method, data):
        self.json = json
        self.APIUrl = 'https://api.chat-api.com/instance240449/'
        self.token = 'yzn9nkx3lxuhr0m4'
        url = f"{self.APIUrl}{method}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + ' '
            message_string = message_string[:(len(message_string))]
            data = {"phone": self.lead_id.mobile,
                    "body": message_string}
            answer = self.send_requests('sendMessage', data)
            print(answer)
            return answer


class SMSSendMessagelead(models.TransientModel):
    _name = 'sms.message.wizard.lead'

    lead_id = fields.Many2one('crm.lead', string="Recipient")
    mobile = fields.Char(related='lead_id.mobile', required=True)
    message = fields.Text(string="message", required=True)

    def send_sms(self, numbers=[], msg="test"):
        numbers = [self.mobile]
        print(numbers)
        if not numbers:
            raise ValidationError('Please Specify numbers')
        if not msg:
            raise ValidationError('Please Specify SMS Message')

        ICPSudo = self.env['ir.config_parameter'].sudo()
        alfa_api_url = ICPSudo.get_param('alfa_sms.api_url')
        alfa_api_key = ICPSudo.get_param('alfa_sms.api_key')
        alfa_api_sender = ICPSudo.get_param('alfa_sms.api_sender')
        if not (alfa_api_key and alfa_api_sender and alfa_api_url):
            raise ValidationError(_('Please Configure Alfa API parameters'))
        mobile = str(self.mobile).replace(" ", "")
        if len(mobile) > 9:
            i = len(mobile) - 9
            mobile = mobile[i:]
        print(mobile)
        params_data = {
            'AppSid': 'ssyt6MSDVpp183kPCZcJwb8cA39fP5',
            'apiKey': 'CfZgT3ptwgq1pxGTjE4Mj0h0DE2PynUmFcfQTGWJvOR4vJ7YnchbyPODsMZz95o7mOYONsspvlD',
            'Recipient': mobile,
            'SenderID': alfa_api_sender,
            'Body': self.message,
            'returnJson': 1,
            'lang': 3,
            'applicationType': 68
        }

        new_request = requests.post(alfa_api_url, params=params_data).json()
        print(new_request)
        if not new_request['success']:
            raise ValidationError(_(
                'Error While sending SMS Message As The Following Error code %s and error message : %s' % (
                    new_request['errorCode'],
                    new_request['message'])))


class SMSSendMessage(models.TransientModel):
    _name = 'sms.message.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="message", required=True)

    def send_sms(self, numbers=[], msg="test"):
        numbers = [self.mobile]
        print(numbers)
        if not numbers:
            raise ValidationError('Please Specify numbers')
        if not msg:
            raise ValidationError('Please Specify SMS Message')

        ICPSudo = self.env['ir.config_parameter'].sudo()
        alfa_api_url = ICPSudo.get_param('alfa_sms.api_url')
        alfa_api_key = ICPSudo.get_param('alfa_sms.api_key')
        alfa_api_sender = ICPSudo.get_param('alfa_sms.api_sender')
        if not (alfa_api_key and alfa_api_sender and alfa_api_url):
            raise ValidationError(_('Please Configure Alfa API parameters'))
        mobile = str(self.mobile).replace(" ", "")
        if len(mobile) > 9:
            i = len(mobile) - 9
            mobile = mobile[i:]
        print(mobile)
        params_data = {
            'AppSid': 'ssyt6MSDVpp183kPCZcJwb8cA39fP5',
            'apiKey': 'CfZgT3ptwgq1pxGTjE4Mj0h0DE2PynUmFcfQTGWJvOR4vJ7YnchbyPODsMZz95o7mOYONsspvlD',
            'Recipient': mobile,
            'SenderID': alfa_api_sender,
            'Body': self.message,
            'returnJson': 1,
            'lang': 3,
            'applicationType': 68
        }

        new_request = requests.post(alfa_api_url, params=params_data).json()
        print(new_request)
        if not new_request['success']:
            raise ValidationError(_(
                'Error While sending SMS Message As The Following Error code %s and error message : %s' % (
                    new_request['errorCode'],
                    new_request['message'])))
