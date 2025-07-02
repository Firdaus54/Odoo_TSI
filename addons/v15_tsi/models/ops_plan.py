from odoo import models, fields, api, SUPERUSER_ID, _

class AuditPlan(models.Model):
    _name           = 'ops.plan'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Plan'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    iso_reference   = fields.Many2one('tsi.iso', string="Reference")    

    notification_id = fields.Many2one('audit.notification', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

# related, ea_code ???
    # program_id       = fields.Many2one('ops.program', string='Program')
    customer            = fields.Many2one('res.partner', string="Customer", compute='_compute_customer', store=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", compute='_compute_customer', store=True)
    head_office         = fields.Char(string="Jumlah Head Office", compute='_compute_customer', store=True)
    site_office         = fields.Char(string="Jumlah Site Office", compute='_compute_customer', store=True)
    off_location        = fields.Char(string="Jumlah Off Location", compute='_compute_customer', store=True)
    part_time           = fields.Char(string="Jumlah Part Time", compute='_compute_customer', store=True)
    subcon              = fields.Char(string="Jumlah Sub Contractor", compute='_compute_customer', store=True)
    unskilled           = fields.Char(string="Jumlah Unskilled", compute='_compute_customer', store=True)
    seasonal            = fields.Char(string="Jumlah Seasonal", compute='_compute_customer', store=True)
    total_emp           = fields.Integer(string="Total Employee", compute='_compute_customer', store=True)
    scope               = fields.Text('Scope', compute='_compute_customer', store=True)
    boundaries          = fields.Text('Boundaries', compute='_compute_customer', store=True)
    # boundaries_id  = fields.Many2many('tsi.iso.boundaries', string="Boundaries", related="iso_reference.boundaries_id")
    telepon             = fields.Char(string="No Telepon", compute='_compute_customer', store=True)

    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code", related="program_id.ea_code")
    ea_code_plan        = fields.Many2many('tsi.ea_code', 'rel_ops_plan_ea_code', string="IAF Code Existing", related="program_id.ea_code_prog")
    program_id          = fields.Many2one('ops.program', string='Program')
    # type_cient          = fields.Char(string="Seasonal")
    apprev_date         = fields.Date(string="Review Date")    
    contract_date       = fields.Date(string="Contract Date")    
    contract_number     = fields.Char(string="Contract Number")    
    dokumen_sosialisasi        = fields.Binary('Organization Chart')
    file_name1      = fields.Char('Filename')
    criteria        = fields.Char(string='Criteria')
    #bisa pilih salah satu
    # boundaries      = fields.Text(string='Boundaries')


# form
    contract_number     = fields.Char('Contract Number')
    audit_start         = fields.Date('Audit Start',)
    audit_end           = fields.Date('Audit End',)
    certification_type  = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, readonly=True, related='iso_reference.certification' )
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    audit_criteria      = fields.Char('Audit Criteria')
    audit_method        = fields.Selection(string='Metode Audit', selection=[
                            ('online',   'Online'), 
                            ('onsite',   'Onsite'), 
                            ('hybrid',   'Hybrid'), 
                            ])

    technical_expert    = fields.Many2one('hr.employee', string='Technical Expert',)
    auditor_lead        = fields.Many2one('hr.employee', string="Lead Auditor",)
    auditor_1           = fields.Many2one('hr.employee', string='Auditor 1',)
    auditor_2           = fields.Many2one('hr.employee', string='Auditor 2')
    auditor_3           = fields.Many2one('hr.employee', string='Auditor 3')

    kan_1               = fields.Char('Name 1')
    kan_2               = fields.Char('Name 2')

    kan_function        = fields.Selection([
                            ('observer', 'Observer'),
                            ('expert',    'Technical Expert'),
                            ('witness',    'Witness'),
                        ], string='Function')
    program_id = fields.Many2one('ops.program', string='Program Reference')
    audit_stage           = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ])


    audit_objectives    = fields.Many2many('ops.objectives',string='Audit Objectives')
    

    plan_detail_ids = fields.One2many('ops.plan_detail', 'plan_id', string="Plan", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('waiting_finance', 'Waiting Finance'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')
    type_client         = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Type Client', tracking=True, related="program_id.type_client")
    
    @api.depends('iso_reference', 'program_id')
    def _compute_customer(self):
        for rec in self:
            if rec.iso_reference:
                rec.customer = rec.iso_reference.customer
                rec.contact_person = rec.iso_reference.contact_person
                rec.head_office = rec.iso_reference.head_office
                rec.telepon = rec.iso_reference.telepon
                rec.scope = rec.iso_reference.scope
            elif rec.program_id:
                rec.customer = rec.program_id.customer
                rec.contact_person = rec.program_id.contact_person
                rec.head_office = rec.program_id.head_office
                rec.telepon = rec.program_id.telepon
                rec.scope = rec.program_id.scope
                rec.ea_code = rec.program_id.ea_code
                rec.contract_number = rec.program_id.contract_number
                rec.contract_date = rec.program_id.contract_date
            else:
                rec.customer = False
                rec.contact_person = False
                rec.head_office = False
                rec.telepon = False
                rec.scope = False
                rec.ea_code = False
                rec.contract_number = False
                rec.contract_date = False

    def set_to_confirm(self):
        self.write({'state': 'confirm'})
        for plan in self:
            # Ambil semua record ops.program.aktual yang terhubung dengan plan ini
            program_lines = self.env['ops.program.aktual'].search([('referance_id', '=', plan.id)])
            for program_line in program_lines:
                # Ambil record ops.program yang terhubung dengan ops.program.aktual ini
                program = self.env['ops.program'].search([('program_lines_aktual', 'in', program_line.id)])
                if program:
                    # Update audit_stage di ops.program berdasarkan audit_stage di ops.plan
                    program.write({
                        'audit_stage': plan.audit_stage
                    })            
        return True

    def set_to_done(self):
        for rec in self:
            if rec.type_client == 'termin':
                rec.state = 'waiting_finance'
            else:
                rec.state = 'done'
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.plan')
        vals['name'] = sequence or _('New')
        result = super(AuditPlan, self).create(vals)
        return result
    

    def generate_stage1_report(self):
        # Code to generate Stage 1 report
        return self.env.ref('v15_tsi.report_plan_stage1').report_action(self)

    def generate_stage2_report(self):
        # Code to generate Stage 2 report
        return self.env.ref('v15_tsi.report_plan_stage2').report_action(self)
    
    def generate_survilance1_report(self):
        # Code to generate Stage 2 report
        return self.env.ref('v15_tsi.report_plan_surveillance1').report_action(self)
    
    def generate_survilance2_report(self):
        # Code to generate Stage 2 report
        return self.env.ref('v15_tsi.report_plan_surveillance2').report_action(self)

    def generate_report(self):
        if self.audit_stage == 'Stage-01':
            self.generate_stage1_report()
        elif self.audit_stage == 'Stage-02':
            self.generate_stage2_report()
        elif self.audit_stage == 'Survillance-1':
            self.generate_survilance1_report()
        elif self.audit_stage == 'Survillance-2':
            self.generate_survilance2_report()
        # elif self.audit_type == 'recertification':
        #     self.generate_recertification_report()

class AuditPlanDetail(models.Model):
    _name           = 'ops.plan_detail'
    _description    = 'Audit Plan Detail'

    plan_id         = fields.Many2one('ops.plan', string="Plan", ondelete='cascade', index=True)
    auditor         = fields.Char(string='Auditor')
    time            = fields.Char(string='Time')
    function        = fields.Many2one('ops.plan_function', string='Function')
    agenda          = fields.Many2many('ops.plan_agenda', string='Agenda')


class AuditPlanFunction(models.Model):
    _name           = 'ops.plan_function'
    _description    = 'Audit Plan Function'

    name            = fields.Char(string='Name')

class AuditPlangenda(models.Model):
    _name           = 'ops.plan_agenda'
    _description    = 'Audit Plan Agenda'

    kode            = fields.Char(string='Kode')
    name            = fields.Char(string='Name')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')

    def name_get(self):
        result = []	
        for rec in self:
            result.append((rec.id, '[%s] %s' % (rec.kode,rec.name)))	
        return result

class AuditObjectives(models.Model):
    _name           = 'ops.objectives'
    _description    = 'Audit Objectives'

    audit_stage           = fields.Selection([
                            ('ia_1',     'Stage 1'),
                            ('ia_2', 'Stage 2'),
                            ('sv_1',    'Surveilance 1'),
                            ('sv_2',    'Surveilance 2'),
                            ('recert',    'Recertification'),
                            ('special',    'Special Audit')
                        ])

    name                = fields.Char(string='Objectives')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
