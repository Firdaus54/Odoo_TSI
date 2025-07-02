from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class WizardQuotation(models.TransientModel):
    _name = 'tsi.wizard_quotation'
    _description = 'Wizard for Quotation'

    def _get_default_partner(self):
        return self.env['tsi.iso.review'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])],limit=1).customer

    def _get_default_doctype(self):
        return self.env['tsi.iso.review'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])],limit=1).doctype

    def _get_default_review(self):
        return self.env['tsi.iso.review'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])])
    
    def _get_default_lines_initial(self):
        initial = self.env['tsi.iso.review'].search([('id','in',self.env.context.get('active_ids'))])
        lines_initial = initial.mapped('lines_initial')
        return lines_initial
    
    def _get_default_lines_surveillance(self):
        surveillance = self.env['tsi.iso.review'].search([('id','in',self.env.context.get('active_ids'))])
        lines_surveillance = surveillance.mapped('lines_surveillance')
        return lines_surveillance

    def _get_default_standards(self):
        all_standards = self.env['tsi.iso.review'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])])
        standards = all_standards.mapped('iso_standard_ids')
        return standards

    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)
    packing_date    = fields.Date('Date',required=True, default=fields.Date.today())
    apprev_ids 	    = fields.Many2many('tsi.iso.review', string='Application Review',  default=_get_default_review)
    initial_ids 	    = fields.Many2many('tsi.iso.initial', string='Lines Initial',  default=_get_default_lines_initial)
    surveillance_ids 	    = fields.Many2many('tsi.iso.surveillance', string='Lines Surveillance',  default=_get_default_lines_surveillance)
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type',  default=_get_default_doctype, readonly=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standards)

    def send(self):
        if self.apprev_ids:
            partner_id = self.apprev_ids[0].customer.id
            reference_id = self.apprev_ids[0].reference.id
            # Cek apakah semua hanya 1 partner
            for application_review in self.apprev_ids:
                if partner_id != application_review.customer.id:
                    raise UserError('Harus dari satu Customer')   
                _logger.info('Partner : ' + str(application_review.customer.id))

            # Buat sale.order
            quotation = self.env['sale.order'].create({
                'iso_reference': reference_id,
                'application_review_ids': self.apprev_ids,
                'doctype': self.doctype,
                'partner_id': self.partner_id.id,
                'iso_standard_ids': self.iso_standard_ids
            })

            # Buat opsi tambahan berdasarkan surveillance_ids
            order_options = []
            for surveillance in self.surveillance_ids:
                order_options.append((0, 0, {
                    'surveillance_id': surveillance.id,
                    'tahun_audit': surveillance.tahun,
                    'price_units': surveillance.price,
                    'audit_tahapan': surveillance.audit_stage,
                    'quanty': 1.0,  # Atur sesuai kebutuhan
                }))

            # Update sale.order dengan opsi tambahan
            if order_options:
                quotation.write({
                    'sale_order_options': order_options,
                })

            # Tambahkan sale.order.line berdasarkan initial_ids
            order_lines = []
            for initial in self.initial_ids:
                order_lines.append((0, 0, {
                    'order_id': quotation.id,  # ID dari sale.order yang baru dibuat
                    'product_id': initial.product_id.id if initial.product_id else False,  # Pastikan product_id diisi
                    # 'name': initial.audit_stage or 'Default Description',  # Atur deskripsi jika perlu
                    'tahun': initial.tahun,  # Pastikan field tahun diisi
                    'price_unit': initial.price,  # Sesuaikan dengan field harga di initial_ids
                    'product_uom_qty': 1.0,  # Atur sesuai kebutuhan
                    'audit_tahapan': initial.audit_stage,
                }))

            # Update sale.order dengan sale.order.line tambahan
            if order_lines:
                quotation.write({
                    'order_line': order_lines,
                })

            # Hitung state ISO
            iso_app = self.env['tsi.iso'].browse(reference_id)
            iso_app.compute_state()

            # if quotation :
            #     for application_review in self.apprev_ids:
