from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class WizardAuditRequest(models.TransientModel):
    _name = 'tsi.wizard_audit_request'
    _description = 'Wizard Audit Request'

    def _get_default_partner(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).partner_id

    def _get_default_tipe_pembayaran(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).tipe_pembayaran
    
    def _get_default_nomor_kontrak(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).no_kontrak

    def _get_default_iso_reference(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).iso_reference
    
    # def _get_default_lines_request(self):
    #     request = self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))])
    #     lines_request = request.mapped('lines_audit_request')
    #     return lines_request

    def _get_default_lines_request(self):
        
        requests = self.env['tsi.audit.request'].search([('id', 'in', self.env.context.get('active_ids'))])
        if requests:
            lines_request = requests.mapped('lines_audit_request')
            return lines_request
        return False

    def _get_default_standards(self):
        all_standards = self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])])
        standards = all_standards.mapped('iso_standard_ids')
        return standards
    
    # Method untuk mendapatkan default untuk is_amendment
    def _get_default_is_amendment(self):
        # Ambil nilai is_amendment dari tsi.audit.request
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            # Cari audit request yang aktif
            requests = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if requests:
                return requests.is_amendment
        # Default untuk kontrak baru adalah False
        return False

    # Method untuk mendapatkan default untuk contract_type
    def _get_default_contract_type(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            # Cari audit request yang aktif
            requests = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if requests:
                # Ambil contract_type dari audit request yang ditemukan
                contract_type = requests.contract_type
                if contract_type:
                    return contract_type
        # Jika tidak ada request yang aktif, anggap ini adalah kontrak baru
        return 'new'

    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)
    request_ids 	= fields.Many2many('audit_request.line', string='Lines Audit Request',  default=_get_default_lines_request)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standards)
    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True, default=_get_default_iso_reference)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran', readonly=True, default=_get_default_tipe_pembayaran)
    no_kontrak          = fields.Char(string='Nomor Kontrak', default=_get_default_nomor_kontrak)
    is_amendment = fields.Boolean(string="Is Amendment Contract?", default=_get_default_is_amendment)
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract", default=_get_default_contract_type)

    def send(self):

        # Cek apakah sudah ada sale.order untuk customer & iso_reference yang sama
        existing_order = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('iso_reference', '=', self.iso_reference.id),
            ('state', '!=', 'cancel'),  # kalau kamu anggap yang cancel boleh dibuat ulang
        ], limit=1)

        if existing_order:
            raise ValidationError(
                f"Sales Order untuk customer '{self.partner_id.name}' dan ISO '{self.iso_reference.name}' sudah ada."
            )

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tipe_pembayaran': self.tipe_pembayaran,
            'iso_reference': self.iso_reference.id,
            'contract_type': self.contract_type,
            'nomor_kontrak': self.no_kontrak,
            'nomor_quotation': self.no_kontrak,
        })

        for line in self.request_ids:
            product = line.product_id

            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': line.product_id.id,
                'audit_tahapan': line.audit_tahapan,
                'tahun': line.tahun,
                'price_unit': line.price,
            })

        # sale_order.action_confirm()
        sale_order.write({'state': 'sent'})
        
        return True