# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, UserError, RedirectWarning


# from odoo.addons import decimal_precision as dp


class LetterCreditType(models.Model):
    _name = 'letter.credit.type'
    _description = 'Letter Of Credit Type'

    name = fields.Char()
    lc_journal = fields.Many2one("account.journal", string="LC Journal", required=True)
    lc_bank_journal = fields.Many2one("account.journal", string="LC Bank Journal", required=True)
    bank_fees = fields.Float("Bank Fees (%)")
    bank_expense_account = fields.Many2one("account.account", string="Bank Expense Account", required=True)
    intermediate_account = fields.Many2one("account.account", string="Intermediate Account", required=True)
    bank_account_number = fields.Char("Bank Account Number")
    bank_fees_from_lc = fields.Boolean("Bank Fees From LC")
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], string='Status',
                             default='draft')

    def activate_action(self):
        self.state = 'active'


class LCAmountExtend(models.Model):
    _name = 'lc.amount.extend'

    name = fields.Char("Description")
    amount = fields.Float("Amount")
    lc_seq = fields.Char("LC Sequence")


class LCPeriodExtend(models.Model):
    _name = 'lc.period.extend'

    name = fields.Char("Description")
    date = fields.Datetime("Expiration Date")
    lc_seq = fields.Char("LC Sequence")


class JornalEntriesInherit(models.Model):
    _inherit = 'account.move'

    lc_seq = fields.Char("LC Sequence")


class LetterCredit(models.Model):
    _name = 'letter.credit'
    _description = 'Letter Of Credit'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one("res.partner", string="Vendor")
    lc_type = fields.Many2one("letter.credit.type", string="LC Type", required=True)
    lc_amount = fields.Float("LC Amount", required=True)
    lc_remaining_amount = fields.Float("LC Remaining Amount", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    curr_rate = fields.Float("Currency Rate")
    purchase_order = fields.Many2one("purchase.order", string="Purchase Order")
    date = fields.Datetime("Date")
    expiration_date = fields.Datetime("Expiration Date")
    delivery_date = fields.Datetime("Delivery Date")
    lc_number = fields.Char("LC Number")
    customs_release_number = fields.Char("Customs Release No")
    customs_clearance_number = fields.Char("Customs Clearance No")
    account_move_count = fields.Integer(compute='compute_count')
    amount_extend_count = fields.Integer(compute='compute_count')
    period_extend_count = fields.Integer(compute='compute_count')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('close', 'Close'),
                              ('cancel', 'Cancel')], string='Status', default='draft')

    @api.model
    def create(self, vals):
        vals['lc_remaining_amount'] = vals['lc_amount']
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('manage.lc.sequence') or _('New')
        return super(LetterCredit, self).create(vals)

    def compute_count(self):
        for move in self:
            move.account_move_count = self.env['account.move'].search_count(
                [('lc_seq', '=', self.name)])
            move.amount_extend_count = self.env['lc.amount.extend'].search_count(
                [('lc_seq', '=', self.name)])
            move.period_extend_count = self.env['lc.period.extend'].search_count(
                [('lc_seq', '=', self.name)])

    def calculate_amount(self):
        amount = self.lc_amount
        rate = self.curr_rate
        result = amount / rate
        return result

    def calculate_close_amount(self):
        amount = self.lc_remaining_amount
        rate = self.curr_rate
        result = amount / rate
        return result

    def confirm_action(self):
        self.state = 'open'
        if self.curr_rate == 0.0:
            raise UserError("Currency Rate can't be 0.0")
        if self.lc_amount == 0.0:
            raise UserError("Amount can't be 0.0")
        today = datetime.datetime.now()
        # Create the 3 journal Entries records
        lc_bank_journal = self.env['account.move'].sudo().create({
            'lc_seq': self.name,
            'date': today,
            'journal_id': self.lc_type.lc_bank_journal.id,
            'currency_id': self.currency_id.id
        })
        lc_journal = self.env['account.move'].sudo().create({
            'lc_seq': self.name,
            'date': today,
            'journal_id': self.lc_type.lc_journal.id,
            'currency_id': self.currency_id.id
        })
        # print(lc_bank_journal.id)
        # print(lc_journal.id)
        amount_fees = (self.lc_type.bank_fees / 100) * self.calculate_amount()
        if self.lc_type.bank_fees_from_lc:
            self.lc_remaining_amount -= (amount_fees * self.curr_rate)
            lc_journal_fees_true = self.env['account.move'].sudo().create({
                'lc_seq': self.name,
                'date': today,
                'journal_id': self.lc_type.lc_journal.id,
                'currency_id': self.currency_id.id
            })

            debit3 = {'move_id': lc_journal_fees_true.id,
                      'account_id': self.lc_type.bank_expense_account.id,
                      'partner_id': self.partner_id.id,
                      'date': today,
                      'currency_id': self.currency_id.id,
                      'debit': amount_fees,
                      'credit': 0.0,
                      'analytic_account_id': False}
            credit3 = {'move_id': lc_journal_fees_true.id,
                       'account_id': self.lc_type.lc_journal.default_account_id.id,
                       'partner_id': self.partner_id.id,
                       'date': today,
                       'currency_id': self.currency_id.id,
                       'debit': 0.0,
                       'credit': amount_fees,
                       'analytic_account_id': False}

            lc_journal_fees_true.write({'line_ids': [(0, 0, debit3), (0, 0, credit3)]})

        elif not self.lc_type.bank_fees_from_lc:
            lc_bank_journal_fees_false = self.env['account.move'].sudo().create({
                'lc_seq': self.name,
                'date': today,
                'journal_id': self.lc_type.lc_bank_journal.id,
                'currency_id': self.currency_id.id
            })

            debit2 = {'move_id': lc_bank_journal_fees_false.id,
                      'account_id': self.lc_type.bank_expense_account.id,
                      'partner_id': self.partner_id.id,
                      'date': today,
                      'currency_id': self.currency_id.id,
                      'debit': amount_fees,
                      'credit': 0.0,
                      'analytic_account_id': False}
            credit2 = {'move_id': lc_bank_journal_fees_false.id,
                       'account_id': self.lc_type.lc_bank_journal.default_account_id.id,
                       'partner_id': self.partner_id.id,
                       'date': today,
                       'currency_id': self.currency_id.id,
                       'debit': 0.0,
                       'credit': amount_fees,
                       'analytic_account_id': False}

            lc_bank_journal_fees_false.write({'line_ids': [(0, 0, debit2), (0, 0, credit2)]})

        ################################################
        # adding table data of journal entries
        ################################################

        debit = {'move_id': lc_bank_journal.id,
                 'account_id': self.lc_type.intermediate_account.id,
                 'partner_id': self.partner_id.id,
                 'date': today,
                 'currency_id': self.currency_id.id,
                 'debit': self.calculate_amount(),
                 'credit': 0.0,
                 'analytic_account_id': False}
        credit = {'move_id': lc_bank_journal.id,
                  'account_id': self.lc_type.lc_bank_journal.default_account_id.id,
                  'partner_id': self.partner_id.id,
                  'date': today,
                  'currency_id': self.currency_id.id,
                  'debit': 0.0,
                  'credit': self.calculate_amount(),
                  'analytic_account_id': False}

        lc_bank_journal.write({'line_ids': [(0, 0, debit), (0, 0, credit)]})

        debit1 = {'move_id': lc_journal.id,
                  'account_id': self.lc_type.lc_journal.default_account_id.id,
                  'partner_id': self.partner_id.id,
                  'date': today,
                  'currency_id': self.currency_id.id,
                  'debit': self.calculate_amount(),
                  'credit': 0.0,
                  'analytic_account_id': False}
        credit1 = {'move_id': lc_journal.id,
                   'account_id': self.lc_type.intermediate_account.id,
                   'partner_id': self.partner_id.id,
                   'date': today,
                   'currency_id': self.currency_id.id,
                   'debit': 0.0,
                   'credit': self.calculate_amount(),
                   'analytic_account_id': False}

        lc_journal.write({'line_ids': [(0, 0, debit1), (0, 0, credit1)]})

    def cancel_action(self):
        self.state = 'cancel'

    def close_action(self):
        self.state = 'close'
        today = datetime.datetime.now()
        # Create the 3 journal Entries records
        lc_bank_journal = self.env['account.move'].sudo().create({
            'lc_seq': self.name,
            'date': today,
            'journal_id': self.lc_type.lc_bank_journal.id,
            'currency_id': self.currency_id.id
        })
        lc_journal = self.env['account.move'].sudo().create({
            'lc_seq': self.name,
            'date': today,
            'journal_id': self.lc_type.lc_journal.id,
            'currency_id': self.currency_id.id
        })

        ################################################
        # adding table data of journal entries
        ################################################

        debit = {'move_id': lc_bank_journal.id,
                 'account_id': self.lc_type.intermediate_account.id,
                 'partner_id': self.partner_id.id,
                 'date': today,
                 'currency_id': self.currency_id.id,
                 'debit': 0.0,
                 'credit': self.calculate_close_amount(),
                 'analytic_account_id': False}
        credit = {'move_id': lc_bank_journal.id,
                  'account_id': self.lc_type.lc_bank_journal.default_account_id.id,
                  'partner_id': self.partner_id.id,
                  'date': today,
                  'currency_id': self.currency_id.id,
                  'debit': self.calculate_close_amount(),
                  'credit': 0.0,
                  'analytic_account_id': False}

        lc_bank_journal.write({'line_ids': [(0, 0, debit), (0, 0, credit)]})

        debit1 = {'move_id': lc_journal.id,
                  'account_id': self.lc_type.lc_journal.default_account_id.id,
                  'partner_id': self.partner_id.id,
                  'date': today,
                  'currency_id': self.currency_id.id,
                  'debit': 0.0,
                  'credit': self.calculate_close_amount(),
                  'analytic_account_id': False}
        credit1 = {'move_id': lc_journal.id,
                   'account_id': self.lc_type.intermediate_account.id,
                   'partner_id': self.partner_id.id,
                   'date': today,
                   'currency_id': self.currency_id.id,
                   'debit': self.calculate_close_amount(),
                   'credit': 0.0,
                   'analytic_account_id': False}

        lc_journal.write({'line_ids': [(0, 0, debit1), (0, 0, credit1)]})

    def amount_extend_action(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Extend Amount'),
                'res_model': 'amount.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_letter_credit': self.id},
                }

    def period_extend_action(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Extend Period'),
                'res_model': 'period.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_letter_credit': self.id},
                }


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def pay_from_lc(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register.lc',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
