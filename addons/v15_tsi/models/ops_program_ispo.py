from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime

class AuditProgramISPO(models.Model):
    _name           = 'ops.program.ispo'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Program'
    _order          = 'id DESC'

    name                = fields.Char(string='Document No')
    ispo_reference       = fields.Many2one('tsi.ispo', string="Reference")
# related, ea_code ???
    notification_id = fields.Many2one('audit.notification.ispo', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

    customer            = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", related='ispo_reference.contact_person')
    head_office         = fields.Char(string="Jumlah Head Office", related='ispo_reference.head_office')
    site_office         = fields.Char(string="Jumlah Site Office", related='ispo_reference.site_office')
    off_location        = fields.Char(string="Jumlah Off Location", related='ispo_reference.off_location')
    part_time           = fields.Char(string="Jumlah Part Time", related='ispo_reference.part_time')
    subcon              = fields.Char(string="Jumlah Sub Contractor", related='ispo_reference.subcon')
    unskilled           = fields.Char(string="Jumlah Unskilled", related='ispo_reference.unskilled')
    seasonal            = fields.Char(string="Jumlah Seasonal", related='ispo_reference.seasonal')
    total_emp           = fields.Integer(string="Total Employee", related='ispo_reference.partner_site.total_emp')
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIKk'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True, related='ispo_reference.scope')
    # boundaries          = fields.Text('Boundaries', related='ispo_reference.boundaries')
    telepon             = fields.Char(string="No Telepon", related='ispo_reference.telepon')

    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code")
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
    dokumen_sosialisasi        = fields.Binary('Organization Chart')
    file_name1      = fields.Char('Filename')
    state                       = fields.Selection([
                                        ('new',     'New'),
                                        ('confirm', 'Confirm'),
                                        ('done',    'Stage-1'),
                                        ('done_stage2', 'Stage-2'),
                                        ('done_surveillance1', 'Surveillance1'),
                                        ('done_surveillance2', 'Surveillance2'),
                                        ('done_surveillance3', 'Surveillance3'),
                                        ('done_surveillance4', 'Surveillance4'),
                                        ('done_recertification', 'Recertification'),
                                    ], string='Status', readonly=True, copy=False, index=True, default='new')

    program_lines               = fields.One2many('ops.program.program.ispo', 'reference_id', string="Reference", index=True, tracking=True)
    program_lines_aktual               = fields.One2many('ops.program.aktual.ispo', 'reference_id', string="Reference", index=True, tracking=True)


    def set_to_confirm(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'Stage-01'
        stage1_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Stage-01')
        
        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-1'
        surveillance1_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-1')

        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-2'
        surveillance2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-2')

        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-2'
        surveillance3_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-3')

        # Filter program_lines_aktual yang memiliki audit_type == 'Survillance-2'
        surveillance4_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-4')

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
                'ispo_reference': self.ispo_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan.ispo'].create(vals)

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
                'ispo_reference': self.ispo_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan.ispo'].create(vals)
        
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
                'ispo_reference': self.ispo_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan.ispo'].create(vals)
        
        # Proses untuk Survillance-3
        for line in surveillance3_lines:
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
                'ispo_reference': self.ispo_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan.ispo'].create(vals)
        
        # Proses untuk Survillance-4
        for line in surveillance4_lines:
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
                'ispo_reference': self.ispo_reference.id,
                'sales_order_id': self.sales_order_id.id,
                'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                'notification_id': self.notification_id.id,
                'contract_number': self.contract_number,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'contract_date': self.contract_date,
                'program_id': self.id
            }
            self.env['ops.plan.ispo'].create(vals)

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
                'ispo_reference': self.ispo_reference.id,
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
            self.env['ops.plan.ispo'].create(vals)

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
                'ispo_reference': self.ispo_reference.id,
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
            self.env['ops.plan.ispo'].create(vals)

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
                'ispo_reference': self.ispo_reference.id,
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
            self.env['ops.plan.ispo'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'done_surveillance2'})

        return True
    
    def action_surviellance3(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'stage2'
        stage2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-3')

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
                'ispo_reference': self.ispo_reference.id,
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
            self.env['ops.plan.ispo'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'done_surveillance3'})

        return True
    
    def action_surviellance4(self):
        self.ensure_one()  # Pastikan hanya dipanggil untuk satu record

        # Filter program_lines_aktual yang memiliki audit_type == 'stage2'
        stage2_lines = self.program_lines_aktual.filtered(lambda line: line.audit_type == 'Survillance-4')

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
                'ispo_reference': self.ispo_reference.id,
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
            self.env['ops.plan.ispo'].create(vals)

        # Setelah selesai, ubah state menjadi 'confirm'
        self.write({'state': 'done_surveillance4'})

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
                'ispo_reference': self.ispo_reference.id,
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
            self.env['ops.plan.ispo'].create(vals)

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
                if 'Survillance-3' in line.audit_type:
                    audit_stage_value.append('Survillance-3')
                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-4' in line.audit_type:
                    audit_stage_value.append('Survillance-4')

            # Tentukan state berdasarkan nilai audit_type yang ditemukan
            if 'Stage-01' in audit_stage_value:
                record.write({'state': 'done'})  # Jika Stage-01 ditemukan, set state ke 'done'
            if 'Survillance-1' in audit_stage_value:
                record.write({'state': 'done_surveillance1'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'Survillance-2' in audit_stage_value:
                record.write({'state': 'done_surveillance2'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'Survillance-3' in audit_stage_value:
                record.write({'state': 'done_surveillance3'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'Survillance-4' in audit_stage_value:
                record.write({'state': 'done_surveillance4'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
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
    
    def set_to_surveillance3(self):
        self.write({'state': 'done_surveillance3'})            
        return True
    
    def set_to_surveillance4(self):
        self.write({'state': 'done_surveillance4'})            
        return True
    
    def set_to_recert(self):
        self.write({'state': 'done_recertification'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.program.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditProgramISPO, self).create(vals)
        return result
    
    def audit_notification(self):
        # Code to generate Stage 1 report
        self.write({
            'tgl_notifikasi': fields.Datetime.now(),
            'notification_printed': True,
        })
        return self.env.ref('v15_tsi.audit_notification').report_action(self)

class PartnerCertificate(models.Model):
    _name           = 'ops.program.program.ispo'
    _description    = 'certificate'

    reference_id        = fields.Many2one('ops.program.ispo', string="Reference")
    audit_type          = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Survillance-3',    'Surveilance 3'),
                            ('Survillance-4',    'Surveilance 4'),
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
    _name           = 'ops.program.aktual.ispo'
    _description    = 'certificate'

    reference_id        = fields.Many2one('ops.program.ispo', string="Reference")
    referance_id = fields.Many2one('ops.plan.ispo', string="Reference")
    audit_type          = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Survillance-3',    'Surveilance 3'),
                            ('Survillance-4',    'Surveilance 4'),
                            ('Survillance-5',    'Surveilance 5'),
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
