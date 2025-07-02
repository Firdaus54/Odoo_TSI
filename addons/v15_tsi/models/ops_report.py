from odoo import models, fields, api, SUPERUSER_ID, _
import logging

# Mendefinisikan logger
_logger = logging.getLogger(__name__)

class AuditReport(models.Model):
    _name           = 'ops.report'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Report'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    iso_reference   = fields.Many2one('tsi.iso', string="Reference")
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    plan_reference   = fields.Many2one('ops.plan', string="Plan Reference")
    notification_id = fields.Many2one('audit.notification', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

# related, ea_code ???
    customer = fields.Many2one('res.partner', string="Customer", compute='_compute_customer', store=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", related='iso_reference.contact_person')
    head_office         = fields.Char(string="Head Office", related='iso_reference.head_office')
    site_office         = fields.Char(string="Site Office", related='iso_reference.site_office')
    off_location        = fields.Char(string="Off Location", related='iso_reference.off_location')
    part_time           = fields.Char(string="Part Time", related='iso_reference.part_time')
    subcon              = fields.Char(string="Sub Contractor", related='iso_reference.subcon')
    unskilled           = fields.Char(string="Unskilled", related='iso_reference.unskilled')
    seasonal            = fields.Char(string="Seasonal", related='iso_reference.seasonal')
    total_emp           = fields.Integer(string="Total Employee", related='iso_reference.partner_site.total_emp')
    scope               = fields.Text('Scope', related='iso_reference.scope')
    boundaries          = fields.Text('Boundaries', related='iso_reference.boundaries')
    # boundaries_id  = fields.Many2many('tsi.iso.boundaries', string="Boundaries", related="iso_reference.boundaries_id")
    telepon             = fields.Char(string="No Telepon", related='iso_reference.telepon')

    ea_code             = fields.Char(string="EA Code")
    type_cient          = fields.Char(string="Seasonal")
    apprev_date         = fields.Date(string="Review Date")    
    contract_date       = fields.Date(string="Contract Date")    


    criteria        = fields.Char(string='Criteria')
    objectives      = fields.Text(string='Objectives')
    upload_dokumen  = fields.Binary('Documen Audit')
    audit_stage           = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], string="Audit Stage", readonly=True, related="plan_reference.audit_stage")
    # report_id       = fields.Many2one('ops.report', string='Report')

# audit general
    contract_number     = fields.Char('Contract Number')
    audit_start         = fields.Char('Audit Start')
    audit_end           = fields.Char('Audit End')
    certification_type  = fields.Char('Certification Type')
    standards           = fields.Char('Standards')
    audit_criteria      = fields.Char('Audit Criteria')
    audit_method        = fields.Char('Audit Method')

    auditor_lead        = fields.Many2one('hr.employee', string="Nama Auditor")
    auditor_1           = fields.Many2one('hr.employee', string='Auditor 1')
    auditor_2           = fields.Many2one('hr.employee', string='Auditor 2')
    auditor_3           = fields.Many2one('hr.employee', string='Auditor 3')

    kan_1               = fields.Char('Auditor KAN 1')
    kan_2               = fields.Char('Auditor KAN 2')

    audit_objectives    = fields.Many2many('ops.objectives',string='Audit Objectives')
    
# executive summary

    report_summary  = fields.One2many('ops.report_summary', 'report_id', string="Plan", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('done',    'Done'),
                            ('approve', 'Approve'),
                            ('reject',    'Reject')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')

    finding_type = fields.Selection([
        ('no_finding', 'No Finding'),
        ('minor', 'Minor'),
        ('major', 'Major')
    ], string='Finding Type')
    
    no_finding_lines = fields.One2many('ops.report.no_finding.line', 'ops_report_id', string='No Finding Lines')
    minor_lines = fields.One2many('ops.report.minor.line', 'ops_report_id', string='Minor Lines')
    major_lines = fields.One2many('ops.report.major.line', 'ops_report_id', string='Major Lines')
    dokumen_sosialisasi = fields.Binary('Organization Chart', related='sales_order_id.dokumen_sosialisasi')
    file_name1      = fields.Char('Filename', related='sales_order_id.file_name1')
    file_name2      = fields.Char('Filename')
    # is_iso_27001 = fields.Boolean(compute='_compute_is_iso_27001', store=False)
    # Fields lainnya
    survillance_type = fields.Selection([
        ('Survillance-1', 'Survillance 1'),
        ('Survillance-2', 'Survillance 2'),
    ], string="Survillance Type", default='Survillance-1')

    recertification_type = fields.Selection([
        ('recertification', 'Recertification'),
    ], string="Recertification Type", default='recertification')

    @api.depends('sales_order_id.partner_id', 'iso_reference.customer')
    def _compute_customer(self):
        for rec in self:
            if rec.sales_order_id and rec.sales_order_id.partner_id:
                rec.customer = rec.sales_order_id.partner_id
            elif rec.iso_reference and rec.iso_reference.customer:
                rec.customer = rec.iso_reference.customer
            else:
                rec.customer = False

    # @api.onchange('iso_standard_ids')
    # def _onchange_iso_standard_ids(self):
    #     # Daftar ISO yang diinginkan
    #     target_iso_codes = ['ISO/IEC 27001', 'ISO 27001:2022', 'ISO/IEC 27017:2015']
        
    #     # Cek apakah salah satu ISO dari target_iso_codes ada dalam iso_standard_ids
    #     iso_27001_selected = any(iso_standard.code in target_iso_codes for iso_standard in self.iso_standard_ids)
        
    #     # Set visibility untuk review_27001 di baris terkait
    #     for line in self.no_finding_lines:
    #         line.review_27001_visible = iso_27001_selected
    #     for line in self.minor_lines:
    #         line.review_27001_visible = iso_27001_selected
    #     for line in self.major_lines:
    #         line.review_27001_visible = iso_27001_selected

    def action_review_stage_27001(self):
        # Code to generate Stage 1 report
        return self.env.ref('v15_tsi.audit_review_stage').report_action(self)
    
    def set_to_confirm(self):
        _logger.info(f"🚀 set_to_confirm dipanggil untuk report: {self.id}")
        self.write({'state': 'approve'})
        self.update_ops_review()
        return True

    def update_ops_review(self):
        _logger.info(f"🚀 Mulai update_ops_review untuk report {self.name or self.id}")
        
        if (self.iso_reference or self.reference_request_ids) and self.iso_standard_ids:
            _logger.info(f"ISO Reference: {getattr(self.iso_reference, 'id', 'N/A')}, "
                        f"Reference Requests: {self.reference_request_ids.ids if self.reference_request_ids else []}, "
                        f"ISO Standards: {self.iso_standard_ids.ids}")

            audit_stage = (self.audit_stage or '').lower()
            if audit_stage == 'stage-02':
                self.create_ops_review_for_stage_02()
            elif audit_stage == 'survillance-1':
                self.create_ops_review_for_survillance('Survillance-1')
            elif audit_stage == 'survillance-2':
                self.create_ops_review_for_survillance('Survillance-2')
            elif audit_stage == 'recertification':
                self.create_ops_review_for_recertification()
            else:
                _logger.info(f"❌ Audit Stage tidak dikenali atau bukan salah satu dari yang ditentukan: {self.audit_stage}")
    
    def create_ops_review_for_stage_02(self):
        # Logic untuk 'Stage-02'
        for standard in self.iso_standard_ids:
            vals = {
                'criteria': self.criteria,
                'upload_dokumen': self.upload_dokumen,
                'iso_reference': self.iso_reference.id,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'file_name2': self.file_name2,
                'iso_standard_ids': [(6, 0, [standard.id])],
                'notification_id': self.notification_id.id,
                'report_id': self.id
            }
            # Tambahkan sales_order_id jika ada
            if self.sales_order_id:
                vals['sales_order_id'] = self.sales_order_id.id

            review = self.env['ops.review'].create(vals)
            _logger.info(f"✅ Ops Review created for Stage-02: {review.id}")

    def create_ops_review_for_survillance(self, survillance_type):
        _logger.info(f"✅ Mulai create_ops_review_for_survillance {survillance_type}")
        
        for standard in self.iso_standard_ids:
            vals = {
                'criteria': self.criteria,
                'upload_dokumen': self.upload_dokumen,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'file_name2': self.file_name2,
                'iso_standard_ids': [(6, 0, [standard.id])],
                'notification_id': self.notification_id.id,
                'report_id': self.id,
                'survillance_type': survillance_type
            }

            # Tambahkan iso_reference jika ada
            if self.iso_reference:
                vals['iso_reference'] = self.iso_reference.id
                _logger.info("📌 iso_reference ditambahkan")

            # Tambahkan reference_request_ids jika ada
            if self.reference_request_ids:
                vals['reference_request_ids'] = [(6, 0, self.reference_request_ids.ids)]
                _logger.info("📌 reference_request_ids ditambahkan")

            # Tambahkan sales_order_id jika ada
            if self.sales_order_id:
                vals['sales_order_id'] = self.sales_order_id.id

            # Jika salah satu ada → baru create
            if self.iso_reference or self.reference_request_ids:
                review = self.env['ops.review'].create(vals)
                _logger.info(f"✅ Ops Review created for {survillance_type}: {review.id}")
            else:
                _logger.info("⚠ Ops Review tidak dibuat karena iso_reference & reference_request_ids kosong dua-duanya")


    def create_ops_review_for_recertification(self):
        _logger.info("✅ Mulai create_ops_review_for_recertification")

        for standard in self.iso_standard_ids:
            vals = {
                'criteria': self.criteria,
                'upload_dokumen': self.upload_dokumen,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'file_name2': self.file_name2,
                'iso_standard_ids': [(6, 0, [standard.id])],
                'notification_id': self.notification_id.id,
                'report_id': self.id,
                'recertification_type': 'Recertification'
            }

            # Tambahkan iso_reference kalau ada
            if self.iso_reference:
                vals['iso_reference'] = self.iso_reference.id
                _logger.info("📌 iso_reference ditambahkan")

            # Tambahkan reference_request_ids kalau ada
            if self.reference_request_ids:
                vals['reference_request_ids'] = [(6, 0, self.reference_request_ids.ids)]
                _logger.info("📌 reference_request_ids ditambahkan")

            # Tambahkan sales_order_id kalau ada
            if self.sales_order_id:
                vals['sales_order_id'] = self.sales_order_id.id

            # Hanya buat ops.review kalau ada minimal salah satu
            if self.iso_reference or self.reference_request_ids:
                review = self.env['ops.review'].create(vals)
                _logger.info(f"✅ Ops Review created for Recertification: {review.id}")
            else:
                _logger.info("⚠ Ops Review tidak dibuat karena iso_reference & reference_request_ids kosong dua-duanya")



    def set_to_done(self):
        self.write({'state': 'done'})           
        return True
    
    def set_reject(self):
        self.write({'state': 'reject'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.report')
        vals['name'] = sequence or _('New')
        result = super(AuditReport, self).create(vals)
        return result

    @api.onchange('finding_type')
    def _onchange_finding_type(self):
        if self.finding_type == 'no_finding':
            self.no_finding_lines = [(5, 0, 0)]
            self.minor_lines = [(5, 0, 0)]
            self.major_lines = [(5, 0, 0)]
        elif self.finding_type == 'minor':
            self.no_finding_lines = [(5, 0, 0)]
            self.minor_lines = [(0, 0, {})]  # Initialize minor lines as needed
            self.major_lines = [(5, 0, 0)]
        elif self.finding_type == 'major':
            self.no_finding_lines = [(5, 0, 0)]
            self.minor_lines = [(0, 0, {})]  # Initialize minor lines as needed
            self.major_lines = [(0, 0, {})]  # Initialize major lines as needed

class OpsReportNoFindingLine(models.Model):
    _name = 'ops.report.no_finding.line'

    ops_report_id = fields.Many2one('ops.report', string='Ops Report')
    audit_plan = fields.Binary(string='Audit Plan')
    file_name1 = fields.Char('File Name')
    attendance_sheet = fields.Binary(string='Attendance Sheet')
    file_name2 = fields.Char('File Name')
    audit_report = fields.Binary(string='Audit Report')
    file_name3 = fields.Char('File Name')
    temuan  = fields.Integer(string="Temuan")
    review_27001 = fields.Binary(string='Review 27001')
    file_name4 = fields.Char('File Name')

class OpsReportMinorLine(models.Model):
    _name = 'ops.report.minor.line'

    ops_report_id = fields.Many2one('ops.report', string='Ops Report')
    audit_plan = fields.Binary(string='Audit Plan')
    file_name1 = fields.Char('File Name')
    attendance_sheet = fields.Binary(string='Attendance Sheet')
    file_name2 = fields.Char('File Name')
    audit_report = fields.Binary(string='Audit Report')
    file_name3 = fields.Char('File Name')
    close_findings = fields.Binary(string='Close Findings')
    file_name4 = fields.Char('File Name')
    temuan  = fields.Integer(string="Temuan")
    review_27001 = fields.Binary(string='Review 27001')
    file_name5 = fields.Char('File Name')

class OpsReportMajorLine(models.Model):
    _name = 'ops.report.major.line'

    ops_report_id = fields.Many2one('ops.report', string='Ops Report')
    audit_plan = fields.Binary(string='Audit Plan')
    file_name1 = fields.Char('File Name')
    attendance_sheet = fields.Binary(string='Attendance Sheet')
    file_name2 = fields.Char('File Name')
    audit_report = fields.Binary(string='Audit Report')
    file_name3 = fields.Char('File Name')
    close_findings = fields.Binary(string='Close Findings')
    file_name4 = fields.Char('File Name')
    verification_audit = fields.Binary(string='Verification Audit')
    file_name5 = fields.Char('File Name')
    verification_attendance = fields.Binary(string='Verification Attendance')
    file_name6 = fields.Char('File Name')
    verifikasi_audit = fields.Binary(string='Verifikasi Audit')
    file_name7 = fields.Char('File Name')
    temuan  = fields.Integer(string="Temuan")
    review_27001 = fields.Binary(string='Review 27001')
    file_name8 = fields.Char('File Name')

class AuditReportDetail(models.Model):
    _name           = 'ops.report_summary'
    _description    = 'Audit Report Summary'

    report_id       = fields.Many2one('ops.report', string="Report", ondelete='cascade', index=True)
    summary         = fields.Char(string='Summary')
    status          = fields.Char(string='Status')
