from odoo import models, fields, api
from odoo import http
import requests
import json
from datetime import datetime, timedelta
import io  
from odoo.tools.translate import _ 
import logging
from docx import Document
from io import BytesIO
import base64
import logging
import re
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit        = "res.partner"

    is_associate        = fields.Boolean('Is Associate' )
    associate_id        = fields.Many2one('res.partner', "Associate Name", domain = [('is_company','=',False)])
    is_franchise        = fields.Boolean('Is Frenchise' )
    franchise_id        = fields.Many2one('res.partner', "Frenchise Name", domain = [('is_company','=',True)])
    code                = fields.Char('Code' )
    jabatan         = fields.Char(string="Position", tracking=True)
    associate_lines     = fields.One2many('tsi.associate_partner', 'partner_id', "Associate")
    site_lines          = fields.One2many('tsi.site_partner', 'partner_id', "Sites")
    feedback_lines      = fields.One2many('tsi.partner_feedback', 'partner_id', "Feedback")
    scope           = fields.Char('Scope') 
    boundaries  = fields.Char(string="Boundaries") 
    number_site     = fields.Char('Number of Site') 
    total_emp       = fields.Char('Total Employee') 
    mandays         = fields.Char('Mandays') 
    tgl_sertifikat  = fields.Date(string='Tanggal Sertifikat')
    harga           = fields.Integer(string='Harga')
    tahun_masuk     = fields.Char('Tahun Masuk')
    invoice_address = fields.Char('Invoice Address')
    office_address  = fields.Char('Office Address')
    contact_person  = fields.Char('Contact Person')
    nomor_customer = fields.Char(string='Customer ID',  copy=False)
    food_category   = fields.Many2one('tsi.food_category', string="Food Category")
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Kategori', index=True)

    certification_lines = fields.One2many('tsi.partner.certificate', 'partner_id', string="Certification", index=True)
    tahun_masuk_lines = fields.One2many('tsi.tahun_masuk', 'partner_id', string="Tahun Masuk", index=True)
    state = fields.Selection([
    ('belum_valid', 'Belum Valid'),
    ('sudah_valid', 'Sudah Valid'),
    ], string='State', default='belum_valid')
    ea_code_ids = fields.Many2many('tsi.ea_code', string="EA Codes")
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string="Standard", compute='_compute_iso_standard_ids', store=True)
    state_2 = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='Status Certificate Klien', default='New', compute='_compute_certification_status', store=True)

    access_token = fields.Char('Access Token')
    
    show_internal_notes = fields.Boolean(compute='_compute_show_internal_notes', store=True)

    status_klien = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='State', compute='_compute_status_klien', inverse='_inverse_status_klien', store=True)

    @api.constrains('name')
    def _check_company_name_format(self):
        for record in self:
            # Validasi hanya untuk perusahaan (is_company = True)
            if not record.is_company:
                continue

            customer_name = record.name or ""

            # 1. Validasi nama harus diawali dengan "PT " atau "CV " tanpa titik setelahnya
            if customer_name.startswith("PT "):
                # Pastikan tidak ada titik setelah PT
                if "." in customer_name[3:]:
                    raise ValidationError("Nama perusahaan dengan awalan 'PT' tidak boleh mengandung titik setelah 'PT'.")
                # Pastikan nama setelah "PT " dimulai dengan huruf kapital
                if not customer_name[3:][0].isupper():
                    raise ValidationError("Nama setelah 'PT' harus dimulai dengan huruf kapital.")
            elif customer_name.startswith("CV "):
                # Pastikan tidak ada titik setelah CV
                if "." in customer_name[3:]:
                    raise ValidationError("Nama perusahaan dengan awalan 'CV' tidak boleh mengandung titik setelah 'CV'.")
                # Pastikan nama setelah "CV " dimulai dengan huruf kapital
                if not customer_name[3:][0].isupper():
                    raise ValidationError("Nama setelah 'CV' harus dimulai dengan huruf kapital.")
            else:
                # 2. Nama perusahaan selain PT/CV harus mengikuti format kapitalisasi
                # Cek apakah semua huruf tidak kapital
                if customer_name.isupper():
                    raise ValidationError("Nama perusahaan tidak boleh seluruhnya huruf kapital.")
                
                # 3. Pastikan setiap kata dimulai dengan huruf kapital
                name_parts = customer_name.split(" ")
                for part in name_parts:
                    if part and not part[0].isupper():
                        raise ValidationError("Setiap kata dalam nama perusahaan harus dimulai dengan huruf kapital.")
            
            # 4. Validasi agar tidak ada format PT., CV., pt., atau cv.
            if re.search(r'\b(pt\.|cv\.)\b', customer_name, re.IGNORECASE):
                raise ValidationError("Nama perusahaan tidak boleh mengandung format yang salah seperti 'PT.' atau 'CV.'.")

    @api.depends('tahun_masuk_lines.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for partner in self:
            # Mengumpulkan semua iso_standard_ids dari tahun_masuk_lines
            all_iso_ids = set()
            for line in partner.tahun_masuk_lines:
                all_iso_ids.update(line.iso_standard_ids.ids)

            # Set iso_standard_ids pada partner
            partner.iso_standard_ids = [(6, 0, list(all_iso_ids))]

    @api.depends('certification_lines.expiry_date', 'certification_lines.validity_date')
    def _compute_certification_status(self):
        today = datetime.today().date()
        
        for partner in self:
            state_set = False
            for cert in partner.certification_lines:
                if cert.expiry_date:
                    if cert.expiry_date + timedelta(days=1) < today <= cert.expiry_date + timedelta(weeks=26):
                        partner.state_2 = 'suspend'
                        state_set = True
                    elif today > cert.expiry_date + timedelta(weeks=26):
                        partner.state_2 = 'withdraw'
                        state_set = True

                if cert.validity_date and today > cert.validity_date + timedelta(days=1):
                    partner.state_2 = 'withdraw'
                    state_set = True
                
                if not state_set:
                    partner.state_2 = 'New'

    @api.depends('state_2')
    def _compute_status_klien(self):
        """Ambil data otomatis dari state_2."""
        for record in self:
            if record.state_2:
                record.status_klien = record.state_2

    def _inverse_status_klien(self):
        """Sinkronisasi otomatis dari status_klien ke state_2."""
        for record in self:
            if record.status_klien:
                record.state_2 = record.status_klien
    
    @api.depends('is_company', 'contact_client')
    def _compute_show_internal_notes(self):
        for record in self:
            record.show_internal_notes = record.is_company and record.contact_client

    
    def action_valid_partner(self):
        self.write({'state': 'sudah_valid'})
        # Tambahkan logika lainnya sesuai kebutuhan, misalnya update field lain atau panggil fungsi lain
        return True
    
    def action_lanjut_partner(self):
        self.write({'state': 'lanjut'})
        # Tambahkan logika lainnya sesuai kebutuhan, misalnya update field lain atau panggil fungsi lain
        return True
    
    def action_lost_partner(self):
        self.write({'state': 'lost'})
        # Tambahkan logika lainnya sesuai kebutuhan, misalnya update field lain atau panggil fungsi lain
        return True
    
    def action_suspen_partner(self):
        self.write({'state': 'suspen'})
        # Tambahkan logika lainnya sesuai kebutuhan, misalnya update field lain atau panggil fungsi lain
        return True

    def action_send_whatsapp(self):
        url = 'https://service-chat.qontak.com/api/open/v1/broadcasts/whatsapp/direct'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer qtYy2OOAf852_AzHb_sEbcmXYzI6jOvXG0lp3S804F0'
        }
        payload = {
            'to_name': self.name,
            'to_number': self.mobile,
            'message_template_id': 'b8c2fb14-ceea-4eab-ba4f-bd240b1e5ad9',
            'channel_integration_id': 'dc259486-869a-4b6c-9c65-2d27462a24c2',
            'language': {'code': 'id'},
            'parameters': {'body': [{'key': '1', 'value_text': self.name, 'value': 'customer_name'}]}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return True
        else:
            return False

    def get_iso_review(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Audit',
                'view_mode': 'tree,form',
                'res_model': 'audit.notification',
                'domain': [('customer', '=', self.id)],
                'context': "{'create': False}"
            }

    def get_feedback(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Feedback',
                'view_mode': 'tree,form',
                'res_model': 'tsi.partner_feedback',
                'domain': [('partner_id', '=', self.id)],
                'context': {'default_partner_id': self.id }

            }

class PartnerCertificate(models.Model):
    _name           = 'tsi.partner.certificate'
    _description    = 'certificate'

    partner_id          = fields.Many2one('res.partner', string="Reference")
    sertifikat_reference = fields.Many2one('ops.sertifikat', string="Document No")
    no_sertifikat        = fields.Char('Nomor Sertifikat')
    tahapan_audit   = fields.Selection([
                            ('initial audit',         'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),
                            ('Recertification', 'Recertification'),
                        ], string='Tahapan Audit')    
    scope           = fields.Char('Scope', related="partner_id.scope", readonly=False)
    boundaries           = fields.Char('Boundaries', related="partner_id.boundaries", readonly=False)
    initial_date = fields.Date(string='Initial Certification Date',store=True)
    issue_date = fields.Date(string='Certification Issue Date', store=True)
    validity_date = fields.Date(string='Certification Validity Date', store=True)
    expiry_date = fields.Date(string='Certification Expiry Date', store=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('suspend', 'Suspended'),
        ('withdraw', 'Withdrawn'),
    ], string='State', default='active')

    @api.onchange('initial_date')
    def _onchange_initial_date(self):
        for record in self:
            if record.initial_date:
                # Set issue_date to initial_date
                record.issue_date = record.initial_date
                
                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initial_date, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validity_date = validity_datetime.date()
                
                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=(365-1))
                record.expiry_date = expiry_datetime.date()

    @api.model
    def _check_certificates(self):
        today = datetime.today().date()
        partners = self.env['res.partner'].search([])

        for partner in partners:
            state_set = False
            for cert in partner.certification_lines:
                if cert.expiry_date:
                    if cert.expiry_date + timedelta(days=1) < today <= cert.expiry_date + timedelta(weeks=26):
                        partner.state_2 = 'suspend'
                        state_set = True
                    elif today > cert.expiry_date + timedelta(weeks=26):
                        partner.state_2 = 'withdraw'
                        state_set = True
                
                if cert.validity_date and today > cert.validity_date + timedelta(days=1):
                    partner.state_2 = 'withdraw'
                    state_set = True
                
                if not state_set:
                    partner.state_2 = 'New'


class PartnerTahunMasuk(models.Model):
    _name           = 'tsi.tahun_masuk'
    _description    = 'Tahun Masuk'

    partner_id = fields.Many2one('res.partner', "Partner")
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards',)
    sertifikat_reference = fields.Many2one('ops.sertifikat', string="Document No")
    issue_date = fields.Date(string='Certification Issue Date', store=True,)
    certification_year = fields.Char(string="Certification Year")

    @api.onchange('iso_standard_ids')
    def _onchange_iso_standard_ids(self):
        # Ketika iso_standard_ids di tahun_masuk_lines berubah
        if self.partner_id:
            # Update iso_standard_ids di res.partner
            self.partner_id.iso_standard_ids = self.iso_standard_ids

    # @api.depends('issue_date')
    # def _compute_certification_year(self):
    #     for record in self:
    #         if record.issue_date:
    #             record.certification_year = str(record.issue_date.year)
    #         else:
    #             record.certification_year = ''

# class IrCronCertificate(models.Model):
#     _inherit = 'ir.cron'

#     interval_type = fields.Selection([
#         ('minutes', 'Minutes'),
#         ('hours', 'Hours'),
#         ('days', 'Days'),
#         ('weeks', 'Weeks'),
#         ('months', 'Months'),
#         ('seconds', 'Seconds')  # Tambahkan opsi detik
#     ], required=True, default='minutes')

#     @api.model
#     def _process_job(self, job_id):
#         job = self.browse(job_id)
#         now = datetime.now()
#         if job.interval_type == 'seconds':
#             nextcall = now + timedelta(seconds=job.interval_number)
#         else:
#             nextcall = super(IrCronCertificate, self)._process_job(job_id)
        
#         job.write({'nextcall': nextcall})
#         return super(IrCronCertificate, self)._process_job(job_id)


    

class AssociatePartner(models.Model):
    _name           = 'tsi.associate_partner'
    _description    = 'Associate Partner'
    _rec_name       = 'associate_id'

    partner_id      = fields.Many2one('res.partner', "Partner")
    associate_id    = fields.Many2one('res.partner', "Associate")
    associate_code  = fields.Char('Associate Code', related='associate_id.code')
    keterangan      = fields.Char('Keterangan') 
    

class SitePartner(models.Model):
    _name           = 'tsi.site_partner'
    _description    = 'Site Partner'
    _rec_name       = 'jenis'

    partner_id      = fields.Many2one('res.partner', "Partner")
    jenis           = fields.Char('Jenis') 
    alamat          = fields.Char('Alamat') 
    telp            = fields.Char('Telp') 
    jumlah_karyawan = fields.Integer(string='Jumlah Karyawan')

class PartnerFeedback(models.Model):
    _name           = 'tsi.partner_feedback'
    _description    = 'Partner Feedback'

    name            = fields.Char(string='Document No', required=True, readonly=True, default='New')
    nama_pic        = fields.Many2one('res.partner', "Nama PIC", domain=[('is_company','=', False)], tracking=True)
    nama_perusahaan = fields.Many2one('res.partner', "Nama Perusahaan", domain=[('is_company','=', True)], tracking=True)
    email           = fields.Char(string='Email', tracking=True)
    telepon         = fields.Char(string='Telepon', tracking=True)
    tgl_keluhan     = fields.Date(string='Tanggal Keluhan',default=fields.Date.context_today, tracking=True)
    media_keluhan   = fields.Selection([
                        ('pertemuan_offline','Pertertemuan Offline'),
                        ('pertemuan_offline','Pertertemuan Offline'),
                        ],string='Media Keluhan', index=True, tracking=True)
    jabatan         = fields.Char(string='Jabatan', tracking=True)
    alamat          = fields.Char(string='Alamat', tracking=True)
    standar         = fields.Many2many('tsi.iso.standard',string='Standar', tracking=True)
    tahap_audit     = fields.Many2many('tsi.iso.tahapan',string='Tahap Audit', tracking=True)
    tgl_selesai     = fields.Date(string='Tanggal Selesai', tracking=True)
    diterima_oleh   = fields.Char(string='Diterima Oleh', tracking=True)
    deskripsi       = fields.Char(string='Deskripsi', tracking=True)
    partner_id      = fields.Many2one('res.partner', "Partner")
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('seq.partner_feedback') or '/'
            current_month = fields.Date.today().month
            roman_month = self._int_to_roman(current_month)
            year = fields.Date.today().strftime('%Y')
            vals['name'] = f'{sequence}/TSI/{roman_month}/{year}'
    
        return super(PartnerFeedback, self).create(vals)

    @staticmethod
    def _int_to_roman(month):
        roman_numerals = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
            7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
        }
        return roman_numerals.get(month, "I")
    
    def action_send_mail(self):
        self.ensure_one()
        _logger.info("Email from object: %s", self.email)

        template_id = self.env.ref('v15_tsi.email_template_tsi_partner_feedback').id
        template = self.env['mail.template'].browse(template_id)

        report = self.env.ref('v15_tsi.report_feedbanck_customer')
        
        docx_content = report.export_doc_by_template(
            file_template_data=report.file_template_data, 
            file_name_export='Report Keluhan Pelanggan',  
            datas=self
        )

        attachment = self.env['ir.attachment'].create({
            'name': 'Report Keluhan Pelanggan.docx',
            'type': 'binary',
            'datas': base64.b64encode(docx_content),
            'res_model': 'tsi.partner_feedback',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        })

        ctx = {
            'default_model': 'tsi.partner_feedback',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_attachment_ids': [(6, 0, [attachment.id])],
            'default_email_to': 'bandung01.emailkerja.id',
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class TSICRMAccreditation(models.Model):
    _name           = 'tsi.crm_accreditation'
    _description    = 'CRM Accreditation'

    reference_id    = fields.Many2one('tsi.crm', "reference")
    loss_id         = fields.Many2one('tsi.crm.loss', "Reference Loss")
    lanjut_id         = fields.Many2one('tsi.crm.lanjut', "Reference Lanjut")
    suspend_id         = fields.Many2one('tsi.crm.suspen', "Reference Suspend")
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    accreditation   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    tahapan_audit   = fields.Selection([
                            ('initial audit',  'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),
                            ('Recertification', 'Recertification'),
                        ], string='Tahapan Audit')
    nilai_ia        = fields.Integer('Nilai') 
    level           = fields.Char('Level') 
    nomor           = fields.Char('Nomor') 
    tanggal         = fields.Char('Tanggal')
    
     

class TSICRM(models.Model):
    _name           = 'tsi.crm'
    _description    = 'TSI CRM'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    partner_id      = fields.Many2one('res.partner', "Partner")
    contract_number = fields.Char('Contract Number')
    contract_date   = fields.Date(string='Tanggal Kontrak')
    tahapan_audit   = fields.Selection([
                            ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Recertification', 'Recertification'),
                        ], string='Tahapan Audit')
    accreditation         = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    nilai_ia        = fields.Char('Nilai Kontrak')   
    level           = fields.Char('Level')
    segment         = fields.Many2many('res.partner.category', string='Segment')

    nilai_ia        = fields.Char('Initial Audit')
    nilai_sv1       = fields.Char('Surveilance 1')
    nilai_sv2       = fields.Char('Surveilance 2')
    nilai_recert    = fields.Char('Recertification')
    sales      = fields.Many2one('res.users', string='Sales Person')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True)
    template_kontrak        = fields.Binary('Upload Kontrak', tracking=True)
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', related='iso_reference.doctype', readonly=True, index=True)
    state           =fields.Selection([
                            ('draft',         'Draft'),
                            ('lanjut',         'Lanjut'),
                            ('reject',         'Reject'),
                            ('approve',         'Approve'),
                            ('lost',      'Lost'),
                            ('suspend',  'Suspend'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    # crm_accreditation       = fields.One2many('tsi.crm_accreditation', 'reference_id', string="Accreditation Lines", index=True)

    def generate_sales_order(self):
        self.env['sale.order'].create({
            'partner_id'        : self.partner_id.id,
            'iso_reference'     : self.iso_reference.id,
            'doctype'           : self.doctype
        })
        return True

    def set_to_lanjut(self):
        self.write({'state': 'lanjut'})  
        self._create_lanjut_record()          
        return True

    def set_to_lost(self):
        self.write({'state': 'lost'})
        self._create_loss_record()            
        return True

    def set_to_suspend(self):
        self.write({'state': 'suspend'})
        self._create_suspend_record()            
        return True

    def create_audit(self):
        return {
            'name': "Create Audit",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_view').id,
            'target': 'new'
        }
    
    def _create_lanjut_record(self):
        for record in self:
            crm_accreditations = record.crm_accreditation  # Get all crm_accreditation records related to record

            # Jika Anda ingin mengambil nilai dari satu catatan tertentu, misalnya yang pertama:
            if crm_accreditations:
                first_accreditation = crm_accreditations[0]
                self.env['tsi.crm.lanjut'].create({
                    'partner_id': record.partner_id.id,
                    'contract_number': record.contract_number,
                    'contract_date': record.contract_date,
                    'segment': [(6, 0, record.segment.ids)],
                    'tahapan_audit': first_accreditation.tahapan_audit,
                    'iso_standard_ids': [(6, 0, first_accreditation.iso_standard_ids.ids)],
                    'nilai': first_accreditation.nilai_ia,
                    # 'accreditation': first_accreditation.accreditation.id,
                })

    def _create_loss_record(self):
        for record in self:
            self.env['tsi.crm.loss'].create({
                'partner_id': record.partner_id.id,
                'contract_number': record.contract_number,
                'contract_date': record.contract_date,
                'segment': [(6, 0, record.segment.ids)],
                'tahapan_audit': record.crm_accreditation.mapped('tahapan_audit')[0] if record.crm_accreditation.mapped('tahapan_audit') else False,
                'iso_standard_ids': [(6, 0, record.crm_accreditation.mapped('iso_standard_ids.id'))],
                'nilai': record.crm_accreditation.nilai_ia
                # 'accreditation': record.crm_accreditation.mapped('accreditation.id')[0] if record.crm_accreditation.mapped('accreditation.id') else False,
            })

    def _create_suspend_record(self):
        for record in self:
            self.env['tsi.crm.suspen'].create({
                'partner_id': record.partner_id.id,
                'contract_number': record.contract_number,
                'contract_date': record.contract_date,
                'segment': [(6, 0, record.segment.ids)],
                'tahapan_audit': record.crm_accreditation.mapped('tahapan_audit')[0] if record.crm_accreditation.mapped('tahapan_audit') else False,
                'iso_standard_ids': [(6, 0, record.crm_accreditation.mapped('iso_standard_ids.id'))],
                'nilai': record.crm_accreditation.nilai_ia
                # 'accreditation': record.crm_accreditation.mapped('accreditation.id')[0] if record.crm_accreditation.mapped('accreditation.id') else False,
            })


class TSICRMLanjut(models.Model):
    _name           = 'tsi.crm.lanjut'
    _description    = 'Customer Lanjut'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'


    partner_id      = fields.Many2one('res.partner', "Partner")
    contract_number = fields.Char('Contract Number')
    contract_date   = fields.Date(string='Tanggal Kontrak')
    sales      = fields.Many2one('res.users', string='Sales Person')
    level           = fields.Char(string='Level', readonly=True)
    accreditation       = fields.Many2one('tsi.iso.accreditation', string='Accreditation', compute='_compute_accreditation', store=True)
    segment         = fields.Many2many('res.partner.category', string='Segment')
    tahapan_audit   = fields.Selection([
                                ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Recertification', 'Recertification'),
                            ], string='Tahapan Audit')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', compute='_compute_iso_standard_ids', store=True)
    nilai_initial_audit = fields.Integer(string='Initial Audit', compute='_compute_nilai_initial_audit', store=True)
    nilai_s1 = fields.Integer(string='Surveillance 1', compute='_compute_nilai_s1', store=True)
    nilai_s2 = fields.Integer(string='Surveillance 2', compute='_compute_nilai_s2', store=True)
    nilai_s3 = fields.Integer(string='Surveillance 3', compute='_compute_nilai_s3', store=True)
    nilai_s4 = fields.Integer(string='Surveillance 4', compute='_compute_nilai_s4', store=True)
    nilai_recertification = fields.Integer(string='Recertification', compute='_compute_nilai_recertification', store=True)
    crm_accreditations  = fields.One2many('tsi.crm_accreditation', 'lanjut_id', string="Accreditation Lines", index=True)
    # ISO 9001
    price_baru_9001      = fields.Float(string='Latest Price ISO 9001')
    price_lama_9001      = fields.Float(string='Oldest Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Latest Price ISO 14001')
    price_lama_14001      = fields.Float(string='Oldest Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Latest Price ISO 22000')
    price_lama_22000      = fields.Float(string='Oldest Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Latest Price ISO 27001')
    price_lama_27001      = fields.Float(string='Oldest Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Latest Price ISO 45001')
    price_lama_45001      = fields.Float(string='Oldest Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Latest Price ISO 37001')
    price_lama_37001      = fields.Float(string='Oldest Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 21001
    price_baru_21001      = fields.Float(string='Latest Price ISO 21001')
    price_lama_21001      = fields.Float(string='Oldest Price ISO 21001')
    up_value_21001        = fields.Float(string='Up Value ISO 21001')
    loss_value_21001      = fields.Float(string='Loss Value ISO 21001')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Latest Price ISO 13485')
    price_lama_13485      = fields.Float(string='Oldest Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Latest Price ISO 9994')
    price_lama_9994      = fields.Float(string='Oldest Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Latest Price ISPO')
    price_lama_ispo      = fields.Float(string='Oldest Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')


    @api.depends('crm_accreditations.accreditation')
    def _compute_accreditation(self):
        for record in self:

            all_accreditations = record.crm_accreditations.mapped('accreditation')
            
            if all_accreditations:
                
                record.accreditation = all_accreditations[0]
            else:
                record.accreditation = False

    @api.depends('crm_accreditations.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for record in self:
            # Mengumpulkan semua ISO standard IDs dari baris crm_accreditations
            iso_standard_ids = record.crm_accreditations.mapped('iso_standard_ids')
            # Hanya ambil ID (integer) dari daftar ISO standards
            all_iso_standard_ids = set(iso_standard_ids.mapped('id'))
            record.iso_standard_ids = [(6, 0, list(all_iso_standard_ids))]
    
    @api.depends('crm_accreditations')
    def _compute_nilai_initial_audit(self):
        for record in self:
            record.nilai_initial_audit = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'initial audit').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s1(self):
        for record in self:
            record.nilai_s1 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s2(self):
        for record in self:
            record.nilai_s2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s3(self):
        for record in self:
            record.nilai_s3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 3').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s4(self):
        for record in self:
            record.nilai_s4 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 4').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification(self):
        for record in self:
            record.nilai_recertification = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification').mapped('nilai_ia')
            ) or False

class TSICRMLoss(models.Model):
    _name           = 'tsi.crm.loss'
    _description    = 'Customer Lanjut'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'


    partner_id      = fields.Many2one('res.partner', "Partner")
    contract_number = fields.Char('Contract Number')
    contract_date   = fields.Date(string='Tanggal Kontrak')
    sales      = fields.Many2one('res.users', string='Sales Person')
    level           = fields.Char(string='Level', readonly=True)
    accreditation       = fields.Many2one('tsi.iso.accreditation', string='Accreditation', compute='_compute_accreditation', store=True)
    segment         = fields.Many2many('res.partner.category', string='Segment')
    tahapan_audit   = fields.Selection([
                                ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Recertification', 'Recertification'),
                            ], string='Tahapan Audit')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', compute='_compute_iso_standard_ids', store=True)
    nilai_initial_audit = fields.Integer(string='Initial Audit', compute='_compute_nilai_initial_audit', store=True)
    nilai_s1 = fields.Integer(string='Surveillance 1', compute='_compute_nilai_s1', store=True)
    nilai_s2 = fields.Integer(string='Surveillance 2', compute='_compute_nilai_s2', store=True)
    nilai_s3 = fields.Integer(string='Surveillance 3', compute='_compute_nilai_s3', store=True)
    nilai_s4 = fields.Integer(string='Surveillance 4', compute='_compute_nilai_s4', store=True)
    nilai_recertification = fields.Integer(string='Recertification', compute='_compute_nilai_recertification', store=True)
    crm_accreditations  = fields.One2many('tsi.crm_accreditation', 'loss_id', string="Accreditation Lines", index=True)
    # ISO 9001
    price_baru_9001      = fields.Float(string='Latest Price ISO 9001')
    price_lama_9001      = fields.Float(string='Oldest Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Latest Price ISO 14001')
    price_lama_14001      = fields.Float(string='Oldest Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Latest Price ISO 22000')
    price_lama_22000      = fields.Float(string='Oldest Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Latest Price ISO 27001')
    price_lama_27001      = fields.Float(string='Oldest Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Latest Price ISO 45001')
    price_lama_45001      = fields.Float(string='Oldest Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Latest Price ISO 37001')
    price_lama_37001      = fields.Float(string='Oldest Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 21001
    price_baru_21001      = fields.Float(string='Latest Price ISO 21001')
    price_lama_21001      = fields.Float(string='Oldest Price ISO 21001')
    up_value_21001        = fields.Float(string='Up Value ISO 21001')
    loss_value_21001      = fields.Float(string='Loss Value ISO 21001')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Latest Price ISO 13485')
    price_lama_13485      = fields.Float(string='Oldest Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Latest Price ISO 9994')
    price_lama_9994      = fields.Float(string='Oldest Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Latest Price ISPO')
    price_lama_ispo      = fields.Float(string='Oldest Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')

    @api.depends('crm_accreditations.accreditation')
    def _compute_accreditation(self):
        for record in self:

            all_accreditations = record.crm_accreditations.mapped('accreditation')
            
            if all_accreditations:
                
                record.accreditation = all_accreditations[0]
            else:
                record.accreditation = False

    @api.depends('crm_accreditations.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for record in self:
            # Mengumpulkan semua ISO standard IDs dari baris crm_accreditations
            iso_standard_ids = record.crm_accreditations.mapped('iso_standard_ids')
            # Hanya ambil ID (integer) dari daftar ISO standards
            all_iso_standard_ids = set(iso_standard_ids.mapped('id'))
            record.iso_standard_ids = [(6, 0, list(all_iso_standard_ids))]
    
    @api.depends('crm_accreditations')
    def _compute_nilai_initial_audit(self):
        for record in self:
            record.nilai_initial_audit = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'initial audit').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s1(self):
        for record in self:
            record.nilai_s1 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s2(self):
        for record in self:
            record.nilai_s2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s3(self):
        for record in self:
            record.nilai_s3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 3').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s4(self):
        for record in self:
            record.nilai_s4 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 4').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification(self):
        for record in self:
            record.nilai_recertification = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification').mapped('nilai_ia')
            ) or False

class TSICRMSuspen(models.Model):
    _name           = 'tsi.crm.suspen'
    _description    = 'Customer Suspen'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'


    partner_id      = fields.Many2one('res.partner', "Partner")
    contract_number = fields.Char('Contract Number')
    contract_date   = fields.Date(string='Tanggal Kontrak')
    sales      = fields.Many2one('res.users', string='Sales Person')
    level           = fields.Char(string='Level', readonly=True)
    accreditation       = fields.Many2one('tsi.iso.accreditation', string='Accreditation', compute='_compute_accreditation', store=True)
    segment         = fields.Many2many('res.partner.category', string='Segment')
    tahapan_audit   = fields.Selection([
                                ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Recertification', 'Recertification'),
                            ], string='Tahapan Audit')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', compute='_compute_iso_standard_ids', store=True)
    nilai_initial_audit = fields.Integer(string='Initial Audit', compute='_compute_nilai_initial_audit', store=True)
    nilai_s1 = fields.Integer(string='Surveillance 1', compute='_compute_nilai_s1', store=True)
    nilai_s2 = fields.Integer(string='Surveillance 2', compute='_compute_nilai_s2', store=True)
    nilai_s3 = fields.Integer(string='Surveillance 3', compute='_compute_nilai_s3', store=True)
    nilai_s4 = fields.Integer(string='Surveillance 4', compute='_compute_nilai_s4', store=True)
    nilai_recertification = fields.Integer(string='Recertification', compute='_compute_nilai_recertification', store=True)
    crm_accreditations  = fields.One2many('tsi.crm_accreditation', 'suspend_id', string="Accreditation Lines", index=True)
    # ISO 9001
    price_baru_9001      = fields.Float(string='Latest Price ISO 9001')
    price_lama_9001      = fields.Float(string='Oldest Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Latest Price ISO 14001')
    price_lama_14001      = fields.Float(string='Oldest Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Latest Price ISO 22000')
    price_lama_22000      = fields.Float(string='Oldest Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Latest Price ISO 27001')
    price_lama_27001      = fields.Float(string='Oldest Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Latest Price ISO 45001')
    price_lama_45001      = fields.Float(string='Oldest Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Latest Price ISO 37001')
    price_lama_37001      = fields.Float(string='Oldest Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 21001
    price_baru_21001      = fields.Float(string='Latest Price ISO 21001')
    price_lama_21001      = fields.Float(string='Oldest Price ISO 21001')
    up_value_21001        = fields.Float(string='Up Value ISO 21001')
    loss_value_21001      = fields.Float(string='Loss Value ISO 21001')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Latest Price ISO 13485')
    price_lama_13485      = fields.Float(string='Oldest Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Latest Price ISO 9994')
    price_lama_9994      = fields.Float(string='Oldest Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Latest Price ISPO')
    price_lama_ispo      = fields.Float(string='Oldest Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')

    def create_lanjut(self):
        
        new_lanjut_record = self.env['tsi.crm.lanjut'].create({
            'partner_id': self.partner_id.id,
            'contract_number': self.contract_number,
            'contract_date': self.contract_date,
            'sales': self.sales.id,
            'level': self.level,
            'segment': [(6, 0, self.segment.ids)],
            'tahapan_audit': self.tahapan_audit,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'accreditation': self.accreditation.id,
        })

        suspen_accreditations = self.env['tsi.crm_accreditation'].search([('suspend_id', '=', self.id)])

        for standard in self.iso_standard_ids:
            suspen_accreditation = suspen_accreditations.filtered(lambda a: standard in a.iso_standard_ids)

            if suspen_accreditation:
                for suspen_acc in suspen_accreditation:

                    if suspen_acc.tahapan_audit == 'Initial Audit' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Initial Audit',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 1' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 1',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 2' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 2',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 3' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 3',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 4' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 4',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

    def create_loss(self):
        
        new_loss_record = self.env['tsi.crm.loss'].create({
            'partner_id': self.partner_id.id,
            'contract_number': self.contract_number,
            'contract_date': self.contract_date,
            'sales': self.sales.id,
            'level': self.level,
            'segment': [(6, 0, self.segment.ids)],
            'tahapan_audit': self.tahapan_audit,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'accreditation': self.accreditation.id,
        })

        suspen_accreditations = self.env['tsi.crm_accreditation'].search([('suspend_id', '=', self.id)])

        for standard in self.iso_standard_ids:

            suspen_accreditation = suspen_accreditations.filtered(lambda a: standard in a.iso_standard_ids)

            if suspen_accreditation:
                for suspen_acc in suspen_accreditation:
                    
                    if suspen_acc.tahapan_audit == 'Initial Audit' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Initial Audit',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 1' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 1',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 2' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 2',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 3' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 3',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 4' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 4',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })


    @api.depends('crm_accreditations.accreditation')
    def _compute_accreditation(self):
        for record in self:
            all_accreditations = record.crm_accreditations.mapped('accreditation')                
            if all_accreditations:                    
                record.accreditation = all_accreditations[0]
            else:
                record.accreditation = False

    @api.depends('crm_accreditations.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for record in self:
            # Mengumpulkan semua ISO standard IDs dari baris crm_accreditations
            iso_standard_ids = record.crm_accreditations.mapped('iso_standard_ids')
            # Hanya ambil ID (integer) dari daftar ISO standards
            all_iso_standard_ids = set(iso_standard_ids.mapped('id'))
            record.iso_standard_ids = [(6, 0, list(all_iso_standard_ids))]
    
    @api.depends('crm_accreditations')
    def _compute_nilai_initial_audit(self):
        for record in self:
            record.nilai_initial_audit = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'initial audit').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s1(self):
        for record in self:
            record.nilai_s1 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s2(self):
        for record in self:
            record.nilai_s2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s3(self):
        for record in self:
            record.nilai_s3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 3').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s4(self):
        for record in self:
            record.nilai_s4 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 4').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification(self):
        for record in self:
            record.nilai_recertification = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification').mapped('nilai_ia')
            ) or False