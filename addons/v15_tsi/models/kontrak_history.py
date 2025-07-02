from odoo import models, fields, api

class KontrakHistory(models.Model):
    _name           = "tsi.kontrak_history"
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = "History Kontrak"
    _order          = 'id DESC'

    nama_klien          = fields.Char(string='Nama Klien')
    # partner_id          = fields.Many2one('res.partner', string="Nama Klien", domain="[('is_company', '=', True)]")
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    tanggal_kontrak     = fields.Date(string="Tanggal Kontrak")
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', )
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', )
    # nilai_kontrak       = fields.Char(string='Nilai Kontrak')
    level               = fields.Char(string='Level')
    segment             = fields.Char(string='Segment')
    # akreditasi_ids      = fields.Many2many('tsi.iso.accreditation', string='Akreditasi', )
    pic                 = fields.Char(string='PIC')
    sales               = fields.Char(string='Sales Person')
    associate           = fields.Char(string='Associate')
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
    amount_total_s1 = fields.Monetary(string="Survilance 1", store=True, compute='_compute_amounts_s1', tracking=4)
    amount_total_s2 = fields.Monetary(string="Survilance 2", store=True, compute='_compute_amounts_s2', tracking=4)
    amount_total_s3 = fields.Monetary(string="Survilance 3", store=True, compute='_compute_amounts_s3', tracking=4)
    amount_total_s4 = fields.Monetary(string="Survilance 4", store=True, compute='_compute_amounts_s4', tracking=4)
    amount_total_re = fields.Monetary(string="Recertification 1", store=True, compute='_compute_amounts_re', tracking=4)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')


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
                    if tahapan.name == 'Survilance 1' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance1 = True
                    if tahapan.name == 'Survilance 2' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance2 = True
                    if tahapan.name == 'Survilance 3' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance3 = True
                    if tahapan.name == 'Survilance 4' :
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
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
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
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
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


