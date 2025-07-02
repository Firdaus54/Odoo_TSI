from odoo import models, fields, api, SUPERUSER_ID, _

class AuditPlanISPO(models.Model):
    _name           = 'ops.plan.ispo'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Plan ISPO'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference")    

    notification_id = fields.Many2one('audit.notification.ispo', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

# related, ea_code ???
    # program_id       = fields.Many2one('ops.program', string='Program')
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
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIKk'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True, related='ispo_reference.scope')
    boundaries          = fields.Text('Boundaries', related='ispo_reference.boundaries')
    # boundaries_id  = fields.Many2many('tsi.iso.boundaries', string="Boundaries", related="ispo_reference.boundaries_id")
    telepon             = fields.Char(string="No Telepon", related='ispo_reference.telepon')

    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code", related="program_id.ea_code")
    program_id          = fields.Many2one('ops.program.ispo', string='Program')
    type_cient          = fields.Char(string="Seasonal")
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
                        ], string='Certification Type', index=True, readonly=True, related='ispo_reference.certification' )
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
    # program_id = fields.Many2one('ops.program', string='Program Reference')
    audit_stage           = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Survillance-3',    'Surveilance 3'),
                            ('Survillance-4',    'Surveilance 4'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], string='Audit Type', tracking=True)


    audit_objectives    = fields.Many2many('ops.objectives',string='Audit Objectives')
    

    plan_detail_ids = fields.One2many('ops.plan_detail', 'plan_id', string="Plan", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')

    def set_to_confirm(self):
        self.write({'state': 'confirm'})
        for plan in self:
            # Ambil semua record ops.program.aktual yang terhubung dengan plan ini
            program_lines = self.env['ops.program.aktual.ispo'].search([('referance_id', '=', plan.id)])
            for program_line in program_lines:
                # Ambil record ops.program yang terhubung dengan ops.program.aktual ini
                program = self.env['ops.program.ispo'].search([('program_lines_aktual', 'in', program_line.id)])
                if program:
                    # Update audit_stage di ops.program berdasarkan audit_stage di ops.plan
                    program.write({
                        'audit_stage': plan.audit_stage
                    })            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.plan.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditPlanISPO, self).create(vals)
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

# class AuditPlanDetail(models.Model):
#     _name           = 'ops.plan_detail'
#     _description    = 'Audit Plan Detail'

#     plan_id         = fields.Many2one('ops.plan', string="Plan", ondelete='cascade', index=True)
#     auditor         = fields.Char(string='Auditor')
#     time            = fields.Char(string='Time')
#     function        = fields.Many2one('ops.plan_function', string='Function')
#     agenda          = fields.Many2many('ops.plan_agenda', string='Agenda')


# class AuditPlanFunction(models.Model):
#     _name           = 'ops.plan_function'
#     _description    = 'Audit Plan Function'

#     name            = fields.Char(string='Name')

# class AuditPlangenda(models.Model):
#     _name           = 'ops.plan_agenda'
#     _description    = 'Audit Plan Agenda'

#     kode            = fields.Char(string='Kode')
#     name            = fields.Char(string='Name')
#     iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')

#     def name_get(self):
#         result = []	
#         for rec in self:
#             result.append((rec.id, '[%s] %s' % (rec.kode,rec.name)))	
#         return result

# class AuditObjectives(models.Model):
#     _name           = 'ops.objectives'
#     _description    = 'Audit Objectives'

#     audit_stage           = fields.Selection([
#                             ('ia_1',     'Stage 1'),
#                             ('ia_2', 'Stage 2'),
#                             ('sv_1',    'Surveilance 1'),
#                             ('sv_2',    'Surveilance 2'),
#                             ('recert',    'Recertification'),
#                             ('special',    'Special Audit')
#                         ])

#     name                = fields.Char(string='Objectives')
#     iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
