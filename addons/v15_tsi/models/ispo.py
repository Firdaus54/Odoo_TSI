from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class Ispo(models.Model):
    _name           = "tsi.ispo"
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = "Form ISPO"
    _order          = 'id DESC'
    
    name            = fields.Char(string="Document No",  readonly=True)
    reference        = fields.Many2one('crm.lead', string="Reference")
    customer        = fields.Many2one('res.partner', string="Customer", domain="[('is_company', '=', True)]")
    alamat          = fields.Char(string="Alamat")
    issue_date      = fields.Date(string="Issued Date", default=datetime.today())
    user_id = fields.Many2one(
        'res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    sales_person       = fields.Many2one('res.users', string="Sales Person")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    company_name        = fields.Char(string="Company Name")
    office_address      = fields.Char(string="Office Address")
    invoicing_address   = fields.Char(string="Invoicing Address", )
    contact_person      = fields.Char(string="Contact Person")
    accreditation     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    jabatan         = fields.Char(string="Jabatan")
    telepon         = fields.Char(string="Telepon")
    fax             = fields.Char(string="Fax")
    email           = fields.Char(string="Email")
    website         = fields.Char(string="Website")
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', index=True,)

    certification   = fields.Selection([
                            ('single',  'SINGLE SITE'),
                            ('multi',   'MULTI SITE'),
                        ], string='Certification Type', index=True)
    
    tx_site_count   = fields.Integer('Number of Site',)
    tx_remarks      = fields.Char('Remarks', )



    contact_name    = fields.Many2one('res.partner', string="Nama Contact")
    # state           = fields.Selection([
    #                         ('draft',   'Draft'),
    #                         ('running', 'Running'),
    #                         ('closed',  'Closed'),
    #                     ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    lingkup = fields.Selection([
                            ('baru',   'sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True)
    kepemilikan = fields.Selection([
                            ('bumn',   'BUMN'),
                            ('individu', 'INDIVIDU'),
                            ('bumd',  'BUMD'),
                            ('kud',  'KUD'),
                            ('pma',  'PMA'),
                        ], string='Kepemilikan', index=True)
    sertifikasi_baru = fields.Boolean(string='Sertifikasi Awal/Baru')
    re_sertifikasi = fields.Boolean(string='Re-Sertifikasi')
    perluasan = fields.Boolean(string='Perluasan Ruang Lingkup')
    pengurangan = fields.Boolean(string='Pengurangan Ruang Lingkup')
    transfer = fields.Boolean(string='Transfer CB/LS') 

    kebun_lines       = fields.One2many('tsi.kebun', 'reference', string="Kebun")
    pabrik_lines       = fields.One2many('tsi.pabrik', 'reference', string="Pabrik")

    outsourced_activity = fields.Text(string="Outsourced Activity", )


    is_associate        = fields.Boolean(string='Associate')    
    associate_id        = fields.Many2one('res.partner', "Associate Name", domain = [('is_associate','=',True)])

    iso_env_aspect_ids  = fields.Many2many('tsi.env_aspect',    string='Environmental Aspect')
    iso_aspect_other    = fields.Char(string="Other Aspect")

    # scope 
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIK'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True)
    boundaries  = fields.Text( string="Boundaries", default="All related area, department & functions within scope")
    cause       = fields.Text('NA Clause', )
    isms_doc    = fields.Text('ISMS Document', )

    # personnel
    head_office     = fields.Char(string="Head Office", )
    site_office     = fields.Char(string="Site Office", )
    off_location    = fields.Char(string="Off Location", )
    part_time       = fields.Char(string="Part Time", )
    subcon          = fields.Char(string="Sub Contractor", )
    unskilled       = fields.Char(string="Unskilled", )
    seasonal        = fields.Char(string="Seasonal", )
    total_emp       = fields.Char(string="Total Employee", )
    shift_number    = fields.Char(string="Shift", )
    number_site     = fields.Char(string="Number Site", )
    outsource_proc  = fields.Text('Outsourcing Process', )

    # management 
    last_audit      = fields.Text('Last Audit', )
    last_review     = fields.Text('Last Review', )


    tx_site_count   = fields.Integer('Number of Site',)
    tx_remarks      = fields.Char('Remarks', )

    # maturity
    start_implement     = fields.Char(string="Start Implement", )

    mat_consultancy     = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Use of Consultants", )
    mat_certified       = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified System", )
    other_system         = fields.Char(string='Other System')
    # mat_certified_cb    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified CB", )
    # mat_tools           = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Continual Improvement", )
    # mat_national        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="National Certified", )
    # mat_more            = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Setup More Standard", )

    txt_mat_consultancy = fields.Char(string="Tx Consultancy", )
    txt_mat_certified   = fields.Char(string="Tx Certified", )
    # txt_mat_certified_cb    = fields.Char(string="Tx Certified CB", )
    # txt_mat_tools       = fields.Char(string="Tx Continual Improvement", )
    # txt_mat_national    = fields.Char(string="Tx National Certified", )
    # txt_mat_more        = fields.Char(string="Tx Setup More Standard", )

    # multisite 
    site_name               = fields.Char(string='Site Name', )
    site_address            = fields.Text(string='Site Address', )
    site_emp_total          = fields.Char(string='Total Site Employee', )
    site_activity           = fields.Text(string='Site Activity', )

    audit_stage = fields.Selection([
                            ('initial',         'Initial Assesment'),
                            ('recertification', 'Recertification'),
                            ('transfer_surveilance',    'Transfer Assesment from Surveilance'),
                            ('transfer_recert',         'Transfer Assesment from Recertification'),
                        ], string='Audit Stage', index=True, )
    
    audit_similarities = fields.Selection([
                            ('similar',         'Similar Activities processes'),
                            ('diferences',      'Diferences between Activities'),
                        ], string='Multisite Similarities', index=True, )

    lingkup = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, )
    # kepemilikan = fields.Selection([
    #                         ('bumn',    'BUMN'),
    #                         ('individu','INDIVIDU'),
    #                         ('swasta',  'SWASTA'),
    #                         ('kud',     'KUD'),
    #                         ('pma',     'PMA'),
    #                     ], string='Kepemilikan', index=True, )
    
    # ISPO RELATED fields
    permohonan     = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, )
    lingkup = fields.Selection([
                            ('kebun',   'KEBUN'),
                            ('pabrik', 'Pabrik'),
                            ('integrasi',  'Integrasi'),
                        ], string='Ruang Lingkup', index=True, )
    tipe_tanah = fields.Selection([
                            ('tidak_gambut',   'Tidak Bergambut'),
                            ('gambut', 'Gambut'),
                        ], string='Tipe Tanah', index=True, )
    sebaran_tanah = fields.Selection([
                            ('tidak',       'Tidak berbatasan langsung dengan lahan negara/ masyarakat'),
                            ('berbatasan',  'Berbatasan dengan lahan negara/  Kawasan lindung namun terdapat Batasan alam yang jelas'),
                            ('lindung',     'Sebagian atau seluruhnya berada pada Kawasan Linding'),
                        ], string='Sebaran Geografis', index=True, )
    tipe_kegiatan = fields.Selection([
                            ('tidak',       'Tidak ada peremajaan'),
                            ('ada',  'Ada peremajaan'),
                        ], string='Tipe Kegiatan', index=True, )
    topografi = fields.Selection([
                            ('datar',       'Datar'),
                            ('bukit',  'Berbukit'),
                        ], string='Topografi Tanah', index=True, )

    is_kebun_pabrik     = fields.Boolean(string='Kebun / Pabrik')
                        
    legal_lokasi        = fields.Char(string='Ijin Lokasi', )
    legal_iup           = fields.Char(string='Ijin IUP', )
    legal_spup          = fields.Char(string='Ijin SPUP', )
    legal_itubp         = fields.Char(string='Ijin ITBUP', )
    legal_prinsip       = fields.Char(string='Ijin Prinsip', )
    legal_menteri       = fields.Char(string='Ijin Menteri', )
    legal_bkpm          = fields.Char(string='Ijin BKPM', )

    perolehan_a         = fields.Char(string='APL', )
    perolehan_b         = fields.Char(string='HPK', )
    perolehan_c         = fields.Char(string='Tanah Adat', )
    perolehan_d         = fields.Char(string='Tanah Lain', )

    legal_hgu           = fields.Char(string='HGU / HGB', )
    legal_amdal         = fields.Char(string='Izin Lingkungan - AMDAL', )

    is_plasma_swadaya   = fields.Boolean(string='Plasma / Swadaya', )

    kebun_sertifikat    = fields.Char(string='Sertifikat Tanah', )
    kebun_penetapan     = fields.Char(string='Penetapan', )
    kebun_std           = fields.Char(string='Surat Tanda Daftar', )
    kebun_pembentukan   = fields.Char(string='Pembentukan', )
    kebun_konversi      = fields.Char(string='Konversi', )
    kebun_kesepakatan   = fields.Char(string='Kesepakatan', )

    sertifikat_ispo     = fields.Text(string='Sertifikat ISPO', )

    tani_nama           = fields.Char(string='Nama Kelompok Tani', )
    tani_adrt           = fields.Char(string='Akta Pendirian', )
    tani_pembentukan    = fields.Char(string='Pembentukan Kelompok Tani', )
    tani_rko            = fields.Char(string='Rencana Kegiatan', )
    tani_kegiatan       = fields.Char(string='Laporan Kegiatan', )
    tani_jumlah         = fields.Char(string='Jumlah Petani', )
    tani_area           = fields.Char(string='Total Area', )
    tani_tertanam       = fields.Char(string='Area Tertanam', )
    tani_tbs            = fields.Char(string='Produksi TBS', )

    peta_lokasi         = fields.Char(string='Peta Lokasi', )

    add_nama_perusahaan = fields.Char(string='Informasi Konsultan', )
    add_sertifikasi     = fields.Char(string='Sertifikasi Lain', )
    add_pic             = fields.Char(string='Personal Perusahaan Yang sudah pelatihan Auditor ISPO', )
    add_kendali         = fields.Boolean(string='Tim Kendali Internal', )
    add_kendali_jml     = fields.Integer(string='Tim Kendali Internal Jumlah', )
    add_auditor         = fields.Boolean(string='Auditor Internal', )
    add_auditor_jml     = fields.Integer(string='Auditor Internal Jumlah', )

    ispo_kebun          = fields.One2many('tsi.ispo.kebun', 'reference', string="Kebun", index=True)
    ispo_pabrik         = fields.One2many('tsi.ispo.pabrik', 'reference', string="Pabrik", index=True)
    ispo_pemasok        = fields.One2many('tsi.ispo.pemasok', 'reference', string="Pemasok", index=True)
    ispo_sertifikat     = fields.One2many('tsi.ispo.sertifikat', 'reference', string="Sertifikat", index=True)

    partner_site        = fields.One2many('tsi.iso.site', 'reference_id', string="Personnel Situation", index=True)

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of attached documents")

    segment_id      = fields.Many2many('res.partner.category', string='Segment')
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Kategori', index=True)
    declaration     = fields.Text(string='Declaration')
    user_signature  = fields.Binary(string='Signature')
    lines_initial       = fields.One2many('tsi.iso.initial', 'reference_id_ispo', string="Lines Initial", index=True)
    lines_surveillance  = fields.One2many('tsi.iso.surveillance', 'reference_id_ispo', string="Lines SUrveillance", index=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', domain="[('standard', 'in', ['ispo'])]" )
    show_ispo           = fields.Boolean(string='Show ISPO', default=False)
    salesinfo_site_ispo    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id10', string="Additional Info", index=True)
    show_salesinfo      = fields.Boolean(string='Additional Info', default=False)
    #count
    count_review        = fields.Integer(string="Count Review", compute="compute_state", store=True)
    count_quotation     = fields.Integer(string="Count Quotation", compute="compute_state", store=True)
    count_sales         = fields.Integer(string="Count Sales", compute="compute_state", store=True)
    count_invoice       = fields.Integer(string="Count Invoice", compute="compute_state", store=True)

    state           =fields.Selection([
                            ('new',         'New'),
                            ('waiting',     'Waiting Verify'),
                            ('review',      'Review'),
                            ('approved',    'Verified'),
                            ('reject',      'Reject'),
                            ('quotation',   'Quotation'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')
    # Field Selection untuk Legalitas
    legalitas_type = fields.Selection([
        ('integrasi', 'Integrasi'),
        ('kebun', 'Kebun'),
        ('pabrik', 'Pabrik'),
        ('swadaya_plasma', 'Swadaya/Plasma'),
    ], string='Tipe Legalitas')

    kebun_line_ids = fields.One2many('tsi.ispo.kebun.line', 'reference_id', string='Personal Situation Kebun')
    pabrik_line_ids = fields.One2many('tsi.ispo.pabrik.line', 'reference_id', string='Personal Situation Pabrik')
    swadaya_line_ids = fields.One2many('tsi.ispo.swadaya.plasma.line', 'reference_id', string='Personal Situation Swadaya/Plasma')

    # Field-field tambahan untuk Integrasi
    hgu = fields.Char(string='No. Sertifikat HGU')
    sk_hgu = fields.Char(string='No. SK HGU')
    hgb = fields.Char(string='No. Sertifikat HGB')
    sk_hgb = fields.Char(string='No. SK HGB')
    iup = fields.Char(string='IUP / IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    pup = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP')
    izin_lingkungan_integrasi = fields.Char(string='Izin Lingkungan (Integrasi)')
    luas_lahan = fields.Float(string='Luas Lahan (Ha)')
    kapasitas_pabrik = fields.Float(string='Kapasitas Pabrik (ton/tbs/jam)')
    izin_lokasi = fields.Char(string='Izin Lokasi')
    apl = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat')
    risalah_panitia = fields.Char(string='Risalah Panitia A/B')
    lahan_gambut = fields.Char(string='Lahan Gambut / Mineral')
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta')
    jlh_kebun = fields.Char('Jumlah Kebun')
    jlh_pabrik = fields.Char('Jumlah Pabrik')

    # Field-field tambahan untuk Kebun
    hgu_kebun = fields.Char(string='No. Sertifikat HGU')
    sk_hgu_kebun = fields.Char(string='No. SK HGU')
    iupb = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    izin_lingkungan_kebun = fields.Char(string='Izin Lingkungan')
    informasi_plasma_kebun = fields.Char(string='Informasi Plasma')
    pup_kebun = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun')
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta')
    risalah_panitia_kebun = fields.Char(string='Risalah Panitia B')
    jumlah_kebun = fields.Char('Jumlah Kebun')
    apl_kebun = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat')

    # Field-field tambahan untuk Pabrik
    hgb_pabrik = fields.Char(string='No. Sertifikat HGB')
    sk_hgb_pabrik = fields.Char(string='No. SK HGB')
    iup_pabrik = fields.Char(string='IUP / IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    sumber_bahan_baku = fields.Char(string='20% Sumber Bahan Baku')
    izin_lingkungan_pabrik = fields.Char(string='Izin Lingkungan')
    kapasitas_pabrik_pabrik = fields.Float(string='Kapasitas Pabrik (ton/tbs/jam)')
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta')
    risalah_panitia_pabrik = fields.Char(string='Risalah Panitia A')
    jumlah_pabrik = fields.Char('Jumlah Pabrik')
    apl_pabrik = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat')

    # Field-field tambahan untuk Swadaya/Plasma
    shm = fields.Char(string='SHM/Kepemilikan Lahan Yang diakui Pemerintah')
    stdb = fields.Char(string='STDB')
    sppl = fields.Char(string='SPPL')
    akta_pendirian = fields.Char(string='Akta Pendirian dan SK Kemenhumkam')
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta')
    jlh_anggota = fields.Char('Jumlah Anggota')
    jlh_kebun_plasma = fields.Char('Jumlah Kebun')
    
    #field auditor
    audit_pt = fields.Boolean(string='Audit Per PT 2 Orang')
    nama_audit_pt = fields.Char(string='Nama Auditor PT')
    audit_group = fields.Boolean(string='Audit Per Group 5 Orang')
    ics = fields.Boolean(string='ICS untuk Plasma/Swadaya')
    nama_ics = fields.Char(string='Nama ICS / Auditor Swadaya') 

    state_sales = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status Sales', compute='_compute_state', store=True, tracking=True)

    audit_status = fields.Selection([
                    ('program', 'Program'),
                    ('plan', 'Plan'),
                    ('report', 'Report'),
                    ('recommendation', 'Recommendation'),
                    ('certificate', 'Certificate'),
                    ('draft', 'Draft'),
                    ('done', 'Done')
                    ], string='Audit Status', compute='_compute_audit_status', store=True, tracking=True)



    @api.depends('name')
    def _compute_state(self):
        for record in self:
            if record.id:
                sale_order = self.env['sale.order'].search([
                    ('ispo_reference', '=', record.name)
                ], limit=1)

                if sale_order:
                    record.state_sales = sale_order.state
                else:
                    record.state_sales = False

    @api.depends('name')
    def _compute_audit_status(self):
        for record in self:
            if record.id:
                sale_order = self.env['sale.order'].search([
                    ('ispo_reference', '=', record.name),
                    ('state', '=', 'sale')
                ], limit=1)

                record.audit_status = sale_order.audit_status if sale_order else False

    @api.onchange('legalitas_type')
    def _onchange_legalitas_type(self):
        if self.legalitas_type == 'integrasi':
            return {
                'domain': {
                    'hgu': [('required', '=', True)],
                    'hgb': [('required', '=', True)],
                    'iup': [('required', '=', True)],
                    'pup': [('required', '=', True)],
                    'izin_lingkungan_integrasi': [('required', '=', True)],
                    'luas_lahan': [('required', '=', True)],
                    'kapasitas_pabrik': [('required', '=', True)],
                    'izin_lokasi': [('required', '=', True)],
                    'apl': [('required', '=', True)],
                    'risalah_panitia': [('required', '=', True)],
                    'lahan_gambut': [('required', '=', True)],
                    'peta_ids': [('name', 'in', ['Peta Lokasi', 'Peta Topografi', 'Peta Kebun', 'Peta Area Statement', 'Peta Kawasan Lindung', 'Peta Sebaran Sungai', 'Peta Kemiringan Lahan'])],
                }
            }
        elif self.legalitas_type == 'kebun':
            return {
                'domain': {
                    'hgu_kebun': [('required', '=', True)],
                    'iupb': [('required', '=', True)],
                    'izin_lingkungan_kebun': [('required', '=', True)],
                    'luas_lahan': [('required', '=', True)],
                    'izin_lokasi': [('required', '=', True)],
                    'apl': [('required', '=', True)],
                    'lahan_gambut': [('required', '=', True)],
                    'peta_ids': [('name', 'in', ['Peta Lokasi', 'Peta Topografi', 'Peta Kebun', 'Peta Area Statement', 'Peta Kawasan Lindung', 'Peta Sebaran Sungai', 'Peta Kemiringan Lahan'])],
                }
            }
        elif self.legalitas_type == 'pabrik':
            return {
                'domain': {
                    'hgb_pabrik': [('required', '=', True)],
                    'kapasitas_pabrik_pabrik': [('required', '=', True)],
                    'luas_lahan': [('required', '=', True)],
                    'izin_lokasi': [('required', '=', True)],
                    'apl': [('required', '=', True)],
                    'risalah_panitia': [('required', '=', True)],
                    'lahan_gambut': [('required', '=', True)],
                    'peta_ids': [('name', 'in', ['Peta Lokasi', 'Peta Area Statement'])],
                }
            }
        elif self.legalitas_type == 'swadaya_plasma':
            return {
                'domain': {
                    'shm': [('required', '=', True)],
                    'stdb': [('required', '=', True)],
                    'sppl': [('required', '=', True)],
                    'akta_pendirian': [('required', '=', True)],
                    'luas_lahan': [('required', '=', True)],
                    'izin_lokasi': [('required', '=', True)],
                    'apl': [('required', '=', True)],
                    'lahan_gambut': [('required', '=', True)],
                    'peta_ids': [('name', 'in', ['Peta Lokasi', 'Peta Topografi', 'Peta Kebun', 'Peta Area Statement', 'Peta Area Konservasi', 'Peta Kawasan Lindung'])],
                }
            }
    
    @api.onchange('certification')
    def _onchange_certification(self):
        if self.certification == 'Single Site':
            self.tx_site_count = 1
        elif self.certification == 'Multi Site':
            self.tx_site_count = False  # Anda dapat mengganti dengan nilai default yang sesuai untuk multi-site

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            if self.customer.office_address:
                self.office_address = self.customer.office_address;
            if self.customer.contact_person:
                self.contact_person = self.customer.contact_person;
            if self.customer.invoice_address:
                self.invoicing_address = self.customer.invoice_address;
            if self.customer.phone:
                self.telepon = self.customer.phone;
            if self.customer.email:
                self.email = self.customer.email;
            if self.customer.website:
                self.website = self.customer.website;
    
    def create_open_iso(self):
        if self.iso_standard_ids :
            for standard in self.iso_standard_ids :

                self.env['tsi.ispo.review'].create({
                    'reference'         : self.id,
                    'certification'     : self.certification,
                    'iso_standard_ids'  : standard,
                    'scope'             : self.scope,
                    'website'           : self.website,
                    'office_address'    : self.office_address,
                    'invoicing_address' : self.invoicing_address,
                    'contact_person'    : self.contact_person,
                    'jabatan'           : self.jabatan,
                    'telepon'           : self.telepon,
                    'fax'               : self.fax,
                    'email'             : self.email,
                    'telepon'          : self.telepon,
                    'stage_audit'       : self.audit_stage,
                    'start_implement'   : self.start_implement,
                    'mat_consultancy'   : self.mat_consultancy,
                    'mat_certified'     : self.mat_certified,
                    'txt_mat_consultancy': self.txt_mat_consultancy,
                    'txt_mat_certified' : self.txt_mat_certified,

                })
        self.compute_state()
    
    def create_open_quotation(self):

        self.env['sale.order'].create({
            'ispo_reference' : self.id,
            'partner_id' : self.customer.id,
        })
        self.compute_state()
    
    def set_to_running(self):
        # Cek apakah legalitas_type sudah di-set
        if self.legalitas_type == 'integrasi':
            # Validasi apakah semua field yang diperlukan sudah diisi
            if not (self.hgu and self.sk_hgu and self.hgb and self.sk_hgb and self.iup and self.pup and self.izin_lingkungan_integrasi):
                raise UserError("Harap lengkapi semua field (HGU,SK HGU, HGB, SK HGB, IUP, PUP, Izin Lingkungan) yang diperlukan untuk tipe 'Integrasi' sebelum melanjutkan.")
        
        elif self.legalitas_type == 'kebun':
            # Validasi apakah semua field yang diperlukan sudah diisi
            if not (self.hgu_kebun and self.sk_hgu_kebun and self.izin_lingkungan_kebun and
                    self.iupb):
                raise UserError("Harap lengkapi semua field (HGB Kebun, SK HGB Kebun, IUP, Izin Lingkungan) yang diperlukan untuk tipe 'Kebun' sebelum melanjutkan.")
        
        elif self.legalitas_type == 'pabrik':
            # Validasi apakah semua field yang diperlukan sudah diisi
            if not (self.hgb_pabrik and self.sk_hgb_pabrik and
                    self.iup_pabrik):
                raise UserError("Harap lengkapi semua field (HGB Pabrik, SK HGB Pabrik, IUP) yang diperlukan untuk tipe 'Pabrik' sebelum melanjutkan.")

        # Jika semua validasi lolos, set ke state 'waiting'
        self.write({'state': 'waiting'})
        return True

    def set_to_closed(self):
        # self.create_open_iso()
        self.write({'state': 'approved'}) 

        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True
    
    def set_to_revice(self):
        self.write({'state': 'approved'})
        review_records = self.env['tsi.ispo.review'].search([('customer', '=', self.customer.id)])
        review_records.write({'state': 'revice'})         
        return True

    def set_to_quotation(self):
        self.write({'state': 'quotation'})            
        return True

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_quotation.app.ispo',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_quotation_app_ispo_view').id,
            'target': 'new'
        }
    
    def get_ispo_review(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Review',
                'view_mode': 'tree,form',
                'res_model': 'tsi.ispo.review',
                'domain': [('reference', '=', self.id)],
                'context': "{'create': True}"
            }

    def get_iso_quotation(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quotation',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': [('ispo_reference', '=', self.id),('state', '=', 'draft')],
                'context': "{'create': True}"
            }

    def get_iso_sales(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sales',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': [('ispo_reference', '=', self.id),('state', '=', 'sale')],
                'context': "{'create': True}"
            }

    def get_iso_invoice(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('ispo_reference', '=', self.id)],
                'context': "{'create': True}"
            }
    
    def _compute_attached_docs_count(self):
        attachment_obj = self.env['ir.attachment']
        for task in self:
            task.doc_count = attachment_obj.search_count([
                '&', ('res_model', '=', 'tsi.iso'), ('res_id', '=', task.id)
            ])

    def attached_docs_view_action(self):
        self.ensure_one()
        domain = [
            '&', ('res_model', '=', 'tsi.iso'), ('res_id', 'in', self.ids),
        ]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks of your project.</p>
                    '''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }
    
    def update_to_contact(self):
        self.customer.write({
            'phone'             : self.telepon,
            'office_address'    : self.office_address,
            'invoice_address'   : self.invoicing_address,
            'website'           : self.website,
            'email'             : self.email,
            'boundaries'        : self.boundaries,
            'scope'             : self.scope,
            'number_site'       : self.tx_site_count,
            'kategori'          : self.kategori,
            'function'          : self.jabatan,
            'email'             : self.email,
            'website'           : self.website,
            'is_associate'      : self.is_associate,
            'category_id'       : self.segment_id,
            'total_emp'         : self.total_emp,
            'contact_person'    : self.contact_person
            })            
        return True
    
    @api.onchange('certification')
    def _onchange_certification(self):
        if self.certification == 'single':
            self.tx_site_count = 1
        elif self.certification == 'multi':
            self.tx_site_count = 0  # Anda dapat mengganti dengan nilai default yang sesuai untuk multi-site

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            if self.customer.office_address:
                self.office_address = self.customer.office_address;
            if self.customer.contact_person:
                self.contact_person = self.customer.contact_person;
            if self.customer.invoice_address:
                self.invoicing_address = self.customer.invoice_address;
            if self.customer.phone:
                self.telepon = self.customer.phone;
            if self.customer.email:
                self.email = self.customer.email;
            if self.customer.website:
                self.website = self.customer.website;
    
    @api.depends('customer')
    def compute_state(self):
        for obj in self:
            if obj.id :
                review = self.env['tsi.ispo.review'].search_count([('reference.id', '=', obj.id)])
                if review :
                    obj.count_review = review

                count_quotation = self.env['sale.order'].search_count([('ispo_reference.id', '=', obj.id)])
                if count_quotation :
                    obj.count_quotation = count_quotation

                count_sales     = self.env['sale.order'].search_count([('ispo_reference.id', '=', obj.id)])
                if count_sales :
                    obj.count_sales = count_sales

                count_invoice   = self.env['account.move'].search_count([('ispo_reference.id', '=', obj.id)])
                if count_invoice :
                    obj.count_invoice = count_invoice

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :  
                obj.show_ispo = False               
                obj.show_salesinfo = False
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISPO' :
                        if obj.show_ispo != True :
                            obj.show_ispo = False
                        obj.show_ispo = True
                    elif standard.name == 'ISO 9001' :
                        obj.show_salesinfo = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.ispo')
        vals['name'] = sequence or _('New')
        result = super(Ispo, self).create(vals)
        return result

class PetaTipe(models.Model):
    _name = 'tipe.peta.ispo'
    _description = 'Tipe Peta'

    name = fields.Char(string='Nama Peta')



class Kebun(models.Model):
    _name           = 'tsi.kebun'
    _description    = 'Kebun'

    reference  = fields.Many2one('tsi.ispo', string="Reference", ondelete='cascade')
    name        = fields.Char(string='Nama')
    lokasi      = fields.Char(string='Lokasi') 
    karyawan    = fields.Char(string='Karyawan') 
    luas        = fields.Char(string='Luas') 
    tahun_tanam = fields.Char(string='Tahun Tanam') 
    keterangan  = fields.Text(string='Keterangan') 

class Pabrik(models.Model):
    _name           = 'tsi.pabrik'
    _description    = 'Pabrik'

    reference  = fields.Many2one('tsi.ispo', string="Reference", ondelete='cascade')
    name        = fields.Char(string='Nama')
    lokasi      = fields.Char(string='Lokasi') 
    karyawan    = fields.Char(string='Karyawan') 
    koordinat        = fields.Char(string='Koordinat') 
    kapasitas = fields.Char(string='Kapasitas') 
    volume = fields.Char(string='Volume') 

class ISOStandard(models.Model):
    _name           = 'tsi.iso.standard'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Standard'

    name            = fields.Char(string='Nama')
    description     = fields.Char(string='Description')
    standard        = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',  'ISPO'),
                        ], string='Standard', index=True)
    
class ISPOKebun(models.Model):
    _name           = 'tsi.ispo.kebun'
    _description    = 'ISPO Kebun'

    reference       = fields.Many2one('tsi.ispo', string="Reference")
    name            = fields.Char(string='Nama Kebun')
    lokasi          = fields.Text(string='Lokasi')
    karyawan        = fields.Char(string='Jumlah Karyawan')
    luas            = fields.Char(string='Luas HGU')
    tahun_tanam     = fields.Char(string='Tahun Tanam')
    keterangan      = fields.Text(string='Keterangan')

class ISPOPabrik(models.Model):
    _name           = 'tsi.ispo.pabrik'
    _description    = 'ISPO Pabrik'

    reference       = fields.Many2one('tsi.ispo', string="Reference")
    name            = fields.Char(string='Nama Pabrik')
    lokasi          = fields.Text(string='Lokasi')
    karyawan        = fields.Char(string='Jumlah Karyawan')
    luas            = fields.Char(string='Koordinat GPS')
    tahun_tanam     = fields.Char(string='Kapasitas')
    keterangan      = fields.Text(string='Volume Tahunan')

class ISPOSertifikat(models.Model):
    _name           = 'tsi.ispo.sertifikat'
    _description    = 'ISPO Sertifikat'

    reference       = fields.Many2one('tsi.ispo', string="Reference")
    name            = fields.Char(string='Nama Sertifikat')
    nomor           = fields.Char(string='Nomor Sertifikat')
    uplad_sertifikat = fields.Binary('Upload Sertifikat')
    file_name       = fields.Char('Filename')

class ISPOPemasok(models.Model):
    _name           = 'tsi.ispo.pemasok'
    _description    = 'ISPO Pemasok'

    reference       = fields.Many2one('tsi.ispo', string="Reference")
    name            = fields.Char(string='Nama Pemasok')
    lokasi          = fields.Text(string='Lokasi')
    total_area      = fields.Char(string='Total Area')
    total_tertanam  = fields.Char(string='Area Tertanam')
    produksi        = fields.Char(string='Produksi TBS')
    koordinat       = fields.Char(string='Koordinat GPS')

class ISOSite(models.Model):
    _name           = 'tsi.iso.site'
    _description    = 'Site'

    reference_id    = fields.Many2one('tsi.ispo', string="Reference")
    nama_site       = fields.Char(string='Nama Site')
    type            = fields.Char(string='Type')
    address         = fields.Char(string='Address')
    product         = fields.Char(string='Product / Process / Activities')
    total_emp       = fields.Char(string='Total No. of Employeesption')
    off_location    = fields.Char(string='Off-location')
    part_time       = fields.Char(string='Part-time (4 hours / day)')
    subcon          = fields.Char(string='Subcontractor')
    unskilled       = fields.Char(string='Unskilled Temporary')
    seasonal        = fields.Char(string='Seasonal Workers')
    non_shift       = fields.Char(string='Non shift')
    shift1          = fields.Char(string='Shift 1')
    shift2          = fields.Char(string='Shift 2')
    shift3          = fields.Char(string='Shift 3')
    differs         = fields.Char(string='Process Differs Across All Shifts')

class TsiIspoKebunLine(models.Model):
    _name           = 'tsi.ispo.kebun.line'
    _description    = 'Site'

    reference_id = fields.Many2one('tsi.ispo', string='Reference')
    nama_kebun = fields.Char(string='Nama Kebun Kelapa Sawit')
    lokasi = fields.Char(string='Lokasi Kebun Kelapa Sawit')
    jumlah_karyawan = fields.Integer(string='Jumlah Karyawan')
    luas_hgu = fields.Float(string='Luas HGU (Ha)')
    tahun_tanam = fields.Char(string='Tahun Tanam Awal')
    keterangan = fields.Text(string='Keterangan')

class TsiIspoPabrikLine(models.Model):
    _name           = 'tsi.ispo.pabrik.line'
    _description    = 'Site'

    reference_id = fields.Many2one('tsi.ispo', string='Reference')
    nama_pabrik = fields.Char(string='Nama Pabrik Kelapa Sawit')
    lokasi = fields.Char(string='Lokasi Kebun Kelapa Sawit')
    jumlah_karyawan = fields.Integer(string='Jumlah Karyawan')
    koordinat_gps = fields.Char(string='Koordinat GPS (Bujur & Lintang)')
    kapasitas = fields.Char(string='Kapasitas Terpasang & Aktual (ton TBS/jam)')
    volume_tahunan = fields.Char(string='Volume Tahunan CPO & Kernel')

class TsiIspoSwadayaPlasmakLine(models.Model):
    _name           = 'tsi.ispo.swadaya.plasma.line'
    _description    = 'Site'

    reference_id = fields.Many2one('tsi.ispo', string='Reference')
    nama_kebun = fields.Char(string='Nama Kebun Pemasok')
    lokasi = fields.Char(string='Lokasi Kebun Pemasok')
    total_area = fields.Float(string='Total Area (Ha)')
    area_tertanam = fields.Float(string='Area Tertanam (Ha)')
    produksi_tbs = fields.Float(string='Produksi TBS (Ton/Tahun)')
    koordinat_gps = fields.Char(string='Koordinat GPS (Bujur & Lintang)')




class SKHguIntegrasi(models.Model):
    _name           = 'tsi.ispo.sk.hgu'
    _description    = 'No SK HGU'

    nama       = fields.Char(string='Nama')
    

class SerHGUIntegrasi(models.Model):
    _name           = 'tsi.ispo.ser.hgu'
    _description    = 'No Sertifikat HGU'
    
    nama       = fields.Char(string='Nama')
    

class SKHgbIntegrasi(models.Model):
    _name           = 'tsi.ispo.sk.hgb'
    _description    = 'No SK HGB'
    
    nama       = fields.Char(string='Nama')
    

class SerHGBIntegrasi(models.Model):
    _name           = 'tsi.ispo.ser.hgb'
    _description    = 'No Sertifikat HGB'
    
    nama       = fields.Char(string='Nama')


class SKHguKebun(models.Model):
    _name           = 'tsi.ispo.sk.hgu.kebun'
    _description    = 'No SK HGU'

    nama       = fields.Char(string='Nama')
    

class SerHGUKebun(models.Model):
    _name           = 'tsi.ispo.ser.hgu.kebun'
    _description    = 'No Sertifikat HGU'
    
    nama       = fields.Char(string='Nama')
    

class SKHgbPabrik(models.Model):
    _name           = 'tsi.ispo.sk.hgb.pabrik'
    _description    = 'No SK HGB'
    
    nama       = fields.Char(string='Nama')
    

class SerHGBPabrik(models.Model):
    _name           = 'tsi.ispo.ser.hgb.pabrik'
    _description    = 'No Sertifikat HGB'
    
    nama       = fields.Char(string='Nama')    