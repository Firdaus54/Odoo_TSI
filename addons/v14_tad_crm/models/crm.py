from odoo import models, fields, api

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    tender_id = fields.Many2one('tad.tender', string="Tender Reference")
