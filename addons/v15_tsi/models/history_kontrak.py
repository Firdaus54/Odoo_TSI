from odoo import models, fields, api
from datetime import datetime, timedelta

class HistoryKontrak(models.Model):
    _name           = "tsi.history_kontrak"
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = "History Kontrak"
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    # nama_klien          = fields.Char(string='Nama Klien')
    partner_id          = fields.Many2one('res.partner', string="Nama Klien", domain="[('is_company', '=', True)]")
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    tanggal_kontrak     = fields.Date(string="Tanggal Kontrak")
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', )
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', )
    # nilai_kontrak       = fields.Char(string='Nilai Kontrak')
    level               = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Kategori', index=True, related="partner_id.kategori")
    segment             = fields.Many2many('res.partner.category', string='Segment', related="partner_id.category_id")
    ea_code_ids = fields.Many2many('tsi.ea_code', string="EA Codes", related="partner_id.ea_code_ids")
    scope           = fields.Char('Scope', related="partner_id.scope") 
    # akreditasi_ids      = fields.Many2many('tsi.iso.accreditation', string='Akreditasi', )
    pic                 = fields.Char(string='PIC')
    sales               = fields.Many2one('res.users', string='Sales Person', related="partner_id.user_id")
    associate           = fields.Many2one('res.partner', string="Associate", related="partner_id.associate_lines.associate_id")
    status_tahun_aktif  = fields.Char(string='Status Tahun AKtif')
    show_tahapan      = fields.Boolean(string='Additional Info', default=False)
    show_initial        = fields.Boolean(string='Show Initial', default=False)
    show_survilance1    = fields.Boolean(string='Show Survilance 1', default=False)
    show_survilance2    = fields.Boolean(string='Show Survilance 2', default=False)
    show_survilance3    = fields.Boolean(string='Show Survilance 3', default=False)
    show_survilance4    = fields.Boolean(string='Show Survilance 4', default=False)
    show_recertification = fields.Boolean(string='Show Recertification', default=False)
    tahapan_ori_lines   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id', string="Lines1 ", index=True)
    tahapan_ori_lines1   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id1', string="Lines2 ", index=True)
    tahapan_ori_lines2   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id2', string="Lines3 ", index=True)
    tahapan_ori_lines3   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id3', string="Lines4", index=True)
    tahapan_ori_lines4   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id4', string="Lines5 ", index=True)
    tahapan_ori_lines_re   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id_re', string="Lines6 ", index=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Nama Klien",
        change_default=True, index=True,
        tracking=1,
        domain="[('company_id', 'in', (False, company_id))]")
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True,
        precompute=True,
        ondelete='restrict')
    amount_total = fields.Monetary(string="Initial Audit", store=True, compute='_compute_amounts', tracking=4)
    amount_total_s1 = fields.Monetary(string="Surveillance 1", store=True, compute='_compute_amounts_s1', tracking=4)
    amount_total_s2 = fields.Monetary(string="Surveillance 2", store=True, compute='_compute_amounts_s2', tracking=4)
    amount_total_s3 = fields.Monetary(string="Surveillance 3", store=True, compute='_compute_amounts_s3', tracking=4)
    amount_total_s4 = fields.Monetary(string="Surveillance 4", store=True, compute='_compute_amounts_s4', tracking=4)
    amount_total_re = fields.Monetary(string="Recertification 1", store=True, compute='_compute_amounts_re', tracking=4)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    state           =fields.Selection([
                            ('draft', 'Draft'),
                            ('approve', 'Approve'),
                            ('reject', 'Reject'),
                            ('lanjut', 'Lanjut'),
                            ('lost','Loss'),
                            ('suspend', 'Suspend'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    state_klien           =fields.Selection([
                            ('draft', 'Draft'),
                            ('approve', 'Approve'),
                            ('reject', 'Reject'),
                            ('New', 'New'),
                            ('active', 'Active'),
                            ('lanjut', 'Lanjut'),
                            ('lost','Loss'),
                            ('suspend', 'Suspend'),
                            ('Re-Active', 'Re-Active'),
                            ('Double', 'Double'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, related="partner_id.status_klien")
    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True)

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

    def create_audits(self):
        return {
            'name': "Create Audit",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_view').id,
            'target': 'new'
        }
    
    def create_audit(self):

        nama_client = self.partner_id.id
        iso_standard_ids = self.iso_standard_ids
        iso_reference = self.iso_reference
        sales_reference = self.sales_reference
        review_reference = self.review_reference

        line_items = []
        audit_stage = ''  

        if self.tahapan_ori_lines1:
            audit_stage = 'surveilance1'
            for tahapan_ori_line in self.tahapan_ori_lines1:
                standard_name = tahapan_ori_line.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s1_value = tahapan_ori_line.mandays_s1

                try:
                    mandays_s1_float = float(mandays_s1_value)
                except (ValueError, TypeError) as e:
                    mandays_s1_float = 0.0 
                
                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s1_float,
                    'audit_tahapan': 'Surveillance 1',
                }))

        if self.tahapan_ori_lines2:
            audit_stage = 'surveilance2'
            for tahapan_ori_line2 in self.tahapan_ori_lines2:
                standard_name = tahapan_ori_line2.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s2_value = tahapan_ori_line2.mandays_s2

                try:
                    mandays_s2_float = float(mandays_s2_value)
                except (ValueError, TypeError) as e:
                    mandays_s2_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s2_float,
                    'audit_tahapan': 'Surveillance 2',
                }))

        if self.tahapan_ori_lines_re:
            audit_stage = 'recertification'
            for tahapan_ori_line_re in self.tahapan_ori_lines_re:
                standard_name = tahapan_ori_line_re.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_re_value = tahapan_ori_line_re.mandays_rs

                try:
                    mandays_re_float = float(mandays_re_value)
                except (ValueError, TypeError) as e:
                    mandays_re_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_re_float,
                    'audit_tahapan': 'Recertification',
                }))

        wizard_audit = self.env['tsi.wizard_audit'].create({ 
            'partner_id': nama_client,
            'iso_standard_ids': iso_standard_ids,
            'iso_reference': self.iso_reference.id,  
            'sales_reference': self.sales_reference.id,
            'review_reference': [(6, 0, self.review_reference.ids)],
            'line_ids': line_items,
            'audit_stage': audit_stage,
        })

        wizard_audit._onchange_partner_id()

        return {
            'name': "Create Audit",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit',
            'res_id': wizard_audit.id,
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_view').id,
            'target': 'new'
        }

    def action_create_partner_certificate(self):
        for history in self:
            # Get the partner
            partner = history.partner_id
            
            # Fetch mandays lines with the relevant dates
            mandays_lines = (
                history.tahapan_ori_lines + 
                history.tahapan_ori_lines1 + 
                history.tahapan_ori_lines2 + 
                history.tahapan_ori_lines3 + 
                history.tahapan_ori_lines4 + 
                history.tahapan_ori_lines_re
            )
            
            # Prepare data for partner certificates
            certificate_data = []
            tahun_masuk_entries = {}  # Track tahun_masuk entries by iso_standard_ids
            
            for line in mandays_lines:
                # Determine the certificate type and corresponding dates
                cert_type = None
                cert_dates = {}

                if line.tahapan_id:
                    cert_type = 'initial audit'
                    cert_dates = {
                        'no_sertifikat': line.nomor_ia,
                        'expiry_date': line.tanggal_sertifikat,
                        'initial_date': line.tanggal_sertifikat1,
                        'issue_date': line.tanggal_sertifikat2,
                        'validity_date': line.tanggal_sertifikat3
                    }
                elif line.tahapan_id1:
                    cert_type = 'Surveillance 1'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s1,
                        'expiry_date': line.tanggal_sertifikat_s1,
                        'initial_date': line.initial_sertifikat_s_2,
                        'issue_date': line.issue_sertifikat_s_3,
                        'validity_date': line.validity_sertifikat_s_4
                    }
                elif line.tahapan_id2:
                    cert_type = 'Surveillance 2'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s2,
                        'expiry_date': line.tanggal_sertifikat_s2,
                        'initial_date': line.tanggal_sertifikat_initial_s2,
                        'issue_date': line.tanggal_sertifikat_issued_s2,
                        'validity_date': line.tanggal_sertifikat_validty_s2
                    }
                elif line.tahapan_id3:
                    cert_type = 'Surveillance 3'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s3,
                        'expiry_date': line.tanggal_sertifikat_s3,
                        'initial_date': line.initial_tanggal_sertifikat_s3,
                        'issue_date': line.issued_tanggal_sertifikat_s3,
                        'validity_date': line.validty_tanggal_sertifikat_s3
                    }
                elif line.tahapan_id4:
                    cert_type = 'Surveillance 4'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s4,
                        'expiry_date': line.tanggal_sertifikat_s4,
                        'initial_date': line.initiall_s4,
                        'issue_date': line.issued_s4,
                        'validity_date': line.validity_s4
                    }
                elif line.tahapan_id_re:
                    cert_type = 'Recertification'
                    cert_dates = {
                        'no_sertifikat': line.nomor_re,
                        'expiry_date': line.tanggal_sertifikat_rs,
                        'initial_date': line.tanggal_sertifikat_initial_rs,
                        'issue_date': line.tanggal_sertifikat__issued_rs,
                        'validity_date': line.tanggal_sertifikat_validty_rs
                    }

                if cert_type:
                    # Handle certificates
                    existing_certificates = self.env['tsi.partner.certificate'].search([
                        ('partner_id', '=', partner.id),
                        ('tahapan_audit', '=', cert_type)
                    ])
                    
                    # Prepare data for certificate_data
                    certificate_entry = {
                        'partner_id': partner.id,
                        'no_sertifikat': cert_dates.get('no_sertifikat'),
                        'initial_date': cert_dates.get('initial_date'),
                        'issue_date': cert_dates.get('issue_date'),
                        'validity_date': cert_dates.get('validity_date'),
                        'expiry_date': cert_dates.get('expiry_date'),
                        'tahapan_audit': cert_type
                    }

                    if existing_certificates:
                        existing_certificates.write(certificate_entry)
                    else:
                        certificate_data.append(certificate_entry)

                    # Prepare data for tahun_masuk
                    issue_year = cert_dates.get('issue_date').year if cert_dates.get('issue_date') else None
                    tahun_masuk_entry = {
                        'partner_id': partner.id,
                        'iso_standard_ids': [(6, 0, line.standard.ids)],  # Adjust this if the relationship is different
                        'issue_date': cert_dates.get('issue_date'),
                        'certification_year': issue_year if issue_year else '',
                    }
                    iso_standard_ids_tuple = tuple(line.standard.ids)  # Convert list to tuple
                    # Add or update entry in tahun_masuk_entries
                    if iso_standard_ids_tuple in tahun_masuk_entries:
                        tahun_masuk_entries[iso_standard_ids_tuple].append(tahun_masuk_entry)
                    else:
                        tahun_masuk_entries[iso_standard_ids_tuple] = [tahun_masuk_entry]
            
            # Delete old partner certificates
            self.env['tsi.partner.certificate'].search([
                ('partner_id', '=', partner.id)
            ]).unlink()
            
            # Create or update partner certificates
            if certificate_data:
                self.env['tsi.partner.certificate'].create(certificate_data)
            
            # Delete old tahun_masuk entries
            self.env['tsi.tahun_masuk'].search([
                ('partner_id', '=', partner.id)
            ]).unlink()
            
            # Add new tahun_masuk entries
            if tahun_masuk_entries:
                for entries in tahun_masuk_entries.values():
                    for entry in entries:
                        self.env['tsi.tahun_masuk'].create(entry)
        
        return True


    def action_approve(self):
        self.write({'state': 'approve'})          
        return True
    
    def action_reject(self):
        self.write({'state': 'reject'})          
        return True
    
    #action Loss
    def action_loss(self):
        for history in self:
            # Cari atau buat catatan tsi.crm.loss berdasarkan partner_id
            loss_record = self.env['tsi.crm.loss'].search([('partner_id', '=', history.partner_id.id)], limit=1)
            if not loss_record:
                loss_record = self.env['tsi.crm.loss'].create({
                    'partner_id': history.partner_id.id,
                    'contract_number': history.no_kontrak,
                    'contract_date': history.tanggal_kontrak,
                    'sales': history.sales.id,
                    'segment': [(6, 0, history.segment.ids)],
                    'iso_standard_ids': [(6, 0, history.iso_standard_ids.ids)] if history.iso_standard_ids else False,
                })

            # Clear existing crm_accreditation lines
            loss_record.crm_accreditations.unlink()

            # Update tahapan_audit based on the lines
            lines = []
            if history.show_initial and history.tahapan_ori_lines:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines, 'initial audit')
            if history.show_survilance1 and history.tahapan_ori_lines1:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines1, 'Surveillance 1')
            if history.show_survilance2 and history.tahapan_ori_lines2:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines2, 'Surveillance 2')
            if history.show_survilance3 and history.tahapan_ori_lines3:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines3, 'Surveillance 3')
            if history.show_survilance4 and history.tahapan_ori_lines4:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines4, 'Surveillance 4')
            if history.show_recertification and history.tahapan_ori_lines_re:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines_re, 'Recertification')

            # Update tahapan_audit with the correct value
            if lines:
                loss_record.write({'crm_accreditations': [(0, 0, line) for line in lines]})

            # Set state to 'loss' on history kontrak
            history.write({'state': 'lost'})

    def _prepare_loss_lines(self, tahapan_lines, tahapan_name):
        lines = []
        if tahapan_lines:
            for line in tahapan_lines:
                line_values = {
                    'accreditation': line.accreditation.id if line.accreditation else False,
                    'tahapan_audit': tahapan_name,
                    'iso_standard_ids': [(6, 0, line.standard.ids)] if line.standard else False,
                    'nilai_ia': False,  # Default value
                }
                # Set nilai_ia based on tahapan_name
                if tahapan_name == 'initial audit':
                    line_values['nilai_ia'] = line.mandays
                elif tahapan_name == 'Surveillance 1':
                    line_values['nilai_ia'] = line.mandays_s1
                elif tahapan_name == 'Surveillance 2':
                    line_values['nilai_ia'] = line.mandays_s2
                elif tahapan_name == 'Surveillance 3':
                    line_values['nilai_ia'] = line.mandays_s3
                elif tahapan_name == 'Surveillance 4':
                    line_values['nilai_ia'] = line.mandays_s4
                elif tahapan_name == 'Recertification':
                    line_values['nilai_ia'] = line.mandays_rs

                lines.append(line_values)
        return lines
    
    #Action Suspen
    def action_suspend(self):
        for history in self:
            # Cari atau buat catatan tsi.crm.loss berdasarkan partner_id
            loss_record = self.env['tsi.crm.suspen'].search([('partner_id', '=', history.partner_id.id)], limit=1)
            if not loss_record:
                loss_record = self.env['tsi.crm.suspen'].create({
                    'partner_id': history.partner_id.id,
                    'contract_number': history.no_kontrak,
                    'contract_date': history.tanggal_kontrak,
                    'sales': history.sales.id,
                    'segment': [(6, 0, history.segment.ids)],
                    'iso_standard_ids': [(6, 0, history.iso_standard_ids.ids)] if history.iso_standard_ids else False,
                })

            # Clear existing crm_accreditation lines
            loss_record.crm_accreditations.unlink()

            # Update tahapan_audit based on the lines
            lines = []
            if history.show_initial and history.tahapan_ori_lines:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines, 'initial audit')
            if history.show_survilance1 and history.tahapan_ori_lines1:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines1, 'Surveillance 1')
            if history.show_survilance2 and history.tahapan_ori_lines2:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines2, 'Surveillance 2')
            if history.show_survilance3 and history.tahapan_ori_lines3:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines3, 'Surveillance 3')
            if history.show_survilance4 and history.tahapan_ori_lines4:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines4, 'Surveillance 4')
            if history.show_recertification and history.tahapan_ori_lines_re:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines_re, 'Recertification')

            # Update tahapan_audit with the correct value
            if lines:
                loss_record.write({'crm_accreditations': [(0, 0, line) for line in lines]})

            # Set state to 'loss' on history kontrak
            history.write({'state': 'suspend'})

    def _prepare_loss_lines(self, tahapan_lines, tahapan_name):
        lines = []
        if tahapan_lines:
            for line in tahapan_lines:
                line_values = {
                    'accreditation': line.accreditation.id if line.accreditation else False,
                    'tahapan_audit': tahapan_name,
                    'iso_standard_ids': [(6, 0, line.standard.ids)] if line.standard else False,
                    'nilai_ia': False,  # Default value
                }
                # Set nilai_ia based on tahapan_name
                if tahapan_name == 'initial audit':
                    line_values['nilai_ia'] = line.mandays
                elif tahapan_name == 'Surveillance 1':
                    line_values['nilai_ia'] = line.mandays_s1
                elif tahapan_name == 'Surveillance 2':
                    line_values['nilai_ia'] = line.mandays_s2
                elif tahapan_name == 'Surveillance 3':
                    line_values['nilai_ia'] = line.mandays_s3
                elif tahapan_name == 'Surveillance 4':
                    line_values['nilai_ia'] = line.mandays_s4
                elif tahapan_name == 'Recertification':
                    line_values['nilai_ia'] = line.mandays_rs

                lines.append(line_values)
        return lines
    
    #Action Suspen
    def action_go_to_tsi_crm(self):
        for history in self:
            # Cari atau buat catatan tsi.crm.loss berdasarkan partner_id
            loss_record = self.env['tsi.crm.lanjut'].search([('partner_id', '=', history.partner_id.id)], limit=1)
            if not loss_record:
                loss_record = self.env['tsi.crm.lanjut'].create({
                    'partner_id': history.partner_id.id,
                    'contract_number': history.no_kontrak,
                    'contract_date': history.tanggal_kontrak,
                    'sales': history.sales.id,
                    'segment': [(6, 0, history.segment.ids)],
                    'iso_standard_ids': [(6, 0, history.iso_standard_ids.ids)] if history.iso_standard_ids else False,
                })

            # Clear existing crm_accreditation lines
            loss_record.crm_accreditations.unlink()

            # Update tahapan_audit based on the lines
            lines = []
            if history.show_initial and history.tahapan_ori_lines:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines, 'initial audit')
            if history.show_survilance1 and history.tahapan_ori_lines1:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines1, 'Surveillance 1')
            if history.show_survilance2 and history.tahapan_ori_lines2:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines2, 'Surveillance 2')
            if history.show_survilance3 and history.tahapan_ori_lines3:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines3, 'Surveillance 3')
            if history.show_survilance4 and history.tahapan_ori_lines4:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines4, 'Surveillance 4')
            if history.show_recertification and history.tahapan_ori_lines_re:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines_re, 'Recertification')

            # Update tahapan_audit with the correct value
            if lines:
                loss_record.write({'crm_accreditations': [(0, 0, line) for line in lines]})

            # Set state to 'loss' on history kontrak
            history.write({'state': 'lanjut'})

    def _prepare_loss_lines(self, tahapan_lines, tahapan_name):
        lines = []
        if tahapan_lines:
            for line in tahapan_lines:
                line_values = {
                    'accreditation': line.accreditation.id if line.accreditation else False,
                    'tahapan_audit': tahapan_name,
                    'iso_standard_ids': [(6, 0, line.standard.ids)] if line.standard else False,
                    'nilai_ia': False,  # Default value
                }
                # Set nilai_ia based on tahapan_name
                if tahapan_name == 'initial audit':
                    line_values['nilai_ia'] = line.mandays
                elif tahapan_name == 'Surveillance 1':
                    line_values['nilai_ia'] = line.mandays_s1
                elif tahapan_name == 'Surveillance 2':
                    line_values['nilai_ia'] = line.mandays_s2
                elif tahapan_name == 'Surveillance 3':
                    line_values['nilai_ia'] = line.mandays_s3
                elif tahapan_name == 'Surveillance 4':
                    line_values['nilai_ia'] = line.mandays_s4
                elif tahapan_name == 'Recertification':
                    line_values['nilai_ia'] = line.mandays_rs

                lines.append(line_values)
        return lines

    
    @api.onchange('tahapan_audit_ids')
    def _onchange_tahapan(self):
        for obj in self:
            if obj.tahapan_audit_ids :
                obj.show_initial         = False
                obj.show_survilance1     = False
                obj.show_survilance2     = False
                obj.show_survilance3     = False
                obj.show_survilance4     = False                
                obj.show_recertification = False
                for tahapan in obj.tahapan_audit_ids :
                    if tahapan.name == 'Initial Audit' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_initial = True
                    if tahapan.name == 'Surveillance 1' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance1 = True
                    if tahapan.name == 'Surveillance 2' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance2 = True
                    if tahapan.name == 'Surveillance 3' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance3 = True
                    if tahapan.name == 'Surveillance 4' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance4 = True
                    if tahapan.name == 'Recertification 1' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_recertification = True
                    #else :
                    #    obj.show_salesinfo = True
    
    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        for tahapan in self:
            if tahapan.partner_id:
                tahapan.pricelist_id = False
                continue
            tahapan = tahapan.with_company(tahapan.company_id)
            tahapan.pricelist_id = tahapan.partner_id.property_product_pricelist
    
    @api.depends('pricelist_id', 'company_id')
    def _compute_currency_id(self):
        for tahapan in self:
            tahapan.currency_id = tahapan.pricelist_id.currency_id or tahapan.company_id.currency_id
    
    @api.depends('tahapan_ori_lines.mandays')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            tahapan_ori_lines = tahapan.tahapan_ori_lines.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines.mapped('mandays'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total = tahapan.amount_untaxed

    @api.depends('tahapan_ori_lines1.mandays_s1')
    def _compute_amounts_s1(self):
        """Compute the total amounts of the SO."""
        for tahapans1 in self:
            tahapan_ori_lines1 = tahapans1.tahapan_ori_lines1.filtered(lambda x: not x.display_type)

            if tahapans1.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines1
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans1.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines1.mapped('mandays_s1'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans1.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans1.amount_total_s1 = tahapans1.amount_untaxed

    @api.depends('tahapan_ori_lines2.mandays_s2')
    def _compute_amounts_s2(self):
        """Compute the total amounts of the SO."""
        for tahapans2 in self:
            tahapan_ori_lines2 = tahapans2.tahapan_ori_lines2.filtered(lambda x: not x.display_type)

            if tahapans2.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines2
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans2.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines2.mapped('mandays_s2'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans2.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans2.amount_total_s2 = tahapans2.amount_untaxed

    @api.depends('tahapan_ori_lines3.mandays_s3')
    def _compute_amounts_s3(self):
        """Compute the total amounts of the SO."""
        for tahapans3 in self:
            tahapan_ori_lines3 = tahapans3.tahapan_ori_lines3.filtered(lambda x: not x.display_type)

            if tahapans3.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans3.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines3.mapped('mandays_s3'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans3.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans3.amount_total_s3 = tahapans3.amount_untaxed

    @api.depends('tahapan_ori_lines4.mandays_s4')
    def _compute_amounts_s4(self):
        """Compute the total amounts of the SO."""
        for tahapans4 in self:
            tahapan_ori_lines4 = tahapans4.tahapan_ori_lines4.filtered(lambda x: not x.display_type)

            if tahapans4.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines4
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans4.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines4.mapped('mandays_s4'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans4.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans4.amount_total_s4 = tahapans4.amount_untaxed

    @api.depends('tahapan_ori_lines_re.mandays_rs')
    def _compute_amounts_re(self):
        """Compute the total amounts of the SO."""
        for tahapan_re in self:
            tahapan_ori_lines_re = tahapan_re.tahapan_ori_lines_re.filtered(lambda x: not x.display_type)

            if tahapan_re.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines_re
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan_re.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines_re.mapped('mandays_rs'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan_re.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan_re.amount_total_re = tahapan_re.amount_untaxed


