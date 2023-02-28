from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id},
                }

    def send_sms(self):
        return {'type': 'ir.actions.act_window',
                'name': _('SMS Message'),
                'res_model': 'sms.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_lead_id': self.id},
                }
