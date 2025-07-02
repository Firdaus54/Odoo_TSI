from odoo import models, fields, api, SUPERUSER_ID, _

class AuditReportISPO(models.Model):
    _name           = 'ops.report.ispo'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Report'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference")
    plan_reference   = fields.Many2one('ops.plan.ispo', string="Plan Reference")
    notification_id = fields.Many2one('audit.notification.ispo', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

# related, ea_code ???
    customer            = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", related='ispo_reference.contact_person')
    head_office         = fields.Char(string="Head Office", related='ispo_reference.head_office')
    site_office         = fields.Char(string="Site Office", related='ispo_reference.site_office')
    off_location        = fields.Char(string="Off Location", related='ispo_reference.off_location')
    part_time           = fields.Char(string="Part Time", related='ispo_reference.part_time')
    subcon              = fields.Char(string="Sub Contractor", related='ispo_reference.subcon')
    unskilled           = fields.Char(string="Unskilled", related='ispo_reference.unskilled')
    seasonal            = fields.Char(string="Seasonal", related='ispo_reference.seasonal')
    total_emp           = fields.Integer(string="Total Employee", related='ispo_reference.partner_site.total_emp')
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIKk'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True, related='ispo_reference.scope')
    boundaries          = fields.Text('Boundaries', related='ispo_reference.boundaries')
    # boundaries_id  = fields.Many2many('tsi.iso.boundaries', string="Boundaries", related="ispo_reference.boundaries_id")
    telepon             = fields.Char(string="No Telepon", related='ispo_reference.telepon')

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
    
    no_finding_lines = fields.One2many('ops.report.ispo.no_finding.line', 'ops_report_id', string='No Finding Lines')
    minor_lines = fields.One2many('ops.report.ispo.minor.line', 'ops_report_id', string='Minor Lines')
    major_lines = fields.One2many('ops.report.ispo.major.line', 'ops_report_id', string='Major Lines')
    dokumen_sosialisasi = fields.Binary('Organization Chart', related='sales_order_id.dokumen_sosialisasi')
    file_name1      = fields.Char('Filename', related='sales_order_id.file_name1')
    file_name2      = fields.Char('Filename')
    
    def set_to_confirm(self):
        self.write({'state': 'approve'})
        self.update_ops_review()            
        return True

    def update_ops_review(self):
        if self.sales_order_id :    
            for standard in self.ispo_reference.iso_standard_ids :
                # Jika tidak ada ops.review, buat yang baru
                review = self.env['ops.review'].create({
                # 'report_id': report.id,
                    'criteria' : self.criteria,
                    'upload_dokumen': self.upload_dokumen,
                    'ispo_reference'     : self.ispo_reference.id,
                    'sales_order_id'    : self.sales_order_id.id,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1'    : self.file_name1,
                    'file_name2'    : self.file_name2,
                    'iso_standard_ids'  : standard,
                    'notification_id'   : self.notification_id.id,
                    'report_id'         : self.id   
                })

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
        sequence = self.env['ir.sequence'].next_by_code('ops.report.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditReportISPO, self).create(vals)
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

class OpsReportISPONoFindingLine(models.Model):
    _name = 'ops.report.ispo.no_finding.line'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report')
    audit_plan = fields.Binary(string='Audit Plan')
    file_name1 = fields.Char('File Name')
    attendance_sheet = fields.Binary(string='Attendance Sheet')
    file_name2 = fields.Char('File Name')
    audit_report = fields.Binary(string='Audit Report')
    file_name3 = fields.Char('File Name')
    temuan  = fields.Integer(string="Temuan")

class OpsReportISPOMinorLine(models.Model):
    _name = 'ops.report.ispo.minor.line'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report')
    audit_plan = fields.Binary(string='Audit Plan')
    file_name1 = fields.Char('File Name')
    attendance_sheet = fields.Binary(string='Attendance Sheet')
    file_name2 = fields.Char('File Name')
    audit_report = fields.Binary(string='Audit Report')
    file_name3 = fields.Char('File Name')
    close_findings = fields.Binary(string='Close Findings')
    file_name4 = fields.Char('File Name')
    temuan  = fields.Integer(string="Temuan")

class OpsReportISPOMajorLine(models.Model):
    _name = 'ops.report.ispo.major.line'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report')
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

# class AuditReportDetail(models.Model):
#     _name           = 'ops.report_summary'
#     _description    = 'Audit Report Summary'

#     report_id       = fields.Many2one('ops.report', string="Report", ondelete='cascade', index=True)
#     summary         = fields.Char(string='Summary')
#     status          = fields.Char(string='Status')
