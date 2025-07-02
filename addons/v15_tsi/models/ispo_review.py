from base64 import standard_b64decode
from odoo import models, fields, api
from datetime import datetime, timedelta


class ISPOReview(models.Model):
    _name           = "tsi.ispo.review"
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = "ISPO Review"
    _order          = 'id DESC'

    def _get_default_iso(self):
        return self.env['sale.order'].search([('id','in',self.env.context.get('active_ids'))],limit=5).iso_standard_ids

    reference       = fields.Many2one('tsi.ispo', string="Reference")
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', index=True, related='reference.doctype', store=True)

    customer        = fields.Many2one('res.partner', string="Customer", related='reference.customer', store=True)

    name            = fields.Char(string="Document No",  readonly=True)
    office_address      = fields.Char(string="Office Address", related="reference.office_address")
    invoicing_address   = fields.Char(string="Invoicing Address", related="reference.invoicing_address")
    received_date   = fields.Date(string="Issued Date", related="reference.issue_date")    
    review_date     = fields.Datetime(string="Verified Date", default=datetime.now())    
    finish_date     = fields.Datetime(string="Approve Date", readonly=True)    
    
    review_by       = fields.Many2one('res.users', string="Created By", related="reference.user_id")
    sales_person       = fields.Many2one('res.users', string="Sales Person", related="reference.sales_person")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    accreditation         = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation")

    # company_name    = fields.Char(string="Company Name")
    # ea_code         = fields.Many2one(string="EA Code", related='reference.ea_code')
    contact_person  = fields.Char(string="Contact Person", related="reference.contact_person")
    jabatan         = fields.Char(string="Position", related="reference.jabatan")
    telepon         = fields.Char(string="Telephone", related="reference.telepon")
    fax             = fields.Char(string="Fax", related="reference.fax")
    email           = fields.Char(string="Email", related="reference.email")
    website         = fields.Char(string="Website", related="reference.website")
    # cellular        = fields.Char(string="Celular", related="reference.cellular")
    # alt_scope       = fields.Text('Alt Scope', website_form_blacklisted=False)
    # alt_scope_id    = fields.Many2one('tsi.alt_scope',      string='Alt Scope')
    catatan             = fields.Text('Notes')

    # scope           = fields.Text(string="Scope", related='reference.scope', store=True)
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIK'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', related='reference.scope', index=True)
    boundaries  = fields.Text(string="Boundaries", related="reference.boundaries")
    cause       = fields.Text('Mandatory SNI', related='reference.cause')

    # personnel
    partner_site    = fields.One2many('tsi.iso.site', 'reference_id', string="Personnel Situation", index=True, related='reference.partner_site')
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
    outsourced_activity = fields.Text(string="Outsourced Activity", )

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
    
    stage_audit     = fields.Selection([
                            ('Stage-1', 'Stage 1'),
                            ('Stage-2', 'Stage 2'),
                            ('Surveillance-1', 'Surveillance 1'),
                            ('Surveillance-2', 'Surveillance 2'),
                            ('Surveillance-3', 'Surveillance 3'),
                            ('Surveillance-4', 'Surveillance 4'),
                            ('Recertification-1', 'Recertification 1'),
                            ('Recertification-2', 'Recertification 2'),
                        ], string='Audit Stage', index=True, related="reference.audit_stage")
    tx_site_count   = fields.Integer('Number of Site', )
    tx_remarks      = fields.Char('Remarks', related="reference.tx_remarks")
    certification   = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, readonly=True, related="reference.certification" )
    
    audit_stage = fields.Selection([
                            ('initial',         'Initial Assesment'),
                            ('recertification', 'Recertification'),
                            ('transfer_surveilance',    'Transfer Assesment from Surveilance'),
                            ('transfer_recert',         'Transfer Assesment from Recertification'),
                        ], string='Audit Stage', index=True, related="reference.audit_stage")
    
    legalitas_type = fields.Selection([
        ('integrasi', 'Integrasi'),
        ('kebun', 'Kebun'),
        ('pabrik', 'Pabrik'),
        ('swadaya_plasma', 'Swadaya/Plasma'),
    ], string='Tipe Legalitas', related="reference.legalitas_type")
    kebun_line_ids = fields.One2many('tsi.ispo.kebun.line', 'reference_id', string='Personal Situation Kebun', related="reference.kebun_line_ids")
    pabrik_line_ids = fields.One2many('tsi.ispo.pabrik.line', 'reference_id', string='Personal Situation Pabrik', related="reference.pabrik_line_ids")
    swadaya_line_ids = fields.One2many('tsi.ispo.swadaya.plasma.line', 'reference_id', string='Personal Situation Swadaya/Plasma', related="reference.swadaya_line_ids")

    # Field-field tambahan untuk Integrasi
    hgu = fields.Char(string='No. Sertifikat HGU', related="reference.hgu")
    sk_hgu = fields.Char(string='No. SK HGU', related="reference.sk_hgu")
    hgb = fields.Char(string='No. Sertifikat HGB', related="reference.hgb")
    sk_hgb = fields.Char(string='No. SK HGB', related="reference.sk_hgb")
    iup = fields.Char(string='IUP / IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP', related="reference.iup")
    pup = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun', related="reference.pup")
    izin_lingkungan_integrasi = fields.Char(string='Izin Lingkungan (Integrasi)', related="reference.izin_lingkungan_integrasi")
    luas_lahan = fields.Float(string='Luas Lahan', related="reference.luas_lahan")
    kapasitas_pabrik = fields.Float(string='Kapasitas Pabrik', related="reference.kapasitas_pabrik")
    izin_lokasi = fields.Char(string='Izin Lokasi', related="reference.izin_lokasi")
    apl = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat', related="reference.apl")
    risalah_panitia = fields.Char(string='Risalah Panitia A/B', related="reference.risalah_panitia")
    lahan_gambut = fields.Char(string='Lahan Gambut / Mineral', related="reference.lahan_gambut")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    jlh_kebun = fields.Char('Jumlah Kebun' , related="reference.jlh_kebun")
    jlh_pabrik = fields.Char('Jumlah Pabrik', related="reference.jlh_pabrik")
    # peta = fields.Selection([
    #     ('Peta Lokasi', 'Peta Lokasi'),
    #     ('Peta Topografi', 'Peta Topografi'),
    #     ('Peta Kebun', 'Peta Kebun'),
    #     ('Peta Area Statement', 'Peta Area Statement'),
    #     ('Peta Kawasan Lindung', 'Peta Kawasan Lindung'),
    #     ('Peta Sebaran Sungai', 'Peta Sebaran Sungai'),
    #     ('Peta Kemiringan Lahan', 'Peta Kemiringan Lahan'),
    # ], string='Peta - Peta', related="reference.peta")

    # Field-field tambahan untuk Kebun
    hgu_kebun = fields.Char(string='No. Sertifikat HGU', related="reference.hgu_kebun")
    sk_hgu_kebun= fields.Char(related="reference.sk_hgu_kebun")
    iupb = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP', related="reference.iupb")
    izin_lingkungan_kebun = fields.Char(string='Izin Lingkungan', related="reference.izin_lingkungan_kebun")
    informasi_plasma_kebun = fields.Char(string='Informasi Plasma', related="reference.informasi_plasma_kebun")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    pup_kebun = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun', related="reference.pup_kebun")
    risalah_panitia_kebun = fields.Char(string='Risalah Panitia B',related="reference.risalah_panitia_kebun")
    jumlah_kebun = fields.Char('Jumlah Kebun' , related="reference.jumlah_kebun")
    apl_kebun = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat', related="reference.apl_kebun")

    # Field-field tambahan untuk Pabrik
    hgb_pabrik = fields.Char(string='No. Sertifikat HGB' , related="reference.hgb_pabrik")
    sk_hgb_pabrik = fields.Char(string='No. SK HGB' , related="reference.sk_hgb_pabrik")
    kapasitas_pabrik_pabrik = fields.Float(string='Kapasitas Pabrik', related="reference.kapasitas_pabrik_pabrik")
    iup_pabrik = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP', related="reference.iup_pabrik")
    sumber_bahan_baku = fields.Char(string='20% Sumber Bahan Baku', related="reference.sumber_bahan_baku")
    izin_lingkungan_pabrik = fields.Char(string='Izin Lingkungan', related="reference.izin_lingkungan_pabrik")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    risalah_panitia_pabrik = fields.Char(string='Risalah Panitia A',related="reference.risalah_panitia_pabrik")
    jumlah_pabrik = fields.Char('Jumlah Pabrik' , related="reference.jumlah_pabrik")
    apl_pabrik = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat', related="reference.apl_pabrik")

    # Field-field tambahan untuk Swadaya/Plasma
    shm = fields.Char(string='SHM/Kepemilikan Lahan Yang diakui Pemerintah', related="reference.shm")
    stdb = fields.Char(string='STDB', related="reference.stdb")
    sppl = fields.Char(string='SPPL', related="reference.sppl")
    akta_pendirian = fields.Char(string='Akta Pendirian dan SK Kemenhumkam', related="reference.akta_pendirian")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    salesinfo_site_ispo    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id10', string="Additional Info", index=True, related="reference.salesinfo_site_ispo")
    jlh_kebun_plasma = fields.Char('Jumlah Kebun' , related="reference.jlh_kebun_plasma")
    jlh_anggota = fields.Char('Jumlah Anggota' , related="reference.jlh_anggota")
    
    audit_type      = fields.Selection([
                            ('single',      'SINGLE AUDIT'),
                            ('join',        'JOIN AUDIT'),
                            ('combine',     'COMBINE AUDIT'),
                            ('integrated',  'INTEGRATED AUDIT'),
                        ], string='Audit Type', index=True)
    allowed_sampling    = fields.Char(string="Number of Sampling")

    proposed_aspect = fields.Char(string="Proposed Standard")
    proposed_desc   = fields.Char(string="Description")
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_iso, related="reference.iso_standard_ids")

    # EMPLOYEE INFORMATION
    total_emp           = fields.Integer(string="Total Employee")
    site_emp_total      = fields.Integer(string='Total Site Employee')
    offsite_emp_total   = fields.Integer(string='Total OffSite Employee')
    ho_emp_total        = fields.Integer(string='Total HO Employee')
    number_of_site      = fields.Integer(string='Number of Site')

    mandays_ori_lines   = fields.One2many('tsi.iso.mandays', 'review_id', string="Mandays Original", index=True)
    mandays_isms_lines  = fields.One2many('tsi.iso.mandays.isms', 'review_id', string="Mandays ISMS", index=True)
    mandays_inte_lines  = fields.One2many('tsi.iso.mandays.integrated', 'review_id', string="Mandays Integrated", index=True)
    mandays_audit_time  = fields.One2many('tsi.iso.mandays.audit_time', 'review_id', string="Audit Time", index=True)
    mandays_justify     = fields.One2many('tsi.iso.mandays.justification', 'review_id', string="Justification", index=True)
    mandays_justify_isms     = fields.One2many('tsi.iso.mandays.justification.isms', 'review_id', string="Justification - ISMS", index=True)
    mandays_pa          = fields.One2many('tsi.iso.mandays.pa', 'review_id', string="PA", index=True)

# ISPO RELATED FIELD
    ispo_evaluasi       = fields.One2many('tsi.ispo.evaluasi', 'review_id', string="Evaluasi", index=True)
    ispo_nilai_skor     = fields.One2many('tsi.ispo.nilai_skor', 'review_id', string="Nilai Skor", index=True)
    ispo_justification  = fields.One2many('tsi.ispo.justification', 'review_id', string="Justification", index=True)
    ispo_mandays        = fields.One2many('tsi.ispo.mandays', 'review_id', string="Mandays", index=True)
    ispo_total_mandays  = fields.One2many('tsi.ispo.total_mandays', 'review_id', string="Total Mandays", index=True)

    sampling_pabrik     = fields.Boolean(string='Sampling Pabrik')
    sampling_kebun      = fields.Boolean(string='Sampling Kebun')


    state           = fields.Selection([
                            ('new',         'New'),
                            # ('review',      'Review'),
                            ('approved',    'Approved'),
                            ('revice',    'Revised'),
                            ('reject',      'Reject'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')
    
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
    kepemilikan = fields.Selection([
                            ('bumn',   'BUMN'),
                            ('individu', 'INDIVIDU'),
                            ('bumd',  'BUMD'),
                            ('kud',  'KUD'),
                            ('pma',  'PMA'),
                        ], string='Kepemilikan', index=True, readonly=True, related="reference.kepemilikan")
    
    sertifikasi_baru = fields.Boolean(string='Sertifikasi Awal/Baru', related="reference.sertifikasi_baru")
    re_sertifikasi = fields.Boolean(string='Re-Sertifikasi', related="reference.re_sertifikasi")
    perluasan = fields.Boolean(string='Perluasan Ruang Lingkup', related="reference.perluasan")
    pengurangan = fields.Boolean(string='Pengurangan Ruang Lingkup', related="reference.pengurangan")
    transfer = fields.Boolean(string='Transfer CB/LS', related="reference.transfer") 

    
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

    add_nama_perusahaan = fields.Char(string='Informasi Konsultan', related="reference.add_nama_perusahaan" )
    add_sertifikasi     = fields.Char(string='Sertifikasi Lain', )
    add_pic             = fields.Char(string='Personal Perusahaan Yang sudah pelatihan Auditor ISPO', )
    add_kendali         = fields.Boolean(string='Tim Kendali Internal', )
    add_kendali_jml     = fields.Integer(string='Tim Kendali Internal Jumlah', )
    add_auditor         = fields.Boolean(string='Auditor ISPO Internal', related="reference.add_auditor" )
    add_auditor_jml     = fields.Integer(string='Auditor Internal Jumlah', )

    ispo_kebun          = fields.One2many('tsi.ispo.kebun', 'reference', string="Kebun", index=True)
    ispo_pabrik         = fields.One2many('tsi.ispo.pabrik', 'reference', string="Pabrik", index=True)
    ispo_pemasok        = fields.One2many('tsi.ispo.pemasok', 'reference', string="Pemasok", index=True)
    ispo_sertifikat     = fields.One2many('tsi.ispo.sertifikat', 'reference', string="Sertifikat", index=True, related="reference.ispo_sertifikat")
    
      
    lines_initial       = fields.One2many('tsi.iso.initial', 'reference_id', string="Lines Initial", index=True, related="reference.lines_initial")
    lines_surveillance  = fields.One2many('tsi.iso.surveillance', 'reference_id', string="Lines SUrveillance", index=True, related="reference.lines_surveillance")
    show_ispo           = fields.Boolean(string='Show ISPO', default=False, related="reference.show_ispo")

    #field auditor
    audit_pt = fields.Boolean(string='Audit Per PT 2 Orang' , related="reference.audit_pt")
    nama_audit_pt = fields.Char(string='Nama Auditor PT', related="reference.nama_audit_pt")
    audit_group = fields.Boolean(string='Audit Per Group 5 Orang' , related="reference.audit_group")
    ics = fields.Boolean(string='ICS untuk Plasma/Swadaya', related="reference.ics")
    nama_ics = fields.Char(string='Nama Auditor PT', related="reference.nama_ics") 
    tgl_perkiraan_mulai = fields.Date(string="Estimated Audit Start Date")
    tgl_perkiraan_selesai = fields.Date(string="Estimated Audit Date End",store=True)

    def action_create_kontrak(self):
        # Cari record sale.order berdasarkan partner_id
        sale_order = self.env['sale.order'].search([('partner_id', '=', self.customer.id)], limit=1)  # Perbaikan di sini
        
        if not sale_order:
            raise UserError("Tidak ditemukan sale order untuk partner ini.")
        
        # Cari dokumen dari tsi.iso.review yang terkait dengan customer
        reviews = self.env['tsi.ispo.review'].search([('customer', '=', self.customer.id)])
        
        if not reviews:
            raise UserError("Tidak ditemukan dokumen ISO Review untuk partner ini.")
        
        # Update state menjadi 'sent'
        sale_order.write({
            'state': 'sent',
            'application_review_ispo_ids': [(6, 0, reviews.ids)],  # Menambahkan dokumen ke field Many2many
        })

        # Opsional: Tampilkan pesan sukses
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': f"State untuk Sale Order '{sale_order.name}' berhasil diubah menjadi 'Sent' dan dokumen review ditambahkan.",
                'type': 'success',
                'sticky': False,
            },
        }
    

    @api.onchange('show_integreted_yes', 'show_integreted_no')
    def onchange_show_integrated(self):
        if self.integrated_audit == 'YES' and not self.show_integreted_yes:
            self.integrated_audit = False
        elif self.integrated_audit == 'NO' and not self.show_integreted_no:
            self.integrated_audit = False

    @api.onchange('integrated_audit')
    def onchange_integrated_audit(self):
        if self.integrated_audit == 'YES':
            self.show_integreted_yes = True
            self.show_integreted_no = False
        elif self.integrated_audit == 'NO':
            self.show_integreted_yes = False
            self.show_integreted_no = True 

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :
                obj.show_14001 = False
                obj.show_45001 = False
                obj.show_27001 = False
                obj.show_haccp = False
                obj.show_22000 = False  
                obj.show_ispo = False               
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
                    if standard.name == 'ISPO' :
                        if obj.show_ispo != True :
                            obj.show_ispo = False
                        obj.show_ispo = True
                    elif standard.name == 'ISO 9001' :
                        obj.show_salesinfo = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.ispo.review')
        vals['name'] = sequence or _('New')
        result = super(ISPOReview, self).create(vals)
        return result

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_quotation_ispo',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_quotation_ispo_view').id,
            'target': 'new'
        }

    # def set_to_running(self):
    #     self.write({'state': 'approved'})            
    #     return return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'iso_review',
    #         'view_id': self.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
    #         'target': [(self.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
    #     }
    
    def set_to_running(self):
        for record in self:
            record.state = 'approved'
            record.finish_date = fields.Datetime.now()
            self.ensure_one()
            action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_isporeview_action')
            action.update({
                'context': {'default_customer': self.customer.id},
                'view_mode': 'form',
                'view_id': self.env.ref('v15_tsi.tsi_ispo_review_view_tree').id,
                'target': [(self.env.ref('v15_tsi.tsi_ispo_review_view_tree').id, 'tree')],
            })
        return action

    def set_to_reject(self):
        self.write({'state': 'reject'})

        self.reference.state = 'reject'
        for review in self:
            # Update message_follower_ids and message_ids to tsi.iso
            self.env['tsi.iso'].sudo().write({
                'message_follower_ids': [(4, review.id)],  # Add followers from this review
                'message_ids': [(4, msg.id) for msg in review.message_ids],  # Add messages from this review
            })            
        return True

    def set_to_revice(self):
        self.write({'state': 'revice'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_isporeview_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_ispo_review_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_ispo_review_view_tree').id, 'tree')],
        })
        return action

    def create_open_quotation(self):
        self.env['sale.order'].create({
            'iso_reference' : self.reference.id,
            'partner_id' : self.customer.id,
        })
        self.reference.compute_state()


    def set_to_closed(self):
        self.create_open_quotation()
        self.write({'state': 'approved'})
        self.write({'finish_date': fields.Datetime.now()})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

class TSIISOReviewSalesInfoSite(models.Model):
    _name = 'tsi.iso.review.salesinfo_site'
    _description = 'TSI ISO Review Sales Info Site'

    review_id = fields.Many2one('tsi.iso.review', string='Review')
    review_id1    = fields.Many2one('tsi.iso.review', string='Review')
    review_id2   = fields.Many2one('tsi.iso.review', string='Review')
    review_id3    = fields.Many2one('tsi.iso.review', string='Review')
    review_id4    = fields.Many2one('tsi.iso.review', string='Review')
    review_id5    = fields.Many2one('tsi.iso.review', string='Review')
    nama_site = fields.Char(string='Name Site')
    stage_1 = fields.Char(string='Stage 1')
    stage_2 = fields.Char(string='Stage 2')
    surveilance_1 = fields.Char(string='Survillance 1')
    surveilance_2 = fields.Char(string='Survillance 2')
    recertification = fields.Char(string='Recertification')
    remarks = fields.Char(string='Remarks')

class TSIISOReviewSalesInfoSite(models.Model):
    _name = 'tsi.iso.review.additional_27001'
    _description = 'TSI ISO Review Additional 27001'

    review_id = fields.Many2one('tsi.iso.review', string='Review')
    nama_site       = fields.Char(string='Nama Site')
    employee        = fields.Char(string='Emp Included')
    it_aspect       = fields.Selection(string='Information Security', selection=[
                            ('identical',   'Mostly Identical'), 
                            ('extenct',     'Only to some extent identical'), 
                            ('differenct',  'Different'), 
                            ])
    it_explanation     = fields.Char(string='IT Explanation')
    isms_aspect     = fields.Selection(string='ISMS as sites', selection=[
                            ('identical',   'Identical, centrally managed'), 
                            ('differs',     'Differs in some respects'), 
                            ('separately',  'Managed separately'), 
                            ])
    isms_explanation     = fields.Char(string='ISMS Explanation')
    special         = fields.Char(string='Special Feature')

class TSIISOReviewSalesInfoSite(models.Model):
    _name = 'tsi.iso.review.site'
    _description = 'TSI ISO Review Site'

    review_id = fields.Many2one('tsi.iso.review', string='Review')
    nama_site       = fields.Char(string='Nama Site')
    type            = fields.Char(string='Type(HO, Factory etc)' )
    address         = fields.Char(string='Address')
    product         = fields.Char(string='Product / Process / Activities')
    # off_location    = fields.Char(string='Off-location')
    total_active    = fields.Char(string='Total No. of Active Temporary Project Sites (see attachment for detai)')
    total_emp       = fields.Char(string='Total No. of Employeesption')
    # part_time       = fields.Char(string='Part-time (4 hours / day)')
    subcon          = fields.Char(string='Subcontractor')
    other           = fields.Char(string='Others')
    remarks         = fields.Char(string='Remark')
    # unskilled       = fields.Char(string='Unskilled Temporary')
    # seasonal        = fields.Char(string='Seasonal Workers')
    non_shift       = fields.Char(string='Non shift')
    shift1          = fields.Char(string='Shift 1')
    shift2          = fields.Char(string='Shift 2')
    shift3          = fields.Char(string='Shift 3')
    differs         = fields.Char(string='Process Differs Across All Shifts')

class ISOReviewHACCP22000(models.Model):
    _name           = 'tsi.iso.review.additional_haccp'
    _description    = 'HACCP 22000'

    review_id        = fields.Many2one('tsi.iso.review', string="Reference")
    hazard_number       = fields.Char(string='Number of hazard')
    hazard_describe     = fields.Char(string='Describe Hazard')
    process_number      = fields.Char(string='Number of process')
    process_describe    = fields.Char(string='Describe Process')
    tech_number         = fields.Char(string='Number of technology')
    tech_describe       = fields.Char(string='Describe Technology')


class APPMandays(models.Model):
    _name           = 'tsi.iso.mandays_app'
    _description    = 'Mandays'

    reference_id    = fields.Many2one('tsi.iso', string="Reference", ondelete='cascade', index=True)
    tahapan_id      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id1      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id2      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id3      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id4      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id_re      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    standard        = fields.Many2one('tsi.iso.standard', string="Standard")
    risk            = fields.Many2one('tsi.iso.risk', string="Risk Category")
    mandays         = fields.Integer(string='Mandays')
    mandays_s1       = fields.Integer(string='Mandays')
    mandays_s2         = fields.Integer(string='Mandays')
    mandays_s3         = fields.Integer(string='Mandays')
    mandays_s4         = fields.Integer(string='Mandays')
    mandays_rs         = fields.Integer(string='Mandays')
    #initial
    nomor_ia    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat     = fields.Date(string="Expiry Date")
    tanggal_sertifikat1     = fields.Date(string="Initial Certification Date")
    tanggal_sertifikat2     = fields.Date(string="Certification Issue Date")
    tanggal_sertifikat3     = fields.Date(string="Certification Validity Date")
    #s1
    nomor_s1    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s1     = fields.Date(string="Expiry Date")
    initial_sertifikat_s_2     = fields.Date(string="Initial Certification Date")
    issue_sertifikat_s_3     = fields.Date(string="Certification Issue Date")
    validity_sertifikat_s_4     = fields.Date(string="Certification Validity Date")
    #s2
    nomor_s2    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s2     = fields.Date(string="Expiry Date")
    tanggal_sertifikat_initial_s2     = fields.Date(string="Initial Certification Date")
    tanggal_sertifikat_issued_s2     = fields.Date(string="Certification Issue Date")
    tanggal_sertifikat_validty_s2     = fields.Date(string="Certification Validity Date")
    #s3
    nomor_s3    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s3     = fields.Date(string="Expiry Date")
    initial_tanggal_sertifikat_s3     = fields.Date(string="Initial Certification Date")
    issued_tanggal_sertifikat_s3     = fields.Date(string="Certification Issue Date")
    validty_tanggal_sertifikat_s3     = fields.Date(string="Certification Validity Date")
    #s4
    nomor_s4    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s4     = fields.Date(string="Expiry Date")
    initiall_s4     = fields.Date(string="Initial Certification Date")
    issued_s4     = fields.Date(string="Certification Issue Date")
    validity_s4     = fields.Date(string="Certification Validity Date")
    #re
    nomor_re    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_rs     = fields.Date(string="Expiry Date")
    tanggal_sertifikat_initial_rs     = fields.Date(string="Initial Certification Date")
    tanggal_sertifikat__issued_rs     = fields.Date(string="Certification Issue Date")
    tanggal_sertifikat_validty_rs     = fields.Date(string="Certification Validity Date")
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', )
    audit_stage     = fields.Selection([
                            ('initial',     'Initial Audit'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                        ], string='Audit Stage', copy=False, index=True)
    accreditation   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    
    @api.onchange('tanggal_sertifikat1')
    def _onchange_tanggal_sertifikat1(self):
        for record in self:
            if record.tanggal_sertifikat1:
                # Set issue_date to initial_date
                record.tanggal_sertifikat2 = record.tanggal_sertifikat1
                
                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.tanggal_sertifikat1, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.tanggal_sertifikat3 = validity_datetime.date()
                
                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat = expiry_datetime.date()

    @api.onchange('initial_sertifikat_s_2')
    def _onchange_initial_sertifikat_s_2(self):
        for record in self:
            if record.initial_sertifikat_s_2:
                # Set issue_date to initial_date
                record.issue_sertifikat_s_3 = record.initial_sertifikat_s_2

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initial_sertifikat_s_2, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validity_sertifikat_s_4 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s1 = expiry_datetime.date()

    @api.onchange('tanggal_sertifikat_initial_s2')
    def _onchange_tanggal_sertifikat_initial_s2(self):
        for record in self:
            if record.tanggal_sertifikat_initial_s2:
                # Set issue_date to initial_date
                record.tanggal_sertifikat_issued_s2 = record.tanggal_sertifikat_initial_s2

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.tanggal_sertifikat_initial_s2, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.tanggal_sertifikat_validty_s2 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s2 = expiry_datetime.date()
    
    @api.onchange('initial_tanggal_sertifikat_s3')
    def _onchange_initial_tanggal_sertifikat_s3(self):
        for record in self:
            if record.initial_tanggal_sertifikat_s3:
                # Set issue_date to initial_date
                record.issued_tanggal_sertifikat_s3 = record.initial_tanggal_sertifikat_s3

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initial_tanggal_sertifikat_s3, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validty_tanggal_sertifikat_s3 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s3 = expiry_datetime.date()

    @api.onchange('initiall_s4')
    def _onchange_initiall_s4(self):
        for record in self:
            if record.initiall_s4:
                # Set issue_date to initial_date
                record.issued_s4 = record.initiall_s4

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initiall_s4, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validity_s4 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s4 = expiry_datetime.date()
    
    @api.onchange('tanggal_sertifikat_initial_rs')
    def _onchange_tanggal_sertifikat_initial_rs(self):
        for record in self:
            if record.tanggal_sertifikat_initial_rs:
                # Set issue_date to initial_date
                record.tanggal_sertifikat__issued_rs = record.tanggal_sertifikat_initial_rs

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.tanggal_sertifikat_initial_rs, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.tanggal_sertifikat_validty_rs = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_rs = expiry_datetime.date()


class APPMandaysPA(models.Model):
    _name           = 'tsi.iso.mandays.pa_app'
    _description    = 'Mandays PA'

    reference_id    = fields.Many2one('tsi.iso', string="Reference", ondelete='cascade', index=True)
    standard        = fields.Many2one('tsi.iso.standard', string='Standard ISO')
    audit_stage     = fields.Selection([
                            ('stage_1',     'Stage 1'),
                            ('stage_2',     'Stage 2'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                            ('recert',      'ReCertification'),
                        ], string='Audit Stage', copy=False, index=True)
    aspect          = fields.Char(string='Significant Aspect')
    personnel       = fields.Many2one('hr.employee', string="Personnel")
    task            = fields.Selection([
                            ('lead',        'Lead Auditor'),
                            ('auditor',     'Auditor'),
                            ('technica;',   'Technical Expert'),
                            ('report',      'Reviewing Audit Report'),
                            ('decision',    'Certification Decision'),
                        ], string='Task', copy=False, index=True)
    remarks         = fields.Char(string='Remarks')


class ISOMandaysJustification(models.Model):
    _name           = 'tsi.iso.mandays.justification_app'
    _description    = 'Mandays Justification'

    reference_id    = fields.Many2one('tsi.iso', string="Reference", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    score_qms       = fields.Integer(string='QMS')
    score_ems       = fields.Integer(string='EMS')
    score_ohs       = fields.Integer(string='OHS')
    score_abms      = fields.Integer(string='ABMS')


class ISOMandays(models.Model):
    _name           = 'tsi.iso.mandays'
    _description    = 'Mandays'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    standard        = fields.Many2one('tsi.iso.standard', string="Standard")
    risk            = fields.Many2one('tsi.iso.risk', string="Risk Category")
    mandays         = fields.Integer(string='Mandays')
    audit_stage     = fields.Selection([
                            ('initial',     'Initial Audit'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                        ], string='Audit Stage', copy=False, index=True)

    
class ISOMandaysISMS(models.Model):
    _name           = 'tsi.iso.mandays.isms'
    _description    = 'Mandays ISMS'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    buss_complexity = fields.Char(string='Business Complexity')
    it_complexity   = fields.Char(string='IT Complexity')
    mandays         = fields.Integer(string='Mandays')
    

class ISOMandaysIntegrated(models.Model):
    _name           = 'tsi.iso.mandays.integrated'
    _description    = 'Mandays Interated'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    mandays         = fields.Integer(string='Mandays')
    
class ISOMandaysAuditTime(models.Model):
    _name           = 'tsi.iso.mandays.audit_time'
    _description    = 'Mandays Audit Time'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    pivot           = fields.Integer(string='Pivot')
    initial         = fields.Integer(string='Initial Audit')
    surveillance    = fields.Integer(string='Surveillance')
    recert          = fields.Integer(string='Recert')

class ISOMandaysJustification(models.Model):
    _name           = 'tsi.iso.mandays.justification'
    _description    = 'Mandays Justification'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    score_qms       = fields.Integer(string='QMS')
    score_ems       = fields.Integer(string='EMS')
    score_ohs       = fields.Integer(string='OHS')
    score_abms      = fields.Integer(string='ABMS')

class ISOMandaysJustificationISMS(models.Model):
    _name           = 'tsi.iso.mandays.justification.isms'
    _description    = 'Mandays Justification ISMS'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    score_isms      = fields.Integer(string='ISMS')

class ISOMandaysPA(models.Model):
    _name           = 'tsi.iso.mandays.pa'
    _description    = 'Mandays PA'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    standard        = fields.Many2one('tsi.iso.standard', string='Standard ISO')
    audit_stage     = fields.Selection([
                            ('stage_1',     'Stage 1'),
                            ('stage_2',     'Stage 2'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                            ('recert',      'ReCertification'),
                        ], string='Audit Stage', copy=False, index=True)
    aspect          = fields.Char(string='Significant Aspect')
    personnel       = fields.Many2one('hr.employee', string="Personnel")
    task            = fields.Selection([
                            ('lead',        'Lead Auditor'),
                            ('auditor',     'Auditor'),
                            ('technica;',   'Technical Expert'),
                            ('report',      'Reviewing Audit Report'),
                            ('decision',    'Certification Decision'),
                        ], string='Task', copy=False, index=True)
    remarks         = fields.Char(string='Remarks')


class ISPOEvaluasi(models.Model):
    _name           = "tsi.ispo.evaluasi"
    _description    = "Evaluasi Isu"

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    issue           = fields.Char(string='Issue')
    evaluasi        = fields.Char(string='Hasil Evaluasi')
    rekomendasi     = fields.Char(string='Rekomendasi')

class ISPONilaiSkor(models.Model):
    _name           = "tsi.ispo.nilai_skor"
    _description    = "Nilai Skor"

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    skor_name       = fields.Char(string='Skor')
    skor_1          = fields.Char(string='Skor = 1')
    skor_2          = fields.Char(string='Skor = 2')
    skor_3          = fields.Char(string='Skor = 3')
    skor_nilai      = fields.Integer(string='Nilai Skor')

class ISPOJustification(models.Model):
    _name           = 'tsi.ispo.justification'
    _description    = 'ISPO Mandays Justification'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Parameter')
    standar         = fields.Integer(string='Standar')
    maksimal        = fields.Integer(string='Maksimal')
    score           = fields.Integer(string='Score')

class ISPOMandays(models.Model):
    _name           = 'tsi.ispo.mandays'
    _description    = 'ISPO Mandays'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    lingkup         = fields.Char(string='Ruang Lingkup')
    awal            = fields.Integer(string='Sertifikasi Awal')
    penilikan       = fields.Integer(string='Penilikan')
    resertifikai    = fields.Integer(string='Resertifikasi')

class ISPOTotalMandays(models.Model):
    _name           = 'tsi.ispo.total_mandays'
    _description    = 'ISPO Total Mandays'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    lingkup         = fields.Selection([
                            ('audit_1',        'Audit Tahap 1'),
                            ('audit_2',     'Audit Tahap 2'),
                            ('penilikan',   'Penilikan'),
                            ('resertifikasi',      'Resertifikasi'),
                        ], string='Ruang Lingkup', copy=False, index=True)
    kebun           = fields.Integer(string='Kebun')
    pabrik          = fields.Integer(string='Pabrik')
