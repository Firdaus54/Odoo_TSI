from odoo import models, fields, api, _
from datetime import datetime, timedelta, date

class AuditNotification(models.Model):
    _name           = 'audit.notification'
    _description    = 'Audit Notification'
    _order          = 'id DESC'

    name                = fields.Char(string='Document No',  readonly=True)
    iso_reference       = fields.Many2one('tsi.iso', string="Reference",  readonly=True)    
    customer            = fields.Many2one('res.partner', string="Customer", related='sales_order_id.partner_id')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

    plan_lines          = fields.One2many('ops.plan', 'notification_id', string="Plan", index=True,  readonly=True)
    program_lines       = fields.One2many('ops.program', 'notification_id', string="Program", index=True,  readonly=True)
    report_lines        = fields.One2many('ops.report', 'notification_id', string="Report", index=True,  readonly=True)
    review_lines        = fields.One2many('ops.review', 'notification_id', string="Review", index=True,  readonly=True)
    sertifikat_lines    = fields.One2many('ops.sertifikat', 'notification_id', string="Sertifikat", index=True,  readonly=True)
    # delivery_sertifikat_line = fields.One2many('sertifikat.delivery', 'notification_id', string="Delivery Sertifikat", index=True,  readonly=True)
    audit_state = fields.Selection([
        ('program', 'Program'),
        ('Stage-1', 'Stage-1'),
        ('Stage-2', 'Stage-2'),
        ('Surveillance1', 'Surveillance1'),
        ('Surveillance2', 'Surveillance2'),
        ('Recertification', 'Recertification'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status', compute='_compute_audit_status', store=True)

    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', related="sales_order_id.tipe_pembayaran", readonly=False)

    # Field computed untuk menggabungkan nilai tgl_perkiraan_selesai dan tgl_perkiraan_audit_selesai
    tgl_perkiraan_selesai = fields.Date(
        string="Plan of Audit Date",
        compute='_compute_tgl_perkiraan_selesai',  # Computed berdasarkan sales_order_id
        store=True  # Simpan nilainya di database agar tidak hilang
    )

    # @api.depends('sales_order_id.tgl_perkiraan_audit_selesai')
    # def _compute_tgl_perkiraan_selesai(self):
    #     for record in self:
    #         # Cek jika sales_order_id ada dan field tgl_perkiraan_audit_selesai ada
    #         if record.sales_order_id:
    #             # Ambil nilai dari tgl_perkiraan_audit_selesai (Selection)
    #             audit_date = record.sales_order_id.tgl_perkiraan_audit_selesai
    #             if audit_date:
    #                 # Ubah nilai dari selection menjadi Date
    #                 record.tgl_perkiraan_selesai = fields.Date.from_string(audit_date)
    #             else:
    #                 # Jika tgl_perkiraan_audit_selesai kosong, biarkan nilai lama di tgl_perkiraan_selesai
    #                 pass
    
    @api.depends('sales_order_id')
    def _compute_tgl_perkiraan_selesai(self):
        for record in self:
            if record.sales_order_id:
                if record.sales_order_id.tgl_perkiraan_audit_selesai:
                    # Mengonversi string menjadi date
                    tgl_selesai = datetime.strptime(record.sales_order_id.tgl_perkiraan_audit_selesai, "%Y-%m-%d").date()
                    record.tgl_perkiraan_selesai = tgl_selesai
                elif record.sales_order_id.tgl_perkiraan_selesai:
                    # Jika tgl_perkiraan_selesai ada, pakai nilai tersebut
                    record.tgl_perkiraan_selesai = record.sales_order_id.tgl_perkiraan_selesai
            else:
                record.tgl_perkiraan_selesai = False

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('audit.notification')
        vals['name'] = sequence or _('New')
        result = super(AuditNotification, self).create(vals)
        return result
    
    @api.depends('program_lines.state', 'plan_lines.state', 'report_lines.state', 'review_lines.state', 'sertifikat_lines.state')
    def _compute_audit_status(self):
        for record in self:
            if any(program.state == 'done' for program in record.program_lines):
                record.audit_state = 'Stage-1'
            if any(program.state == 'done_stage2' for program in record.program_lines):
                record.audit_state = 'Stage-2'
            if any(program.state == 'done_surveillance1' for program in record.program_lines):
                record.audit_state = 'Surveillance1'
            if any(program.state == 'done_surveillance2' for program in record.program_lines):
                record.audit_state = 'Surveillance2'
            if any(program.state == 'done_recertification' for program in record.program_lines):
                record.audit_state = 'Recertification'
            if any(plan.state == 'done' for plan in record.plan_lines):
                record.audit_state = 'plan'
            if any(report.state == 'done' for report in record.report_lines):
                record.audit_state = 'report'
            if any(recommendation.state in ['waiting_finance', 'done'] for recommendation in record.review_lines):
                record.audit_state = 'recommendation'
            # elif any(recommendation.state == 'done' for recommendation in record.review_lines):
            #     record.audit_state = 'Recommendation'
            if any(certificate.state == 'done' for certificate in record.sertifikat_lines):
                record.audit_state = 'certificate'
            if any(program.state == 'new' for program in record.program_lines):
                record.audit_state = 'draft'

    def write(self, vals):
        res = super(AuditNotification, self).write(vals)
        # Set audit status when any related audit status is updated
        if any(key in vals for key in ['program_lines', 'plan_lines', 'report_lines', 'review_lines', 'sertifikat_lines']):
            self._compute_audit_status()
        return res