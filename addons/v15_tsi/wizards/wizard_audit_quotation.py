from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class WizardAuditQuotation(models.TransientModel):
    _name = 'tsi.wizard_audit_quotation'
    _description = 'Wizard for Quotation'

    def _get_default_partner(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))],limit=1).partner_id

    def _get_default_iso(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_reference

    def _get_default_sales(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))],limit=1).sales_reference

    def _get_default_review(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))],limit=1).review_reference

    def _get_default_iso(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)

    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type',  default='iso', readonly=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True,   default=_get_default_iso)
    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True,   default=_get_default_partner)
    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True, default=_get_default_iso)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True, default=_get_default_sales)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True, default=_get_default_review)

    def send(self):
        if self.partner_id :

            quotation = self.env['sale.order'].create({
                'iso_reference'             : self.iso_reference.id,
                'application_review_ids'    : self.review_reference,
                'doctype'                   : self.doctype,
                'partner_id'                : self.partner_id.id,
                'iso_standard_ids'          : self.iso_standard_ids
            })

            # if quotation :
            #     for application_review in self.apprev_ids:
