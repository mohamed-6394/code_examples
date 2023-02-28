from odoo import api, fields, models, _
import json
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.misc import get_lang

from datetime import datetime, timedelta


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_date': order.date_order,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
        }

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'invoice_date': self.date_order,
        }
        return invoice_vals


class QuotationTemplate(models.TransientModel):
    _name = 'quotation.template'

    @api.depends('quotation_lines.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the QT.
        """
        for qt in self:
            amount_untaxed = amount_tax = 0.0
            for line in qt.quotation_lines:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            qt.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.model
    def default_get(self, fields_list):
        default_vals = super(QuotationTemplate, self).default_get(fields_list)
        if "sale_order_template_id" in fields_list and not default_vals.get("sale_order_template_id"):
            company_id = default_vals.get('company_id', False)
            company = self.env["res.company"].browse(company_id) if company_id else self.env.company
            default_vals['sale_order_template_id'] = company.sale_order_template_id.id
        return default_vals

    partner_ids = fields.Many2many("res.partner", string="Customer", required=True)
    validity_date = fields.Date("Expiration")
    date_order = fields.Datetime("Quotation Date", default=fields.Datetime.now, required=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.user.company_id.currency_id,
                                  ondelete="restrict")
    company_id = fields.Many2one("res.country", default=lambda self: self.env.user.company_id.id)
    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quotation Template')
    quotation_lines = fields.One2many("quotation.template.line", "quotation_id")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, compute='_amount_all', tracking=5)
    tax_totals_json = fields.Char(compute='_compute_tax_totals_json')
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all', tracking=4)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if self.sale_order_template_id and self.sale_order_template_id.number_of_days > 0:
            default = dict(default or {})
            default['validity_date'] = fields.Date.context_today(self) + timedelta(
                self.sale_order_template_id.number_of_days)
        return super(QuotationTemplate, self).copy(default=default)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(QuotationTemplate, self).onchange_partner_id()
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

    def _compute_line_data_for_template_change(self, line):
        return {
            'name': line.name,
        }

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):

        template = self.sale_order_template_id

        # --- first, process the list of products from the template
        quotation_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)

            if line.product_id:
                price = line.product_id.lst_price
                discount = 0

                data.update({
                    'price_unit': price,
                    'discount': discount,
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                })

            quotation_lines.append((0, 0, data))

        self.quotation_lines = quotation_lines
        # self.quotation_lines._compute_tax_id()

        if template.number_of_days > 0:
            self.validity_date = fields.Date.context_today(self) + timedelta(template.number_of_days)

    @api.depends('quotation_lines.tax_id', 'quotation_lines.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(quotation_lines):
            price = quotation_lines.price_unit * (1 - (quotation_lines.discount or 0.0) / 100.0)
            quotation = quotation_lines.quotation_id
            return quotation_lines.tax_id._origin.compute_all(price, quotation.currency_id,
                                                              quotation_lines.product_uom_qty,
                                                              product=quotation_lines.product_id,
                                                              partner=False)

        account_move = self.env['account.move']
        for quotation in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(quotation.quotation_lines,
                                                                                         compute_taxes)
            tax_totals = account_move._get_tax_totals(False, tax_lines_data, quotation.amount_total,
                                                      quotation.amount_untaxed, quotation.currency_id)
            quotation.tax_totals_json = json.dumps(tax_totals)

    def action_create(self):
        if self.quotation_lines:
            for partner in self.partner_ids:
                sale_order = self.env['sale.order'].sudo().create({
                    'partner_id': partner.id,
                    'validity_date': self.validity_date,
                    'date_order': self.date_order,
                    'company_id': self.company_id.id,
                })
                for rec in self.quotation_lines:
                    sale_order_line = {
                        'order_id': sale_order.id,
                        'product_id': rec.product_id.id,
                        'name': rec.name,
                        'product_uom_qty': rec.product_uom_qty,
                        'product_uom': rec.product_uom.id,
                        'price_unit': rec.price_unit,
                        'tax_id': rec.tax_id,
                        'discount': rec.discount,
                        'customer_lead': rec.customer_lead,
                    }
                    sale_order.write({'order_line': [(0, 0, sale_order_line)]})
                sale_order.action_confirm()
        else:
            raise UserError("You have to create lines")


class QuotationTemplateLine(models.TransientModel):
    _name = 'quotation.template.line'

    quotation_id = fields.Many2one("quotation.template", string='Quotation Reference', required=True,
                                   ondelete='cascade', index=True, copy=False)
    name = fields.Char("Description")
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    currency_id = fields.Many2one(related='quotation_id.currency_id', depends=["quotation_id"], store=True,
                                  ondelete="restrict")
    company_id = fields.Many2one(related='quotation_id.company_id', string='Company')
    customer_lead = fields.Float(
        'Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name
            self.tax_id = self.product_id.taxes_id.ids

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=False)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
