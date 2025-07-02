from odoo import models, fields, api

class PlanFood22000(models.Model):
    _name = 'project.plan.food.22000'
    _description = 'Project Plan Food 22000'
    _order          = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    budget_plan = fields.Integer(string='Budget - Plan')
    budget_actual = fields.Integer(string='Budget - Actual')
    noted = fields.Html('Noted')
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
    amount_percentage = fields.Float(string='Average Percentage', compute='_compute_total_percentage', store=True)
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amount_totals', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amount_totalss', tracking=4)
    project_plan_food_22000    = fields.One2many('tsi.pd.info', 'reference_id', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    state = fields.Selection([
        ('1', 'Pendaftaran Akreditasi'),
        ('2', 'Submit Dokumen Permohonan'),
        ('3', 'Audit Kelayakan'),
        ('4', 'Kaji Ulang Permohonan Asesmen (KUPA)'),
        ('5', 'Pembayaran Biaya Permohonan'),
        ('6', 'Persetujuan Tim dan Kontrak'),
        ('7', 'Audit Kecukupan'),
        ('8', 'Surat Info dan Tagihan Asesmen'),
        ('9', 'Registrasi Pembayaran Asesmen'),
        ('10', 'Surat Tugas Asesmen'),
        ('11', 'Input Tim'),
        ('12', 'Pelaksanaan Asesmen'),
        ('13', 'Tindakan Perbaikan dan Verifikasi Tindakan Perbaikan'),
        ('14', 'Laporan Asesmen'),
        ('15', 'Rekomendasi Ruang Lingkup oleh Asesor'),
        ('16', 'Evaluasi Hasil Asesmen'),
        ('17', 'Rapat Kajian Panitia Teknis'),
        ('18', 'Rapat KAN Council'),
        ('19', 'Surat Keputusan Akreditasi'),
        ('20', 'Penerbitan Sertifikat Akreditasi'),
        ('21', 'Penerbitan Lampiran Akreditasi'),
    ], string='Status', default='1', tracking=True, readonly=True)

    def action_next_step(self):
        for record in self:
            if int(record.status) < 21:
                record.status = str(int(record.status) + 1)

    @api.depends('project_plan_food_22000.percentage', 
             'project_plan_food_22000.plan_food_new.percentage',
             'project_plan_food_22000.plan_food_new.plan_food_new_details.percentage',
             'project_plan_food_22000.plan_food_new.plan_food_new_details.plan_food_new_details1.percentage',
             'project_plan_food_22000.plan_food_new.plan_food_new_details.plan_food_new_details1.plan_food_new_details2.percentage',
             'project_plan_food_22000.plan_food_new.plan_food_new_details.plan_food_new_details1.plan_food_new_details2.plan_food_new_details3.percentage')
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            # Sum percentages from project_plan_food_22000
            for line in record.project_plan_food_22000:
                if line.percentage:
                    total += line.percentage
                # Sum percentages from nested plan_food_new
                for sub_line in line.plan_food_new:
                    if sub_line.percentage:
                        total += sub_line.percentage
                    # Sum percentages from nested plan_food_new_details
                    for sub_sub_line in sub_line.plan_food_new_details:
                        if sub_sub_line.percentage:
                            total += sub_sub_line.percentage
                        # Sum percentages from nested plan_food_new_details1
                        for sub_sub_line1 in sub_sub_line.plan_food_new_details1:
                            if sub_sub_line1.percentage:
                                total += sub_sub_line1.percentage
                            # Sum percentages from nested plan_food_new_details2
                            for sub_sub_line2 in sub_sub_line1.plan_food_new_details2:
                                if sub_sub_line2.percentage:
                                    total += sub_sub_line2.percentage
                                # Sum percentages from nested plan_food_new_details3
                                for sub_sub_line3 in sub_sub_line2.plan_food_new_details3:
                                    if sub_sub_line3.percentage:
                                        total += sub_sub_line3.percentage
            # Assign the total to the amount_percentage field
            record.amount_percentage = total

    @api.depends('percentage')
    def _compute_average_percentage(self):
        # Menghitung total percentage
        total = 0.0
        # Mengiterasi semua record untuk menghitung total percentage
        for record in self:
            total += record.percentage
        
        # Menyimpan hasil ke dalam field `amount_percentage`
        for record in self:
            record.amount_percentage = total

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
    
    @api.depends('project_plan_food_22000.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_food_22000 = tahapan.project_plan_food_22000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_food_22000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_food_22000.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_food_22000.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_food_22000 = tahapan.project_plan_food_22000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_food_22000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_food_22000.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanFoodHACCP(models.Model):
    _name = 'project.plan.food.haccp'
    _description = 'Project Plan Food HACCP'
    _order          = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    budget_plan = fields.Integer(string='Budget - Plan')
    budget_actual = fields.Integer(string='Budget - Actual')
    noted = fields.Html('Noted')
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
    amount_percentage = fields.Float(string='Average Percentage', compute='_compute_average_percentage', store=True)
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amount_totals', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amount_totalss', tracking=4)
    project_plan_food_haccp    = fields.One2many('tsi.pd.info', 'reference_id2', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    @api.depends('project_plan_food_haccp.percentage', 
             'project_plan_food_haccp.plan_food_existing.percentage',
             'project_plan_food_haccp.plan_food_existing.plan_food_existing_details.percentage',
             'project_plan_food_haccp.plan_food_existing.plan_food_existing_details.plan_food_existing_details1.percentage',
             'project_plan_food_haccp.plan_food_existing.plan_food_existing_details.plan_food_existing_details1.plan_food_existing_details2.percentage',
             'project_plan_food_haccp.plan_food_existing.plan_food_existing_details.plan_food_existing_details1.plan_food_existing_details2.plan_food_existing_details3.percentage')
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            # Sum percentages from project_plan_food_haccp
            for line in record.project_plan_food_haccp:
                if line.percentage:
                    total += line.percentage
                # Sum percentages from nested plan_food_existing
                for sub_line in line.plan_food_existing:
                    if sub_line.percentage:
                        total += sub_line.percentage
                    # Sum percentages from nested plan_food_existing_details
                    for sub_sub_line in sub_line.plan_food_existing_details:
                        if sub_sub_line.percentage:
                            total += sub_sub_line.percentage
                        # Sum percentages from nested plan_food_existing_details1
                        for sub_sub_line1 in sub_sub_line.plan_food_existing_details1:
                            if sub_sub_line1.percentage:
                                total += sub_sub_line1.percentage
                            # Sum percentages from nested plan_food_existing_details2
                            for sub_sub_line2 in sub_sub_line1.plan_food_existing_details2:
                                if sub_sub_line2.percentage:
                                    total += sub_sub_line2.percentage
                                # Sum percentages from nested plan_food_existing_details3
                                for sub_sub_line3 in sub_sub_line2.plan_food_existing_details3:
                                    if sub_sub_line3.percentage:
                                        total += sub_sub_line3.percentage
            # Assign the total to the amount_percentage field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_food_haccp.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_food_haccp = tahapan.project_plan_food_haccp.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_food_haccp
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_food_haccp.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_food_haccp.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_food_haccp = tahapan.project_plan_food_haccp.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_food_haccp
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_food_haccp.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanFoodHACCP(models.Model):
    _name = 'project.plan.food'
    _description = 'Project Plan Food HACCP'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    budget_plan = fields.Integer(string='Budget - Plan')
    budget_actual = fields.Integer(string='Budget - Actual')
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
    amount_percentage = fields.Float(string='Average Percentage', compute='_compute_average_percentage', store=True)
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amount_totals', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amount_totalss', tracking=4)
    project_plan_food    = fields.One2many('tsi.pd.info', 'reference_id2', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_food.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_food = tahapan.project_plan_food.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_food
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_food.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_food.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_food = tahapan.project_plan_food.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_food
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_food.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanICT27001(models.Model):
    _name = 'project.plan.ict.27001'
    _description = 'Project Plan ICT 27001'
    _order  = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_ict_27001    = fields.One2many('tsi.pd.info', 'reference_id3', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    @api.depends(
    'project_plan_ict_27001.percentage', 
    'project_plan_ict_27001.plan_ict_new.percentage',
    'project_plan_ict_27001.plan_ict_new.plan_ict_new_details.percentage',
    'project_plan_ict_27001.plan_ict_new.plan_ict_new_details.plan_ict_new_details1.percentage',
    'project_plan_ict_27001.plan_ict_new.plan_ict_new_details.plan_ict_new_details1.plan_ict_new_details2.percentage',
    'project_plan_ict_27001.plan_ict_new.plan_ict_new_details.plan_ict_new_details1.plan_ict_new_details2.plan_ict_new_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_ict_27001`
            for line in record.project_plan_ict_27001:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_ict_new`
                for sub_line in line.plan_ict_new:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_ict_new_details`
                    for detail in sub_line.plan_ict_new_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_ict_new_details1`
                        for detail1 in detail.plan_ict_new_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_ict_new_details2`
                            for detail2 in detail1.plan_ict_new_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_ict_new_details3` (level paling dalam)
                                for detail3 in detail2.plan_ict_new_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total


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
    
    @api.depends('project_plan_ict_27001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_ict_27001 = tahapan.project_plan_ict_27001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_ict_27001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_ict_27001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_ict_27001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_ict_27001 = tahapan.project_plan_ict_27001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_ict_27001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_ict_27001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanICT20000(models.Model):
    _name = 'project.plan.ict.20000'
    _description = 'Project Plan ICT 20000'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_ict_20000    = fields.One2many('tsi.pd.info', 'reference_id4', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    @api.depends(
    'project_plan_ict_20000.percentage', 
    'project_plan_ict_20000.plan_ict_existing.percentage',
    'project_plan_ict_20000.plan_ict_existing.plan_ict_existing_details.percentage',
    'project_plan_ict_20000.plan_ict_existing.plan_ict_existing_details.plan_ict_existing_details1.percentage',
    'project_plan_ict_20000.plan_ict_existing.plan_ict_existing_details.plan_ict_existing_details1.plan_ict_existing_details2.percentage',
    'project_plan_ict_20000.plan_ict_existing.plan_ict_existing_details.plan_ict_existing_details1.plan_ict_existing_details2.plan_ict_existing_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_ict_20000`
            for line in record.project_plan_ict_20000:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_ict_existing`
                for sub_line in line.plan_ict_existing:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_ict_existing_details`
                    for detail in sub_line.plan_ict_existing_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_ict_existing_details1`
                        for detail1 in detail.plan_ict_existing_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_ict_existing_details2`
                            for detail2 in detail1.plan_ict_existing_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_ict_existing_details3` (level paling dalam)
                                for detail3 in detail2.plan_ict_existing_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

    # @api.depends('project_plan_ict_20000.percentage', 'project_plan_ict_20000.plan_ict_existing.percentage')
    # def _compute_total_percentage(self):
    #     for record in self:
    #         total = 0.0
    #         # Sum percentages from `project_plan_ict_20000`
    #         for line in record.project_plan_ict_20000:
    #             if line.percentage:
    #                 total += line.percentage
    #             # Sum percentages from nested `plan_ict_existing`
    #             for sub_line in line.plan_ict_existing:
    #                 if sub_line.percentage:
    #                     total += sub_line.percentage
    #         # Assign the total to the `amount_percentage` field
    #         record.amount_percentage = total

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
    
    @api.depends('project_plan_ict_20000.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_ict_20000 = tahapan.project_plan_ict_20000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_ict_20000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_ict_20000.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_ict_20000.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_ict_20000 = tahapan.project_plan_ict_20000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_ict_20000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_ict_20000.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanICT20000(models.Model):
    _name = 'project.plan.ict'
    _description = 'Project Plan ICT 20000'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_ict    = fields.One2many('tsi.pd.info', 'reference_id4', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_ict.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_ict = tahapan.project_plan_ict.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_ict
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_ict.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_ict.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_ict = tahapan.project_plan_ict.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_ict
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_ict.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanSustainabilityISPO(models.Model):
    _name = 'project.plan.sustainability.ispo'
    _description = 'Project Plan Sustainability ISPO'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_sustainability_ispo    = fields.One2many('tsi.pd.info', 'reference_id5', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    # @api.depends('project_plan_sustainability_ispo.percentage', 'project_plan_sustainability_ispo.plan_sustainability_new.percentage')
    # def _compute_total_percentage(self):
    #     for record in self:
    #         total = 0.0
    #         # Sum percentages from `project_plan_sustainability_ispo`
    #         for line in record.project_plan_sustainability_ispo:
    #             if line.percentage:
    #                 total += line.percentage
    #             # Sum percentages from nested `plan_sustainability_new`
    #             for sub_line in line.plan_sustainability_new:
    #                 if sub_line.percentage:
    #                     total += sub_line.percentage
    #         # Assign the total to the `amount_percentage` field
    #         record.amount_percentage = total
    
    @api.depends(
    'project_plan_sustainability_ispo.percentage', 
    'project_plan_sustainability_ispo.plan_sustainability_new.percentage',
    'project_plan_sustainability_ispo.plan_sustainability_new.plan_sustainability_new_details.percentage',
    'project_plan_sustainability_ispo.plan_sustainability_new.plan_sustainability_new_details.plan_sustainability_new_details1.percentage',
    'project_plan_sustainability_ispo.plan_sustainability_new.plan_sustainability_new_details.plan_sustainability_new_details1.plan_sustainability_new_details2.percentage',
    'project_plan_sustainability_ispo.plan_sustainability_new.plan_sustainability_new_details.plan_sustainability_new_details1.plan_sustainability_new_details2.plan_sustainability_new_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_sustainability_ispo`
            for line in record.project_plan_sustainability_ispo:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_sustainability_new`
                for sub_line in line.plan_sustainability_new:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_sustainability_new_details`
                    for detail in sub_line.plan_sustainability_new_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_sustainability_new_details1`
                        for detail1 in detail.plan_sustainability_new_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_sustainability_new_details2`
                            for detail2 in detail1.plan_sustainability_new_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_sustainability_new_details3` (level paling dalam)
                                for detail3 in detail2.plan_sustainability_new_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_sustainability_ispo.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_sustainability_ispo = tahapan.project_plan_sustainability_ispo.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_sustainability_ispo
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_sustainability_ispo.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_sustainability_ispo.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_sustainability_ispo = tahapan.project_plan_sustainability_ispo.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_sustainability_ispo
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_sustainability_ispo.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanSustainabilityISCC(models.Model):
    _name = 'project.plan.sustainability.iscc'
    _description = 'Project Plan Sustainability ISPO'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_sustainability_iscc    = fields.One2many('tsi.pd.info', 'reference_id6', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    @api.depends('project_plan_sustainability_iscc.percentage', 'project_plan_sustainability_iscc.plan_sustainability_existing.percentage')
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            # Sum percentages from `project_plan_sustainability_iscc`
            for line in record.project_plan_sustainability_iscc:
                if line.percentage:
                    total += line.percentage
                # Sum percentages from nested `plan_sustainability_existing`
                for sub_line in line.plan_sustainability_existing:
                    if sub_line.percentage:
                        total += sub_line.percentage
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total
    
    @api.depends(
    'project_plan_sustainability_iscc.percentage', 
    'project_plan_sustainability_iscc.plan_sustainability_existing.percentage',
    'project_plan_sustainability_iscc.plan_sustainability_existing.plan_sustainability_existing_details.percentage',
    'project_plan_sustainability_iscc.plan_sustainability_existing.plan_sustainability_existing_details.plan_sustainability_existing_details1.percentage',
    'project_plan_sustainability_iscc.plan_sustainability_existing.plan_sustainability_existing_details.plan_sustainability_existing_details1.plan_sustainability_existing_details2.percentage',
    'project_plan_sustainability_iscc.plan_sustainability_existing.plan_sustainability_existing_details.plan_sustainability_existing_details1.plan_sustainability_existing_details2.plan_sustainability_existing_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_sustainability_iscc`
            for line in record.project_plan_sustainability_iscc:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_sustainability_existing`
                for sub_line in line.plan_sustainability_existing:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_sustainability_existing_details`
                    for detail in sub_line.plan_sustainability_existing_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_sustainability_existing_details1`
                        for detail1 in detail.plan_sustainability_existing_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_sustainability_existing_details2`
                            for detail2 in detail1.plan_sustainability_existing_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_sustainability_existing_details3` (level paling dalam)
                                for detail3 in detail2.plan_sustainability_existing_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_sustainability_iscc.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_sustainability_iscc = tahapan.project_plan_sustainability_iscc.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_sustainability_iscc
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_sustainability_iscc.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_sustainability_iscc.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_sustainability_iscc = tahapan.project_plan_sustainability_iscc.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_sustainability_iscc
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_sustainability_iscc.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanSustainabilityISCC(models.Model):
    _name = 'project.plan.sustainability'
    _description = 'Project Plan Sustainability ISPO'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_sustainability    = fields.One2many('tsi.pd.info', 'reference_id6', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_sustainability.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_sustainability = tahapan.project_plan_sustainability.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_sustainability
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_sustainability.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_sustainability.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_sustainability = tahapan.project_plan_sustainability.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_sustainability
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_sustainability.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanXMS9001(models.Model):
    _name = 'project.plan.9001'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_9001    = fields.One2many('tsi.pd.info', 'reference_id7', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_9001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_9001 = tahapan.project_plan_xms_9001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_9001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_9001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_9001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_9001 = tahapan.project_plan_xms_9001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_9001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_9001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectPlanXMS9001(models.Model):
    _name = 'project.plan.xms.9001'
    _description = 'Project Plan XMS'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_9001    = fields.One2many('tsi.pd.info', 'reference_id7', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    # @api.depends('project_plan_xms_9001.percentage', 'project_plan_xms_9001.plan_xms_new.percentage')
    # def _compute_total_percentage(self):
    #     for record in self:
    #         total = 0.0
    #         # Sum percentages from `project_plan_xms_9001`
    #         for line in record.project_plan_xms_9001:
    #             if line.percentage:
    #                 total += line.percentage
    #             # Sum percentages from nested `plan_xms_new`
    #             for sub_line in line.plan_xms_new:
    #                 if sub_line.percentage:
    #                     total += sub_line.percentage
    #         # Assign the total to the `amount_percentage` field
    #         record.amount_percentage = total
    
    @api.depends(
    'project_plan_xms_9001.percentage', 
    'project_plan_xms_9001.plan_xms_new.percentage',
    'project_plan_xms_9001.plan_xms_new.plan_xms_new_details.percentage',
    'project_plan_xms_9001.plan_xms_new.plan_xms_new_details.plan_xms_new_details1.percentage',
    'project_plan_xms_9001.plan_xms_new.plan_xms_new_details.plan_xms_new_details1.plan_xms_new_details2.percentage',
    'project_plan_xms_9001.plan_xms_new.plan_xms_new_details.plan_xms_new_details1.plan_xms_new_details2.plan_xms_new_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_xms_9001`
            for line in record.project_plan_xms_9001:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_xms_new`
                for sub_line in line.plan_xms_new:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_xms_new_details`
                    for detail in sub_line.plan_xms_new_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_xms_new_details1`
                        for detail1 in detail.plan_xms_new_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_xms_new_details2`
                            for detail2 in detail1.plan_xms_new_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_xms_new_details3` (level paling dalam)
                                for detail3 in detail2.plan_xms_new_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_xms_9001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_9001 = tahapan.project_plan_xms_9001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_9001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_9001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_9001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_9001 = tahapan.project_plan_xms_9001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_9001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_9001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectPlanXMS(models.Model):
    _name = 'project.plan.xms'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms    = fields.One2many('tsi.pd.info', 'reference_id7', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms = tahapan.project_plan_xms.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms = tahapan.project_plan_xms.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanXMS14001(models.Model):
    _name = 'project.plan.14001'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_14001    = fields.One2many('tsi.pd.info', 'reference_id8', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_14001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_14001 = tahapan.project_plan_xms_14001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_14001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_14001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_14001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_14001 = tahapan.project_plan_xms_14001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_14001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_14001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectPlanXMS14001(models.Model):
    _name = 'project.plan.xms.14001'
    _description = 'Project Plan XMS'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_14001    = fields.One2many('tsi.pd.info', 'reference_id8', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    # @api.depends('project_plan_xms_14001.percentage', 'project_plan_xms_14001.plan_xms_existing.percentage')
    # def _compute_total_percentage(self):
    #     for record in self:
    #         total = 0.0
    #         # Sum percentages from `project_plan_xms_14001`
    #         for line in record.project_plan_xms_14001:
    #             if line.percentage:
    #                 total += line.percentage
    #             # Sum percentages from nested `plan_xms_existing`
    #             for sub_line in line.plan_xms_existing:
    #                 if sub_line.percentage:
    #                     total += sub_line.percentage
    #         # Assign the total to the `amount_percentage` field
    #         record.amount_percentage = total
    
    @api.depends(
    'project_plan_xms_14001.percentage', 
    'project_plan_xms_14001.plan_xms_existing.percentage',
    'project_plan_xms_14001.plan_xms_existing.plan_xms_existing_details.percentage',
    'project_plan_xms_14001.plan_xms_existing.plan_xms_existing_details.plan_xms_existing_details1.percentage',
    'project_plan_xms_14001.plan_xms_existing.plan_xms_existing_details.plan_xms_existing_details1.plan_xms_existing_details2.percentage',
    'project_plan_xms_14001.plan_xms_existing.plan_xms_existing_details.plan_xms_existing_details1.plan_xms_existing_details2.plan_xms_existing_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_xms_14001`
            for line in record.project_plan_xms_14001:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_xms_existing`
                for sub_line in line.plan_xms_existing:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_xms_existing_details`
                    for detail in sub_line.plan_xms_existing_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_xms_existing_details1`
                        for detail1 in detail.plan_xms_existing_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_xms_existing_details2`
                            for detail2 in detail1.plan_xms_existing_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_xms_existing_details3` (level paling dalam)
                                for detail3 in detail2.plan_xms_existing_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_xms_14001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_14001 = tahapan.project_plan_xms_14001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_14001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_14001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_14001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_14001 = tahapan.project_plan_xms_14001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_14001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_14001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed


class PlanXMS45001(models.Model):
    _name = 'project.plan.45001'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_45001    = fields.One2many('tsi.pd.info', 'reference_id9', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_45001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_45001 = tahapan.project_plan_xms_45001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_45001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_45001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_45001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_45001 = tahapan.project_plan_xms_45001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_45001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_45001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectPlanXMS45001(models.Model):
    _name = 'project.plan.xms.45001'
    _description = 'Project Plan XMS'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_45001    = fields.One2many('tsi.pd.info', 'reference_id9', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    @api.depends('project_plan_xms_45001.percentage', 'project_plan_xms_45001.plan_others_new.percentage')
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            # Sum percentages from `project_plan_xms_45001`
            for line in record.project_plan_xms_45001:
                if line.percentage:
                    total += line.percentage
                # Sum percentages from nested `plan_others_new`
                for sub_line in line.plan_others_new:
                    if sub_line.percentage:
                        total += sub_line.percentage
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total
    
    @api.depends(
    'project_plan_xms_45001.percentage', 
    'project_plan_xms_45001.plan_others_new.percentage',
    'project_plan_xms_45001.plan_others_new.plan_others_new_details.percentage',
    'project_plan_xms_45001.plan_others_new.plan_others_new_details.plan_others_new_details1.percentage',
    'project_plan_xms_45001.plan_others_new.plan_others_new_details.plan_others_new_details1.plan_others_new_details2.percentage',
    'project_plan_xms_45001.plan_others_new.plan_others_new_details.plan_others_new_details1.plan_others_new_details2.plan_others_new_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_xms_45001`
            for line in record.project_plan_xms_45001:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_others_new`
                for sub_line in line.plan_others_new:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_others_new_details`
                    for detail in sub_line.plan_others_new_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_others_new_details1`
                        for detail1 in detail.plan_others_new_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_others_new_details2`
                            for detail2 in detail1.plan_others_new_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_others_new_details3` (level paling dalam)
                                for detail3 in detail2.plan_others_new_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_xms_45001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_45001 = tahapan.project_plan_xms_45001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_45001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_45001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_45001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_45001 = tahapan.project_plan_xms_45001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_45001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_45001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanXMS21000(models.Model):
    _name = 'project.plan.21000'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_21000    = fields.One2many('tsi.pd.info', 'reference_id10', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_21000.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_21000 = tahapan.project_plan_xms_21000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_21000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_21000.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_21000.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_21000 = tahapan.project_plan_xms_21000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_21000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_21000.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectPlanXMS21000(models.Model):
    _name = 'project.plan.xms.21000'
    _description = 'Project Plan XMS'
    _order = 'id DESC'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_21000    = fields.One2many('tsi.pd.info', 'reference_id10', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)
    amount_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    @api.depends('project_plan_xms_21000.percentage', 'project_plan_xms_21000.plan_others_existing.percentage')
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            # Sum percentages from `project_plan_xms_21000`
            for line in record.project_plan_xms_21000:
                if line.percentage:
                    total += line.percentage
                # Sum percentages from nested `plan_others_existing`
                for sub_line in line.plan_others_existing:
                    if sub_line.percentage:
                        total += sub_line.percentage
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total
    
    @api.depends(
    'project_plan_xms_21000.percentage', 
    'project_plan_xms_21000.plan_others_existing.percentage',
    'project_plan_xms_21000.plan_others_existing.plan_others_existing_details.percentage',
    'project_plan_xms_21000.plan_others_existing.plan_others_existing_details.plan_others_existing_details1.percentage',
    'project_plan_xms_21000.plan_others_existing.plan_others_existing_details.plan_others_existing_details1.plan_others_existing_details2.percentage',
    'project_plan_xms_21000.plan_others_existing.plan_others_existing_details.plan_others_existing_details1.plan_others_existing_details2.plan_others_existing_details3.percentage'
    )
    def _compute_total_percentage(self):
        for record in self:
            total = 0.0
            
            # Sum percentages from `project_plan_xms_21000`
            for line in record.project_plan_xms_21000:
                if line.percentage:
                    total += line.percentage
                
                # Sum percentages from nested `plan_others_new`
                for sub_line in line.plan_others_new:
                    if sub_line.percentage:
                        total += sub_line.percentage

                    # Sum percentages from nested `plan_others_new_details`
                    for detail in sub_line.plan_others_new_details:
                        if detail.percentage:
                            total += detail.percentage

                        # Sum percentages from nested `plan_others_new_details1`
                        for detail1 in detail.plan_others_new_details1:
                            if detail1.percentage:
                                total += detail1.percentage

                            # Sum percentages from nested `plan_others_new_details2`
                            for detail2 in detail1.plan_others_new_details2:
                                if detail2.percentage:
                                    total += detail2.percentage

                                # Sum percentages from nested `plan_others_new_details3` (level paling dalam)
                                for detail3 in detail2.plan_others_new_details3:
                                    if detail3.percentage:
                                        total += detail3.percentage
            
            # Assign the total to the `amount_percentage` field
            record.amount_percentage = total

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
    
    @api.depends('project_plan_xms_21000.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_21000 = tahapan.project_plan_xms_21000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_21000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_21000.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_21000.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_21000 = tahapan.project_plan_xms_21000.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_21000
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_21000.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanXMS37001(models.Model):
    _name = 'project.plan.xms.37001'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    noted = fields.Html('Noted')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_37001    = fields.One2many('tsi.pd.info', 'reference_id11', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_37001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_37001 = tahapan.project_plan_xms_37001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_37001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_37001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_37001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_37001 = tahapan.project_plan_xms_37001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_37001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_37001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PlanXMS37001(models.Model):
    _name = 'project.plan.37001'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_37001    = fields.One2many('tsi.pd.info', 'reference_id11', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_37001.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_37001 = tahapan.project_plan_37001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_37001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_37001.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_37001.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_37001 = tahapan.project_plan_37001.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_37001
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_37001.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed


class ProjectPlanSMK3(models.Model):
    _name = 'project.plan.smk3'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_smk3    = fields.One2many('tsi.pd.info', 'reference_id12', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_smk3.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_smk3 = tahapan.project_plan_xms_smk3.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_smk3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_smk3.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_smk3.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_smk3 = tahapan.project_plan_xms_smk3.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_smk3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_smk3.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectPlanXMSSMK3(models.Model):
    _name = 'project.plan.xms.smk3'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_xms_smk3    = fields.One2many('tsi.pd.info', 'reference_id12', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_xms_smk3.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_smk3 = tahapan.project_plan_xms_smk3.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_smk3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_smk3.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_xms_smk3.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_xms_smk3 = tahapan.project_plan_xms_smk3.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_xms_smk3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_xms_smk3.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class ProjectSMK3(models.Model):
    _name = 'plan.smk3'
    _description = 'Project Plan XMS'

    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
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
    budget_plan = fields.Float(string='Budget - Plan')
    budget_actual = fields.Float(string='Budget - Actual')
    amount_total_plan = fields.Monetary(string="Budget - Plan", store=True, compute='_compute_amounts', tracking=4)
    amount_total_actual = fields.Monetary(string="Budget - Actual", store=True, compute='_compute_amountss', tracking=4)
    project_plan_smk3    = fields.One2many('tsi.pd.info', 'reference_id13', string="Info", index=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_untaxedd = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amountss', tracking=5)

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
    
    @api.depends('project_plan_smk3.budget_plan')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_smk3 = tahapan.project_plan_smk3.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_smk3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_smk3.mapped('budget_plan'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_plan = tahapan.amount_untaxed
    
    @api.depends('project_plan_smk3.budget_actual')
    def _compute_amountss(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            project_plan_smk3 = tahapan.project_plan_smk3.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in project_plan_smk3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(project_plan_smk3.mapped('budget_actual'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total_actual = tahapan.amount_untaxed

class PDInfoinfo(models.Model):
    _name           = 'tsi.pd.info'
    _description    = 'Project Plan Info'

    reference_id    = fields.Many2one('project.plan.food.22000', string="Reference")
    reference_id2    = fields.Many2one('project.plan.food.haccp', string="Reference")
    reference_id3    = fields.Many2one('project.plan.ict.27001', string="Reference")
    reference_id4    = fields.Many2one('project.plan.ict.20000', string="Reference")
    reference_id5    = fields.Many2one('project.plan.sustainability.ispo', string="Reference")
    reference_id6    = fields.Many2one('project.plan.sustainability.iscc', string="Reference")
    reference_id7    = fields.Many2one('project.plan.xms.9001', string="Reference")
    reference_id8    = fields.Many2one('project.plan.xms.14001', string="Reference")
    reference_id9    = fields.Many2one('project.plan.xms.45001', string="Reference")
    reference_id10    = fields.Many2one('project.plan.xms.21000', string="Reference")
    reference_id11   = fields.Many2one('project.plan.xms.37001', string="Reference")
    reference_id12   = fields.Many2one('project.plan.smk3', string="Reference")
    reference_id13   = fields.Many2one('plan.smk3', string="Reference")
    is_checked = fields.Boolean(string="Tracking Done")  # Checkbox field
    nama_site       = fields.Char(string='Nama Site')
    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    budget_plan = fields.Integer(string='Budget - Plan')
    budget_actual = fields.Integer(string='Budget - Actual')
    noted = fields.Html('Noted')
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    plan_food_new    = fields.One2many('tsi.plan.info', 'reference_ids', string="Info", index=True)
    plan_food_existing    = fields.One2many('tsi.plan.info', 'reference_ids_1', string="Info", index=True)
    plan_ict_new    = fields.One2many('tsi.plan.info', 'reference_ids_2', string="Info", index=True)
    plan_ict_existing    = fields.One2many('tsi.plan.info', 'reference_ids_3', string="Info", index=True)
    plan_sustainability_new    = fields.One2many('tsi.plan.info', 'reference_ids_5', string="Info", index=True)
    plan_sustainability_existing    = fields.One2many('tsi.plan.info', 'reference_ids_6', string="Info", index=True)
    plan_xms_new    = fields.One2many('tsi.plan.info', 'reference_ids_7', string="Info", index=True)
    plan_xms_existing    = fields.One2many('tsi.plan.info', 'reference_ids_8', string="Info", index=True)
    plan_others_new    = fields.One2many('tsi.plan.info', 'reference_ids_9', string="Info", index=True)
    plan_others_existing    = fields.One2many('tsi.plan.info', 'reference_ids_10', string="Info", index=True)

class PDInfoinfo(models.Model):
    _name           = 'tsi.plan.info'
    _description    = 'Project Plan Info'

    reference_ids    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_1    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_2    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_3    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_5    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_6    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_7    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_8    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_9    = fields.Many2one('tsi.pd.info', string="Reference")
    reference_ids_10    = fields.Many2one('tsi.pd.info', string="Reference")
    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    noted = fields.Html('Noted')
    plan_food_new_details    = fields.One2many('tsi.plan.info.details', 'reference_ids', string="Info", index=True)
    plan_food_existing_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_1', string="Info", index=True)
    plan_ict_new_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_2', string="Info", index=True)
    plan_ict_existing_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_3', string="Info", index=True)
    plan_sustainability_new_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_5', string="Info", index=True)
    plan_sustainability_existing_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_6', string="Info", index=True)
    plan_xms_new_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_7', string="Info", index=True)
    plan_xms_existing_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_8', string="Info", index=True)
    plan_others_new_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_9', string="Info", index=True)
    plan_others_existing_details    = fields.One2many('tsi.plan.info.details', 'reference_ids_10', string="Info", index=True)

class PDInfoinfoDetails(models.Model):
    _name           = 'tsi.plan.info.details'
    _description    = 'Project Plan Info'

    reference_ids    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_1    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_2    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_3    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_5    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_6    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_7    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_8    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_9    = fields.Many2one('tsi.plan.info', string="Reference")
    reference_ids_10    = fields.Many2one('tsi.plan.info', string="Reference")
    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    noted = fields.Html('Noted')
    plan_food_new_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids', string="Info", index=True)
    plan_food_existing_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_1', string="Info", index=True)
    plan_ict_new_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_2', string="Info", index=True)
    plan_ict_existing_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_3', string="Info", index=True)
    plan_sustainability_new_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_5', string="Info", index=True)
    plan_sustainability_existing_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_6', string="Info", index=True)
    plan_xms_new_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_7', string="Info", index=True)
    plan_xms_existing_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_8', string="Info", index=True)
    plan_others_new_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_9', string="Info", index=True)
    plan_others_existing_details1    = fields.One2many('tsi.plan.info.details1', 'reference_ids_10', string="Info", index=True)

class PDInfoinfoDetails1(models.Model):
    _name           = 'tsi.plan.info.details1'
    _description    = 'Project Plan Info'

    reference_ids    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_1    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_2    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_3    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_5    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_6    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_7    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_8    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_9    = fields.Many2one('tsi.plan.info.details', string="Reference")
    reference_ids_10    = fields.Many2one('tsi.plan.info.details', string="Reference")
    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    noted = fields.Html('Noted')
    plan_food_new_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids', string="Info", index=True)
    plan_food_existing_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_1', string="Info", index=True)
    plan_ict_new_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_2', string="Info", index=True)
    plan_ict_existing_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_3', string="Info", index=True)
    plan_sustainability_new_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_5', string="Info", index=True)
    plan_sustainability_existing_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_6', string="Info", index=True)
    plan_xms_new_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_7', string="Info", index=True)
    plan_xms_existing_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_8', string="Info", index=True)
    plan_others_new_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_9', string="Info", index=True)
    plan_others_existing_details2    = fields.One2many('tsi.plan.info.details2', 'reference_ids_10', string="Info", index=True)

class PDInfoinfoDetails2(models.Model):
    _name           = 'tsi.plan.info.details2'
    _description    = 'Project Plan Info'

    reference_ids    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_1    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_2    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_3    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_5    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_6    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_7    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_8    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_9    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    reference_ids_10    = fields.Many2one('tsi.plan.info.details1', string="Reference")
    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    noted = fields.Html('Noted')
    plan_food_new_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids', string="Info", index=True)
    plan_food_existing_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_1', string="Info", index=True)
    plan_ict_new_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_2', string="Info", index=True)
    plan_ict_existing_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_3', string="Info", index=True)
    plan_sustainability_new_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_5', string="Info", index=True)
    plan_sustainability_existing_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_6', string="Info", index=True)
    plan_xms_new_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_7', string="Info", index=True)
    plan_xms_existing_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_8', string="Info", index=True)
    plan_others_new_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_9', string="Info", index=True)
    plan_others_existing_details3    = fields.One2many('tsi.plan.info.details3', 'reference_ids_10', string="Info", index=True)

class PDInfoinfoDetails3(models.Model):
    _name           = 'tsi.plan.info.details3'
    _description    = 'Project Plan Info'

    reference_ids    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_1    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_2    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_3    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_5    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_6    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_7    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_8    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_9    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    reference_ids_10    = fields.Many2one('tsi.plan.info.details2', string="Reference")
    name = fields.Char(string='Task Name', required=True)
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Status', default='not_started')
    assignee = fields.Char(string='Assignee')
    plan_start_date = fields.Date(string='Plan Start Date')
    plan_end_date = fields.Date(string='Plan End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    percentage = fields.Integer(string='Percentage', default=0)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority')
    tags = fields.Selection([
        ('PD', 'PD'),
        ('Marketing', 'Marketing'),
        ('Operasional', 'Operasional'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),], string='Tags')
    noted = fields.Html('Noted')