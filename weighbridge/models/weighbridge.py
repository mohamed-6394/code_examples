# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class WeighBridge(models.Model):
    _name = 'weighbridge.weighbridge'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    wb_ticket_num = fields.Char("WB Ticket Number")
    db_ticket_id = fields.Integer("DB Record ID")
    validation_date = fields.Datetime("Validation Date", compute='_compute_validation_time')
    car_plate_num = fields.Char("Car Plate Number")
    first_driver_name = fields.Char("Driver Name", required=True)
    first_national_id = fields.Char("First National ID")
    second_national_id = fields.Char("Second National ID")
    first_datetime = fields.Datetime("First DateTime", required=True)
    first_weight = fields.Float("First Weight", required=True)
    second_datetime = fields.Datetime("Second DateTime", required=True)
    second_weight = fields.Float("Second Weight", required=True)
    duration = fields.Char("Duration", compute='_compute_datetime_fields')
    net_weight = fields.Float("Net Weight", compute="_compute_net_weight")
    transaction_type = fields.Selection([('in', 'IN'), ('out', 'OUT')], string="Transaction Type",
                                        compute="_compute_net_weight")
    sale_id = fields.Many2one("sale.order", string="Sale")
    purchase_id = fields.Many2one("purchase.order", string="Purchase")
    product = fields.Char("Product")
    partner_id = fields.Many2one("res.partner", string="Partner")
    product_category = fields.Many2one("product.category", string="Product Category")
    location = fields.Many2one("stock.location", string="Location")
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancelled', 'Cancelled')],
                             default='draft')

    @api.constrains('wb_ticket_num')
    def check_ticket_num(self):
        tickets = self.env['weighbridge.weighbridge'].search([('wb_ticket_num', '=', self.wb_ticket_num),
                                                              ('id', '!=', self.id)], limit=1)
        if tickets:
            if tickets.location.id == self.location.id:
                tickets.write({
                    'car_plate_num': self.car_plate_num,
                    'first_datetime': self.first_datetime,
                    'second_datetime': self.second_datetime,
                    'first_weight': self.first_weight,
                    'second_weight': self.second_weight,
                })
                if self.sale_id:
                    tickets.sale_id = self.sale_id.id
                elif self.purchase_id:
                    tickets.purchase_id = self.purchase_id.id
                raise UserError(
                    _("there's a ticket with the same number, Don't worry your data updated in this ticket number"))

    def unlink(self):
        for rec in self:
            if rec.state == 'validated':
                raise UserError(_("You can't DELETE any record in state Validated"))
        return super(WeighBridge, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('weighbridge.log.sequence') or _('New')
        return super(WeighBridge, self).create(vals)

    @api.depends('state')
    def _compute_validation_time(self):
        for rec in self:
            rec.validation_date = datetime.datetime.now()
            if rec.state == 'validated':
                rec.validation_date = datetime.datetime.now()

    @api.depends('first_datetime', 'second_datetime')
    def _compute_datetime_fields(self):
        for rec in self:
            rec.duration = '0.0'
            if rec.first_datetime and rec.second_datetime:
                first = rec.first_datetime
                second = rec.second_datetime
                if second > first:
                    rec.duration = second - first

    @api.constrains('first_datetime', 'second_datetime', 'duration')
    def duration_const(self):
        for rec in self:
            if rec.first_datetime and rec.second_datetime:
                if rec.first_datetime > rec.second_datetime:
                    raise UserError(_("Second DateTime Should be bigger than First DateTime"))

    @api.onchange('first_datetime', 'second_datetime')
    def onchange_datetime_fields(self):
        for rec in self:
            if rec.first_datetime and rec.second_datetime:
                first = rec.first_datetime
                second = rec.second_datetime
                if second > first:
                    rec.duration = second - first
                else:
                    raise UserError(_("Second DateTime Should be bigger than First DateTime"))

    @api.depends('first_weight', 'second_weight')
    def _compute_net_weight(self):
        for rec in self:
            rec.transaction_type = ''
            rec.net_weight = 0.0
            if rec.first_weight > rec.second_weight:
                rec.transaction_type = 'in'
                rec.net_weight = rec.first_weight - rec.second_weight
            elif rec.second_weight > rec.first_weight:
                rec.net_weight = rec.second_weight - rec.first_weight
                rec.transaction_type = 'out'

    @api.constrains('first_weight', 'second_weight', 'net_weight')
    def net_weight_const(self):
        for rec in self:
            if rec.first_weight > rec.second_weight:
                if rec.first_weight == rec.second_weight:
                    raise UserError(_("first and second weights can't be equal"))

    @api.onchange('first_weight', 'second_weight')
    def onchange_weight_fields(self):
        for rec in self:
            if rec.first_weight and rec.second_weight:
                if rec.first_weight > rec.second_weight:
                    rec.transaction_type = 'in'
                    rec.net_weight = rec.first_weight - rec.second_weight
                elif rec.second_weight > rec.first_weight:
                    rec.net_weight = rec.second_weight - rec.first_weight
                    rec.transaction_type = 'out'
                else:
                    raise UserError(_("first and second weights can't be equal"))

    @api.onchange('sale_id', 'purchase_id')
    def onchange_sale_purchase(self):
        for rec in self:
            products = []
            if rec.sale_id:
                rec.partner_id = rec.sale_id.partner_id.id
                for sale in rec.sale_id.order_line:
                    products.append(sale.product_id.name)
                    rec.product_category = sale.product_id.categ_id.id
                rec.product = products
            elif rec.purchase_id:
                rec.partner_id = rec.purchase_id.partner_id.id
                for purchase in rec.purchase_id.order_line:
                    products.append(purchase.product_id.name)
                    rec.product_category = purchase.product_id.categ_id.id
                rec.product = products

    def action_validate(self):
        self.state = 'validated'
        today = datetime.datetime.now()
        if self.sale_id:
            pickings = self.env['stock.picking'].search([('origin', '=', self.sale_id.name),
                                                         ('state', '=', 'assigned')])
            if pickings:
                for line in pickings.move_ids_without_package:
                    line.quantity_done = self.net_weight
                pickings.with_context({'skip_backorder': True}).button_validate()
        elif self.purchase_id:
            pickings = self.env['stock.picking'].search([('origin', '=', self.purchase_id.name),
                                                         ('state', '=', 'assigned')])
            if pickings:
                for line in pickings.move_ids_without_package:
                    line.quantity_done = self.net_weight
                pickings.with_context({'skip_backorder': True}).button_validate()
        else:
            raise UserError(_('Sale Order OR Purchase Order are Mandatory'))

    def action_cancelled(self):
        self.state = 'cancelled'
