from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime

class AuditProgram(models.Model):
    _name           = 'ops.program'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Program'
    _order          = 'id DESC'

    name                = fields.Char(string='Document No')
    iso_reference       = fields.Many2one('tsi.iso', string="Reference")
# related, ea_code ???
    notification_id = fields.Many2one('audit.notification', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

    customer            = fields.Many2one('res.partner', string="Customer", related='sales_order_id.partner_id')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", related='iso_reference.contact_person')
    head_office         = fields.Char(string="Jumlah Head Office", related='iso_reference.head_office')
    site_office         = fields.Char(string="Jumlah Site Office", related='iso_reference.site_office')
    off_location        = fields.Char(string="Jumlah Off Location", related='iso_reference.off_location')
    part_time           = fields.Char(string="Jumlah Part Time", related='iso_reference.part_time')
    subcon              = fields.Char(string="Jumlah Sub Contractor", related='iso_reference.subcon')
    unskilled           = fields.Char(string="Jumlah Unskilled", related='iso_reference.unskilled')
    seasonal            = fields.Char(string="Jumlah Seasonal", related='iso_reference.seasonal')
    total_emp           = fields.Integer(string="Total Employee", related='iso_reference.partner_site.total_emp')
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    scope               = fields.Text('Scope', related='iso_reference.scope')
    # boundaries          = fields.Text('Boundaries', related='iso_reference.boundaries')
    telepon             = fields.Char(string="No Telepon", related='iso_reference.telepon')

    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_prog        = fields.Many2many('tsi.ea_code', 'rel_ops_prog_ea_code', string="IAF Code Existing")
    type_client         = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Type Client', tracking=True, related="sales_order_id.tipe_pembayaran")
    apprev_date         = fields.Datetime(string="Review Date", related="sales_order_id.application_review_ids.finish_date")    
    contract_date       = fields.Datetime(string="Contract Date", related="sales_order_id.date_order")    
    contract_number     = fields.Char(string="Contract Number") 

    tgl_sertifikat              = fields.Date('Tanggal Sertifikat')
    tgl_sertifikat_original     = fields.Date('Tanggal Sertifikat Original')
    tgl_sertifikat_update       = fields.Date('Tanggal Sertifikat Terkini')
    tgl_sertifikat_descision    = fields.Date('Tanggal Sertifikat Decision')
    pic_decision                = fields.Char(string='Nama Decision Maker')
    tgl_audit_stage_2           = fields.Date('Tanggal Audit Stage 2')

    pic_auditor_2               = fields.Many2many('hr.employee', string="Nama Auditor")

    tgl_review_stage_1          = fields.Date('Tanggal Review Stage 1')
    pic_reviewer                = fields.Char(string='PIC Reviewer Stage 1')
    
    tgl_audit_stage_1           = fields.Date('Tanggal Audit Stage 1 Awal')
    tgl_audit_stage_1_akhir           = fields.Date('Tanggal Audit Stage 1 Akhir')
    pic_auditor_1               = fields.Char(string='PIC Auditor 1')

    tgl_application_form        = fields.Date('Tanggal Application Form')
    tgl_kontrak                 = fields.Date('Tanggal Kontrak')
    tgl_notifikasi              = fields.Date(string="Date Notification", default=datetime.today(), tracking=True)
    notification_printed = fields.Boolean(string='Notification Printed', default=False)
    upload_dokumen              = fields.Binary('Documen Audit')
    dokumen_sosialisasi        = fields.Binary(string='Organization Chart', related="sales_order_id.dokumen_sosialisasi", store=True)
    file_name1      = fields.Char('Filename')
    state                       = fields.Selection([
                                        ('new',     'New'),
                                        ('confirm', 'Confirm'),
                                        ('done',    'Done'),
                                        ('done_stage2', 'Stage-2'),
                                        ('done_surveillance1', 'Surveillance1'),
                                        ('done_surveillance2', 'Surveillance2'),
                                        ('done_recertification', 'Recertification'),
                                    ], string='Status', readonly=True, copy=False, index=True, default='new')

    program_lines               = fields.One2many('ops.program.program', 'reference_id', string="Reference", index=True, tracking=True)
    program_lines_aktual               = fields.One2many('ops.program.aktual', 'reference_id', string="Reference", index=True, tracking=True)
    show_salesinfo      = fields.Boolean(string='Additional Info', default=False)
    show_14001          = fields.Boolean(string='Show 14001', default=False)
    show_45001          = fields.Boolean(string='Show 45001', default=False) 
    show_27001          = fields.Boolean(string='Show 27001', default=False)
    show_22000           = fields.Boolean(string='Show 22000', default=False) 
    show_haccp          = fields.Boolean(string='Show HACCP', default=False)  

    #ea_code
    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code",)
    ea_code_14001           = fields.Many2one('tsi.ea_code', string="EA Code",)
    ea_code_27001           = fields.Many2one('tsi.ea_code', string="EA Code",)
    ea_code_45001           = fields.Many2one('tsi.ea_code', string="EA Code",)
    food_category_22000     = fields.Many2one('tsi.food_category', string="Food Category",)
    food_category_22000     = fields.Many2one('tsi.food_category', string="Food Category",)

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :
                obj.show_14001 = False
                obj.show_45001 = False
                obj.show_27001 = False
                obj.show_haccp = False
                obj.show_22000 = False               
                obj.show_salesinfo = False
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISO 14001' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_14001 = True
                    if standard.name == 'ISO 45001' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_45001 = True
                    if standard.name == 'ISO 27001' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001 = True
                    if standard.name == 'ISO 22000' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22000 = True
                    if standard.name == 'HACCP' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_haccp = True
                    elif standard.name == 'ISO 9001' :
                        obj.show_salesinfo = True
                    #else :
                    #    obj.show_salesinfo = True


    def set_to_confirm(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'Stage-01'
        stage1_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Stage-01')
        
        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-1'
        surveillance1_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-1')

        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-2'
        surveillance2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-2')

        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-2'
        recertification_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Recertification')

        # Proses untuk Stage-01
        for line in stage1_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan'].create(vals)

        # Proses untuk Survillance-1
        for line in surveillance1_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan'].create(vals)
        
        # Proses untuk Survillance-1
        for line in surveillance2_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan'].create(vals)
        
        # Proses untuk Survillance-1
        for line in recertification_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'confirm'})

        return True
    
    def action_stage2(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'Stage-02'
        stage2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Stage-02')

        # Iterasi setiap line yang memenuhi kriteria stage2
        for line in stage2_lines:
            vals = {
                'auditor_1': line.auditor.id if line.auditor.id else False,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id if line.expert.id else False,
                'audit_method': line.metode if line.metode else False,
                'audit_stage': line.audit_type if line.audit_type else False,
                'audit_start': line.date_start if line.date_start else False,
                'audit_end': line.date_end if line.date_end else False,
                'auditor_lead': line.lead_auditor.id if line.lead_auditor.id else False,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],  # Perlu didefinisikan atau diambil dari suatu tempat
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date'   : self.contract_date,
                'program_id': self.id
                # Copy other fields as needed
            }

            # Buat entri baru di ops.plan dengan nilai-nilai yang sudah dipilih
            self.env['ops.plan'].create(vals)

        # Setelah selesai, ubah state menjadi 'done_stage2'
        self.write({'state': 'done_stage2'})
        return True
    
    def action_surviellance1(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'stage2'
        stage2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-1')

        # Iterasi setiap line yang memenuhi kriteria stage2
        for line in stage2_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],  # Perlu didefinisikan atau diambil dari suatu tempat
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date'   : self.contract_date,
                'program_id': self.id
                # Copy other fields as needed
            }

            # Buat entri baru di ops.plan dengan nilai-nilai yang sudah dipilih
            self.env['ops.plan'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'done_surveillance1'})

        return True
    
    def action_surviellance2(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'stage2'
        stage2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-2')

        # Iterasi setiap line yang memenuhi kriteria stage2
        for line in stage2_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],  # Perlu didefinisikan atau diambil dari suatu tempat
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date'   : self.contract_date,
                'program_id': self.id
                # Copy other fields as needed
            }

            # Buat entri baru di ops.plan dengan nilai-nilai yang sudah dipilih
            self.env['ops.plan'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'done_surveillance2'})

        return True
    
    def action_recertification(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'stage2'
        stage2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Recertification')

        # Iterasi setiap line yang memenuhi kriteria stage2
        for line in stage2_lines:
            vals = {
                'auditor_1': line.auditor.id,
                'auditor_2': line.auditor_2.id,
                'auditor_3': line.auditor_3.id,
                'technical_expert': line.expert.id,
                'audit_method': line.metode,
                'audit_stage': line.audit_type,
                'audit_start': line.date_start,
                'audit_end': line.date_end,
                'auditor_lead': line.lead_auditor.id,
                'iso_reference': self.iso_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],  # Perlu didefinisikan atau diambil dari suatu tempat
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date'   : self.contract_date,
                'program_id': self.id
                # Copy other fields as needed
            }

            # Buat entri baru di ops.plan dengan nilai-nilai yang sudah dipilih
            self.env['ops.plan'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'new'})

        return True


    def set_to_done(self):
        # Periksa setiap record di model ini
        for record in self:
            # Inisialisasi variabel untuk menyimpan status
            audit_stage_value = []
            
            # Iterasi untuk setiap program_lines_aktual yang terkait dengan record ini
            for line in record.program_lines_aktual:
                # Tambahkan 'Stage-01' jika ada pada audit_type
                if 'Stage-01' in line.audit_type:
                    audit_stage_value.append('Stage-01')

                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-1' in line.audit_type:
                    audit_stage_value.append('Survillance-1')
                
                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-2' in line.audit_type:
                    audit_stage_value.append('Survillance-2')
                
                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Recertification' in line.audit_type:
                    audit_stage_value.append('Recertification')

            # Tentukan state berdasarkan nilai audit_type yang ditemukan
            if 'Stage-01' in audit_stage_value:
                record.write({'state': 'done'})  # Jika Stage-01 ditemukan, set state ke 'done'
            if 'Survillance-1' in audit_stage_value:
                record.write({'state': 'done_surveillance1'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'Survillance-2' in audit_stage_value:
                record.write({'state': 'done_surveillance2'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_2'
            if 'Recertification' in audit_stage_value:
                record.write({'state': 'done_recertification'})  # Jika Surveillance-1 ditemukan, set state ke 'recertification'
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True
    
    def set_to_stage1(self):
        self.write({'state': 'done'})            
        return True
    
    def set_to_stage2(self):
        self.write({'state': 'done_stage2'})            
        return True
    
    def set_to_surveillance1(self):
        self.write({'state': 'done_surveillance1'})            
        return True
    
    def set_to_surveillance2(self):
        self.write({'state': 'done_surveillance2'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.program')
        vals['name'] = sequence or _('New')
        result = super(AuditProgram, self).create(vals)
        return result
    
    def audit_notification(self):
        # Code to generate Stage 1 report
        self.write({
            'tgl_notifikasi': fields.Datetime.now(),
            'notification_printed': True,
        })
        return self.env.ref('v15_tsi.audit_notification').report_action(self)

class PartnerCertificate(models.Model):
    _name           = 'ops.program.program'
    _description    = 'certificate'

    reference_id        = fields.Many2one('ops.program', string="Reference")
    audit_type          = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ])
    date_start          = fields.Date(string='Date Start')
    date_end            = fields.Date(string='Date End')
    lead_auditor        = fields.Many2one('hr.employee', string="Lead Auditor")
    auditor             = fields.Many2one('hr.employee', string="Auditor")
    auditor_2             = fields.Many2one('hr.employee', string="Auditor")
    auditor_3             = fields.Many2one('hr.employee', string="Auditor")
    expert              = fields.Many2one('hr.employee', string="Technical Expert")
    remarks             = fields.Text(string='Remarks')
    mandayss            = fields.Char(string="Mandays")
    metode              = fields.Selection(string='Metode Audit', selection=[
                            ('online',   'Online'), 
                            ('onsite',   'Onsite'), 
                            ('hybrid',   'Hybrid'), 
                            ])

class PartnerCertificates(models.Model):
    _name           = 'ops.program.aktual'
    _description    = 'certificate'

    reference_id        = fields.Many2one('ops.program', string="Reference")
    referance_id = fields.Many2one('ops.plan', string="Reference")
    audit_type          = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ])
    date_start          = fields.Date(string='Date Start')
    date_end            = fields.Date(string='Date End')
    lead_auditor        = fields.Many2one('hr.employee', string="Lead Auditor", tracking=True)
    auditor             = fields.Many2one('hr.employee', string="Auditor")
    auditor_2             = fields.Many2one('hr.employee', string="Auditor")
    auditor_3             = fields.Many2one('hr.employee', string="Auditor")
    expert              = fields.Many2one('hr.employee', string="Technical Expert", tracking=True)
    remarks             = fields.Text(string='Remarks')
    mandayss            = fields.Char(string="Mandays")
    metode              = fields.Selection(string='Metode Audit', selection=[
                            ('online',   'Online'), 
                            ('onsite',   'Onsite'), 
                            ('hybrid',   'Hybrid'), 
                            ])
