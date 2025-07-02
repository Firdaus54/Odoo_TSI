from odoo import models, fields, api, http, SUPERUSER_ID, _
import base64
from datetime import datetime

class AuditReview(models.Model):
    _name           = 'ops.review'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Recommendation'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    iso_reference   = fields.Many2one('tsi.iso', string="Reference")
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    nama_customer   = fields.Many2one('res.partner', string="Customer", related='report_id.customer')    
    criteria        = fields.Char(string='Criteria', track_visibility='always')
    objectives      = fields.Text(string='Objectives')
    iso_standard_ids= fields.Many2many('tsi.iso.standard', string='Standards')
    notification_id = fields.Many2one('audit.notification', string="Notification")    
    sales_order_id  = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    
    upload_dokumen  = fields.Binary('Documen Audit', track_visibility='always')
    report_id       = fields.Many2one('ops.report', string='Report')
    program_id      = fields.Many2one('ops.program', string='Program')
    review_summary  = fields.One2many('ops.review_summary', 'review_id', string="Detail", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('approve', 'Approve'),
                            ('waiting_finance', 'Waiting Finance Set Lunas Payment'),
                            ('reject', 'Reject'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')
    dokumen_sosialisasi = fields.Binary('Organization Chart', track_visibility='always')
    file_name1      = fields.Char('Filename', track_visibility='always')
    file_name2      = fields.Char('Filename', track_visibility='always')
    # Fields baru yang ditambahkan untuk Survillance dan Recertification
    survillance_type = fields.Selection([
        ('Survillance-1', 'Survillance 1'),
        ('Survillance-2', 'Survillance 2'),
    ], string="Survillance Type", default='Survillance-1')

    recertification_type = fields.Selection([
        ('recertification', 'Recertification'),
    ], string="Recertification Type", default='recertification')

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.review')
        vals['name'] = sequence or _('New')
        result = super(AuditReview, self).create(vals)
        return result


    def set_to_confirm(self):
        self.write({'state': 'approve'})            
        return True
    
    def set_to_reject(self):
        self.write({'state': 'reject'})            
        return True

    def set_to_done(self):
        self.write({'state': 'waiting_finance'})
        sertifikat_obj = self.env['ops.sertifikat']
        for review in self:
            for summary in review.review_summary:
                if summary.date:
                    sertifikat_obj.create({'review_summary_id': summary.id,
                                           'iso_reference' : self.iso_reference.id,
                                           'sales_order_id' : self.sales_order_id.id,
                                           'notification_id' : self.notification_id.id,
                                           'iso_standard_ids' : [(6, 0, self.iso_standard_ids.ids)]})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True
    
    def audit_notification(self):
        # Code to generate Stage 1 report
        return self.env.ref('v15_tsi.audit_recomendation').report_action(self)

class AuditReviewDetail(models.Model):
    _name           = 'ops.review_summary'
    _description    = 'Audit Review Summary'

    review_id       = fields.Many2one('ops.review', string="Review", ondelete='cascade', index=True)
    remarks         = fields.Char(string='Remarks')
    status          = fields.Selection([
                                        ('reject', 'Reject'),
                                        ('Ok', 'Ok'),
                                    ], string="Status")
    attachment      = fields.Binary('Upload Doc')
    file_name1      = fields.Char('Filename', track_visibility='always')
    date            = fields.Date(string="Date Notification", default=datetime.today())

    @api.onchange('status')
    def onchange_status(self):
        if self.status == 'reject':
            # Tambahkan baris baru secara otomatis
            self.create({
                'review_id': self.review_id.id,
                # Isi field lainnya sesuai kebutuhan
            })
    # @api.onchange('status')
    # def onchange_status(self):
    #     if self.status == 'reject' and self.review_id:
    #         # Tambahkan baris baru secara otomatis
    #         self.review_id.write({'review_summary': [(0, 0, {
    #             # Isi field lainnya sesuai kebutuhan
    #         })]})
