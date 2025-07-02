from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class WizardQuotationAPP(models.TransientModel):
    _name = 'tsi.wizard_quotation.app.ispo'
    _description = 'Wizard for Quotation App ISPO'

    def _get_default_reference(self):
        return self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])])

    def _get_default_partner(self):
        return self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])],limit=1).customer

    def _get_default_doctype(self):
        return self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])],limit=1).doctype

    def _get_default_review(self):
        return self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])])
    
    def _get_default_lines_initial(self):
        initial = self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids'))])
        lines_initial = initial.mapped('lines_initial')
        return lines_initial
    
    def _get_default_lines_surveillance(self):
        surveillance = self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids'))])
        lines_surveillance = surveillance.mapped('lines_surveillance')
        return lines_surveillance

    def _get_default_standards(self):
        all_standards = self.env['tsi.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['new', 'approved'])])
        standards = all_standards.mapped('iso_standard_ids')
        return standards

    form_id	    = fields.Many2one('tsi.ispo', string='Application Form',  default=_get_default_reference)
    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)
    # packing_date    = fields.Date('Date',required=True, default=fields.Date.today())
    apprev_ids 	    = fields.Many2many('tsi.ispo', string='Application Review',  default=_get_default_review)
    initial_ids 	    = fields.Many2many('tsi.iso.initial', string='Lines Initial',  default=_get_default_lines_initial)
    surveillance_ids 	    = fields.Many2many('tsi.iso.surveillance', string='Lines Surveillance',  default=_get_default_lines_surveillance)
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type',  default=_get_default_doctype, readonly=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standards)

    def send(self):
        if not self.partner_id:
            raise UserError('Partner harus diisi.')

        reference_id = self.form_id.id

        quotation = self.env['sale.order'].create({
            'ispo_reference': reference_id,
            'partner_id': self.partner_id.id,
            'doctype': self.doctype,
            'iso_standard_ids': self.iso_standard_ids,
        })

        order_options = []
        for surveillance in self.surveillance_ids:
            order_options.append((0, 0, {
                'surveillance_id': surveillance.id,
                'tahun_audit': surveillance.tahun,
                'price_units': surveillance.price,
                'audit_tahapan': surveillance.audit_stage_ispo,
                'quanty': 1.0,
            }))

        if order_options:
            quotation.write({
                'sale_order_options': order_options,
            })

        order_lines = []
        for initial in self.initial_ids:
            order_lines.append((0, 0, {
                'order_id': quotation.id,
                'product_id': initial.product_id.id if initial.product_id else False,
                'tahun': initial.tahun,
                'price_unit': initial.price,
                'in_pajak': initial.in_pajak,
                'ex_pajak': initial.ex_pajak,
                'product_uom_qty': 1.0,
                'audit_tahapan': initial.audit_stage,
            }))

        if order_lines:
            quotation.write({
                'order_line': order_lines,
            })

        iso_app = self.env['tsi.ispo'].browse(reference_id)
        iso_app.compute_state()
