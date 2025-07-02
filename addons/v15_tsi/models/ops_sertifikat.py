from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime, timedelta
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError
import qrcode
from PIL import Image
from io import BytesIO
import base64

class AuditSertifikat(models.Model):
    _name           = 'ops.sertifikat'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Sertifikat'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    iso_reference   = fields.Many2one('tsi.iso', string="Reference")    
    criteria        = fields.Char(string='Criteria')
    objectives      = fields.Text(string='Objectives')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    
    notification_id = fields.Many2one('audit.notification', string="Notification")    
    tanggal_terbit  = fields.Date("Terbit Sertifikat")
    upload_sertifikat   = fields.Binary('Upload Sertifikat')
    nomor_sertifikat    = fields.Char('Nomor Sertifikat')
    sertifikat_summary  = fields.One2many('ops.sertifikat_summary', 'sertifikat_id', string="Plan", index=True)
    sertifikat_kan  = fields.One2many('ops.sertifikat_kan', 'sertifikat_id', string="KAN", index=True)
    sertifikat_non  = fields.One2many('ops.sertifikat_non', 'sertifikat_id', string="Non KAN", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')
    nama_customer       = fields.Many2one('res.partner', string="Organization",related='sales_order_id.partner_id', tracking=True, store=True)
    address             = fields.Char(string="Address", related='iso_reference.office_address')
    scope               = fields.Text('Scope', related='iso_reference.scope')
    accreditation       = fields.Selection([
                            ('KAN',     'KAN'),
                            ('Non KAN', 'Non KAN'),
                        ], string='Accreditaion')
    akre_tes = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    review_summary_id = fields.Many2one('ops.review_summary', string='Review Summary')
    initial_date = fields.Date(string='Initial Certification Date')
    issue_date = fields.Date(string='Certification Issue Date', store=True)
    validity_date = fields.Date(string='Certification Validity Date', store=True)
    expiry_date = fields.Date(string='Certification Expiry Date', store=True)
    qr_image = fields.Binary("QR Code", attachment=True)

    def generate_qr_code(self):
        for rec in self:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(rec.nomor_sertifikat)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

            # Dapatkan path ke logo
            logo_path = get_module_resource('v15_tsi', 'static/description', 'logo_tsi.png')
            if not logo_path:
                raise UserError("Logo tidak ditemukan. Pastikan file ada di: v15_tsi/static/img/logo_tsi.png")

            # Buka dan resize logo
            logo = Image.open(logo_path)
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.25)
            logo = logo.resize((logo_size, logo_size))

            # Sisipkan logo di tengah QR
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

            # Simpan sebagai binary
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            rec.qr_image = base64.b64encode(buffer.getvalue())

    @api.onchange('iso_reference')
    def _onchange_iso_reference(self):
        if not self.iso_reference:
            # Jika tidak ada ISO reference, isi dengan partner_id atau kondisi lain
            self.nama_customer = self.partner_id.id
        else:
            # Jika ada ISO reference, biarkan nama_customer tetap diambil dari relasi
            self.nama_customer = self.iso_reference.customer_id.id

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
    # initial_date = fields.Date(string='Initial Certification Date', related='review_summary_id.date', readonly=True)
    # issue_date = fields.Date(string='Certification Issue Date', compute='_compute_issue_date', store=True)
    # validity_date = fields.Date(string='Certification Validity Date', compute='_compute_validity_date', store=True)
    # expiry_date = fields.Date(string='Certificatio Expiry Date', compute='_compute_expiry_date', store=True)

    # @api.depends('initial_date')
    # def _compute_issue_date(self):
    #     for record in self:
    #         if record.initial_date:
    #             initial_date = fields.Datetime.from_string(record.initial_date)
    #             record.issue_date = (initial_date).date()
    #         else:
    #             record.issue_date = False

    # @api.depends('issue_date')
    # def _compute_validity_date(self):
    #     for record in self:
    #         if record.issue_date:
    #             issue_date = fields.Datetime.from_string(record.issue_date)
    #             record.validity_date = (issue_date + timedelta(days=(3*365-1))).date()
    #         else:
    #             record.validity_date = False

    # @api.depends('issue_date')
    # def _compute_expiry_date(self):
    #     for record in self:
    #         if record.issue_date:
    #             issue_date = fields.Datetime.from_string(record.issue_date)
    #             record.expiry_date = (issue_date + timedelta(days=(365-1))).date()
    #         else:
    #             record.expiry_date = False



    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.sertifikat')
        vals['name'] = sequence or _('New')
        if not vals.get('iso_reference'):
            vals['nama_customer'] = self.env.user.partner_id.id  # ✅ Fix di sini
        result = super(AuditSertifikat, self).create(vals)
        return result

    def set_to_confirm(self):
        self.write({'state': 'confirm'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})
        
        # Update res.partner with certification_lines
        partner = self.nama_customer
        if partner:
            cert_line_vals = {
                'sertifikat_reference': self.id,
                'no_sertifikat': self.nomor_sertifikat,
                'initial_date': self.initial_date,
                'issue_date': self.issue_date,
                'validity_date': self.validity_date,
                'expiry_date': self.expiry_date
            }
            partner.write({
                'certification_lines': [(0, 0, cert_line_vals)]
            })

            # Also update tahun_masuk
            # Ensure issue_date is a datetime.date object
            certification_year = self.issue_date.year if self.issue_date else ''
            tahun_masuk_vals = {
                'partner_id': partner.id,
                'sertifikat_reference': self.id,
                # 'iso_standard_ids': self.iso_reference.iso_standard_ids,
                'iso_standard_ids': [(6, 0, self.iso_reference.iso_standard_ids.ids)],
                'issue_date': self.issue_date,
                'certification_year': certification_year,
            }
            # Create new entry in 'tsi.tahun_masuk'
            self.env['tsi.tahun_masuk'].create(tahun_masuk_vals)

        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True
    
    @api.onchange('akre_tes')
    def _onchange_akre_tes(self):
        if self.akre_tes.name == 'KAN':
            self.sertifikat_non = [(5, 0, 0)]  
        elif self.akre_tes.name == 'NON KAN':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'Akreditasi 1':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'APMG':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'UAF':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'GLOBUS':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'IAF':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'SCC':
            self.sertifikat_kan = [(5, 0, 0)]

class AuditSertifikatDetail(models.Model):
    _name           = 'ops.sertifikat_summary'
    _description    = 'Audit Sertifikat Summary'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True)
    summary         = fields.Char(string='Summary')
    status          = fields.Char(string='Status')

class SertifikatKAN(models.Model):
    _name           = 'ops.sertifikat_kan'
    _description    = 'Audit Sertifikat KAN'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True)
    status_sertifikat   = fields.Selection([
                            ('sned_client', 'Draft send To Client'),
                            ('approv_client', 'Draft Approved by Client'),
                            ('register_kan', 'Draft Registered to KAN'),
                            ('approv_kan', 'Draft Approved by KAN'),
                            ('seritifikat_client', 'Certificate send to Client'),
                            ('received_client', 'Certificate received by Client'),
                        ], string='Accreditaion')
    date                = fields.Date(string='Date')
    remarks             = fields.Char(string='Remarks')

class SertifikatNonKAN(models.Model):
    _name           = 'ops.sertifikat_non'
    _description    = 'Audit Sertifikat Non KAN'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True)
    status_sertifikat   = fields.Selection([
                            ('sned_client', 'Draft send To Client'),
                            ('approv_client', 'Draft Approved by Client'),
                            ('seritifikat_client', 'Certificate send to Client'),
                            ('received_client', 'Certificate received by Client'),
                        ], string='Accreditaion')
    date                = fields.Date(string='Date')
    remarks             = fields.Char(string='Remarks')
