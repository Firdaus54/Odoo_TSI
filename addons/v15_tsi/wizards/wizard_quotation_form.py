from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class WizardQuotationAPP(models.TransientModel):
    _name = 'tsi.wizard_quotation.app'
    _description = 'Wizard for Quotation App'

    def _get_default_reference(self):
        return self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['waiting', 'approved'])])

    def _get_default_partner(self):
        return self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['waiting', 'approved'])],limit=1).customer

    def _get_default_doctype(self):
        return self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['waiting', 'approved'])],limit=1).doctype

    def _get_default_review(self):
        return self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['waiting', 'approved'])])
    
    def _get_default_lines_initial(self):
        initial = self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids'))])
        lines_initial = initial.mapped('lines_initial')
        return lines_initial
    
    def _get_default_lines_surveillance(self):
        surveillance = self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids'))])
        lines_surveillance = surveillance.mapped('lines_surveillance')
        return lines_surveillance

    def _get_default_standards(self):
        all_standards = self.env['tsi.iso'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['waiting', 'approved'])])
        standards = all_standards.mapped('iso_standard_ids')
        return standards

    form_id	    = fields.Many2one('tsi.iso', string='No Document',  default=_get_default_reference)
    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)
    # packing_date    = fields.Date('Date',required=True, default=fields.Date.today())
    apprev_ids 	    = fields.Many2many('tsi.iso', string='Application Form',  default=_get_default_review)
    initial_ids 	    = fields.Many2many('tsi.iso.initial', string='Lines Initial',  default=_get_default_lines_initial)
    surveillance_ids 	    = fields.Many2many('tsi.iso.surveillance', string='Lines Surveillance',  default=_get_default_lines_surveillance)
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type',  default=_get_default_doctype, readonly=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standards)
    nomor_kontrak = fields.Char(string='Nomor Kontrak', readonly=True, compute='_compute_nomor_kontrak')

    @api.depends('form_id')
    def _compute_nomor_kontrak(self):
        for wizard in self:
            sale_order = self.env['sale.order'].search([('iso_reference', '=', wizard.form_id.id)], limit=1)
            wizard.nomor_kontrak = sale_order.nomor_kontrak if sale_order else 'Nomor kontrak belum dibuat'

    def send(self):
        if not self.partner_id:
            raise UserError('Partner harus diisi.')

        # Cek apakah status sales sudah berada di status yang tidak bisa diubah
        if self.form_id.state_sales in ['waiting_verify_operation', 'sent', 'sale']:
            raise UserError('Tidak bisa membuat quotation atau mengubah status karena status sales saat ini adalah: ' + self.form_id.state_sales)

        # Cek apakah `state_sales` sudah dalam state 'client_approval'
        if self.form_id.state_sales == 'client_approval':
            raise UserError('Quotation sudah dibuat dan dalam status Client Approval, tidak dapat membuat quotation lagi.')

        reference_id = self.form_id.id

        # Cek apakah `sale_order_id` sudah ada pada `form_id`
        if self.form_id.sale_order_id:
            # Jika sudah ada, gunakan `sale_order_id` yang sudah terisi
            sale_order = self.form_id.sale_order_id
        else:
            # Jika belum ada, buat `sale.order` baru
            sale_order = self.env['sale.order'].create({
                'iso_reference': reference_id,
                'partner_id': self.partner_id.id,
                'doctype': self.doctype,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],  # Format Many2many
            })
            # Link `sale_order_id` ke form_id
            self.form_id.sale_order_id = sale_order.id

        # Refresh nomor_kontrak
        self._compute_nomor_kontrak()

        # Menambahkan options untuk order
        order_options = []
        for surveillance in self.surveillance_ids:
            order_options.append((0, 0, {
                'surveillance_id': surveillance.id,
                'tahun_audit': surveillance.tahun,
                'price_units': surveillance.price,
                'audit_tahapan': surveillance.audit_stage,
                'quanty': 1.0,
            }))
        if order_options:
            sale_order.write({
                'sale_order_options': order_options,
            })

        # Menambahkan order lines untuk initial_ids
        order_lines = []
        for initial in self.initial_ids:
            order_lines.append((0, 0, {
                'order_id': sale_order.id,
                'product_id': initial.product_id.id if initial.product_id else False,
                'tahun': initial.tahun,
                'price_unit': initial.price,
                'in_pajak': initial.in_pajak,
                'ex_pajak': initial.ex_pajak,
                'product_uom_qty': 1.0,
                'audit_tahapan': initial.audit_stage,
            }))
        if order_lines:
            sale_order.write({
                'order_line': order_lines,
            })

        # Update status untuk form_id terkait
        iso_app = self.env['tsi.iso'].browse(reference_id)
        iso_app.compute_state()

        # Update the status of sale order
        sale_order.write({'state': 'cliennt_approval'})

