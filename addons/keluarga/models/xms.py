# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class SkemaXMS(models.Model):
    _name = 'skema.xms'
    _description = 'Data Skema XMS'
    _order          = 'id DESC'

    name = fields.Char(string='Document Name', required=True)
    id_dokumen = fields.Char(string="Dokumen ID", default='New', readonly=True, copy=False)
    nomor_dokumen = fields.Char(string="Nomor Dokumen")
    upload_date = fields.Datetime(string="Upload Date&Time", default=datetime.today())
    attachment = fields.Binary('Attachment')
    user_id = fields.Many2one(
        'res.users', string='Uploader_ID', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    document_type = fields.Selection([('docx', 'DOCX'), ('pdf', 'PDF'), ('xls', 'XLS')], string="Document Type")
    file_name       = fields.Char('Filename')
    edition_number  = fields.Char('Edition')
    original_date  = fields.Date('Original Date')
    revisi_date  = fields.Date('Revision Date')
    initial_date  = fields.Date('Initial Date')
    issued_date  = fields.Date('Issued Date')
    authorisasi = fields.Char('Authorisasi Document')
    revisi_number  = fields.Char('Revision Number')
    approval_by = fields.Char('Approval By')
    approval_date   = fields.Date('Approval Date')

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('id_dokumen', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('skema.xms') or 'New'
            vals['id_dokumen'] = 'Dok/%s/%s/%s' %(datetime.today().month,datetime.today().year, seq_number)
            result = super(SkemaXMS, self).create(vals)
        return result
