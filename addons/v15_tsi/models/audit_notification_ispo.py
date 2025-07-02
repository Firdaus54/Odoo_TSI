from odoo import models, fields, api, _

class AuditNotificationISPO(models.Model):
    _name           = 'audit.notification.ispo'
    _description    = 'Audit Notification ISPO'
    _order          = 'id DESC'

    name                = fields.Char(string='Document No',  readonly=True)
    ispo_reference       = fields.Many2one('tsi.ispo', string="Reference",  readonly=True)    
    customer            = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

    plan_lines          = fields.One2many('ops.plan.ispo', 'notification_id', string="Plan", index=True,  readonly=True)
    program_lines       = fields.One2many('ops.program.ispo', 'notification_id', string="Program", index=True,  readonly=True)
    report_lines        = fields.One2many('ops.report.ispo', 'notification_id', string="Report", index=True,  readonly=True)
    review_lines        = fields.One2many('ops.review.ispo', 'notification_id', string="Review", index=True,  readonly=True)
    sertifikat_lines    = fields.One2many('ops.sertifikat.ispo', 'notification_id', string="Sertifikat", index=True,  readonly=True)
    # delivery_sertifikat_line = fields.One2many('sertifikat.delivery', 'notification_id', string="Delivery Sertifikat", index=True,  readonly=True)
    audit_state = fields.Selection([
        ('program', 'Program'),
        ('Stage-1', 'Stage-1'),
        ('Stage-2', 'Stage-2'),
        ('Surveillance1', 'Surveillance1'),
        ('Surveillance2', 'Surveillance2'),
        ('Surveillance3', 'Surveillance3'),
        ('Surveillance4', 'Surveillance4'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status', compute='_compute_audit_status', store=True)

    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', related="sales_order_id.tipe_pembayaran", readonly=False)


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('audit.notification.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditNotificationISPO, self).create(vals)
        return result
    
    @api.depends('program_lines.state', 'plan_lines.state', 'report_lines.state', 'review_lines.state', 'sertifikat_lines.state')
    def _compute_audit_status(self):
        for record in self:
            if any(program.state == 'done' for program in record.program_lines):
                record.audit_state = 'Stage-1'
            if any(program.state == 'done_stage2' for program in record.program_lines):
                record.audit_state = 'Stage-2'
            if any(program.state == 'done_surveillance1' for program in record.program_lines):
                record.audit_state = 'Surveillance1'
            if any(program.state == 'done_surveillance2' for program in record.program_lines):
                record.audit_state = 'Surveillance2'
            if any(program.state == 'done_surveillance3' for program in record.program_lines):
                record.audit_state = 'Surveillance3'
            if any(program.state == 'done_surveillance4' for program in record.program_lines):
                record.audit_state = 'Surveillance4'
            if any(plan.state == 'done' for plan in record.plan_lines):
                record.audit_state = 'plan'
            if any(report.state == 'done' for report in record.report_lines):
                record.audit_state = 'report'
            if any(recommendation.state == 'done' for recommendation in record.review_lines):
                record.audit_state = 'recommendation'
            # elif any(recommendation.state == 'done' for recommendation in record.review_lines):
            #     record.audit_state = 'Recommendation'
            if any(certificate.state == 'done' for certificate in record.sertifikat_lines):
                record.audit_state = 'certificate'
            if any(program.state == 'new' for program in record.program_lines):
                record.audit_state = 'draft'

    def write(self, vals):
        res = super(AuditNotification, self).write(vals)
        # Set audit status when any related audit status is updated
        if any(key in vals for key in ['program_lines', 'plan_lines', 'report_lines', 'review_lines', 'sertifikat_lines']):
            self._compute_audit_status()
        return res