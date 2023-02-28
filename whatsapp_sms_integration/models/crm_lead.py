from odoo import api, fields, models, _


class ResLead(models.Model):
    _inherit = 'crm.lead'

    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard.lead',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_lead_id': self.id},
                }

    def send_sms(self):
        return {'type': 'ir.actions.act_window',
                'name': _('SMS Message'),
                'res_model': 'sms.message.wizard.lead',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_lead_id': self.id},
                }
