from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date
import time  # Tambahkan impor ini

class SaleOrders(models.Model):
    _inherit = 'sale.order'

    amount_remaining = fields.Monetary(string='Amount Remaining', store=True, readonly=True, compute='_compute_amount_remaining', tracking=True)

    @api.depends('order_line.price_total', 'invoice_ids.state', 'invoice_ids.amount_total', 'invoice_ids.payment_state')
    def _compute_amount_remaining(self):
        for order in self:
            total_invoiced_amount = sum(order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state in ['in_payment', 'paid']).mapped('amount_total'))
            order.amount_remaining = order.amount_untaxed + order.amount_tax - total_invoiced_amount

    @api.depends('amount_untaxed', 'amount_tax')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = order.amount_untaxed + order.amount_tax

class SaleAdvancePaymentInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    _description = "Sales Advance Payment Invoice"

    advance_payment_method = fields.Selection([
        ('delivered', 'Regular invoice'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Termin 1'),
        ('termin_2', 'Termin 2'),
        ('termin_3', 'Termin 3'),
        ('termin_4', 'Termin 4'),
        ('termin_5', 'Termin 5'),
    ], string='Create Invoice', default='delivered', required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing, \
        according to their invoicing policy (based on ordered or delivered quantity).")

    fixed_amount = fields.Float('Down Payment Amount', digits='Account')
    termin_2_amount = fields.Float('Down Payment Amount', digits='Account')
    termin_3_amount = fields.Float('Down Payment Amount', digits='Account')
    termin_4_amount = fields.Float('Down Payment Amount', digits='Account')
    termin_5_amount = fields.Float('Down Payment Amount', digits='Account')

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        elif self.advance_payment_method == 'fixed':
            fixed_amount = self.default_get(['fixed_amount']).get('fixed_amount')
            return {'value': {'fixed_amount': fixed_amount}}
        elif self.advance_payment_method in ['termin_2', 'termin_3', 'termin_4', 'termin_5']:
            termin_amount = getattr(self, f'{self.advance_payment_method}_amount', 0.0)
            return {'value': {f'{self.advance_payment_method}_amount': termin_amount}}
        return {}

    def _prepare_invoice_values(self, order, name, termin_amount):
        method_names = {
            'delivered': 'Regular Invoice',
            'percentage': 'Down Payment (Percentage)',
            'fixed': 'Termin 1',
            'termin_2': 'Termin 2',
            'termin_3': 'Termin 3',
            'termin_4': 'Termin 4',
            'termin_5': 'Termin 5',
        }

        method_display_name = method_names.get(self.advance_payment_method, 'Down Payment')

        if self.advance_payment_method in ['fixed', 'termin_2', 'termin_3', 'termin_4', 'termin_5']:
            product_name = method_display_name
            product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
            if not product:
                raise UserError(f'Product with name "{product_name}" not found!')
            product_id = product.id
        else:
            product_id = self.product_id.id

        analytic_account_id = False
        for line in order.order_line:
            if not line.display_type and order.analytic_account_id:
                analytic_account_id = order.analytic_account_id.id
                break

        account = self.env['account.account'].search([('code', '=', '11120004')], limit=1)
        if not account:
            raise UserError('Account with code "11120004" not found!')

        # ✅ Partner ID tetap ada, Associate hanya muncul jika terbit_invoice == 'Associate'
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,  # ✅ Partner tetap ada
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
            'terbit_invoice': order.terbit_invoice,  # ✅ Simpan pilihan invoice
            'associate_name': order.associate_name.id if order.terbit_invoice == 'Associate' else False,  # ✅ Hanya muncul jika Associate
            'invoice_line_ids': [(0, 0, {
                'name': method_display_name,
                'price_unit': termin_amount,
                'quantity': 1.0,
                'product_id': product_id,
                'product_uom_id': self.product_id.uom_id.id,
                'tax_ids': [(6, 0, self.product_id.taxes_id.ids)],
                'sale_line_ids': [(6, 0, order.order_line.ids)],
                'analytic_tag_ids': [(6, 0, order.order_line.analytic_tag_ids.ids)],
                'analytic_account_id': analytic_account_id,
                'in_pajak': line.in_pajak,  # ✅ Menambahkan field in_pajak pada account.move.line
                'ex_pajak': line.ex_pajak,  # ✅ Menambahkan field ex_pajak pada account.move.line
                'account_id': account.id,
            })],
        }

        return invoice_vals

    def _create_invoice(self, order, termin_amount):
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method in ['fixed', 'termin_2', 'termin_3', 'termin_4', 'termin_5'] and termin_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))

        method_names = {
            'delivered': 'Regular Invoice',
            'percentage': 'Down Payment (Percentage)',
            'fixed': 'Termin 1',
            'termin_2': 'Termin 2',
            'termin_3': 'Termin 3',
            'termin_4': 'Termin 4',
            'termin_5': 'Termin 5',
        }

        method_display_name = method_names.get(self.advance_payment_method)

        name = _('%s: %s') % (method_display_name, time.strftime('%m %Y'),)

        invoice_vals = self._prepare_invoice_values(order, name, termin_amount)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id

        invoice = self.env['account.move'].with_company(order.company_id)\
            .sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)

        return invoice

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                elif self.advance_payment_method == 'fixed':
                    amount = self.fixed_amount
                elif self.advance_payment_method in ['termin_2', 'termin_3', 'termin_4', 'termin_5']:
                    amount = getattr(self, f'{self.advance_payment_method}_amount', 0.0)

                invoice = self._create_invoice(order, amount)

                total_invoiced_amount = sum(order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state != 'cancel').mapped('amount_total'))
                if total_invoiced_amount < order.amount_total:
                    order.write({'invoice_status': 'to invoice'})
                else:
                    order.write({'invoice_status': 'invoiced'})

                order._compute_amount_total()

        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': 'Down Payment',
            'type': 'service',
            'invoice_policy': 'order',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'uom_po_id': self.env.ref('uom.product_uom_unit').id,
            'taxes_id': [],
        }

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_register_payment(self):
        res = super(AccountMove, self).action_register_payment()
        
        self.update_sale_order_invoice_status()
        
        return res

    def update_sale_order_invoice_status(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.state == 'posted':
                sale_orders = self.env['sale.order'].search([('name', '=', move.invoice_origin)])
                for order in sale_orders:
                    total_paid_amount = sum(order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted').mapped('amount_total'))
                    
                    if total_paid_amount < order.amount_total:
                        order.invoice_status = 'to invoice'
                    else:
                        order.invoice_status = 'invoiced'
                    
                    order._compute_amount_total()