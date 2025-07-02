from odoo import models, fields, api
from datetime import datetime

class AuditRecord(models.Model):
    _name = 'audit.record'
    _description = 'Audit Record'
    _description    = "Operation War Sheet"
    _rec_name       = 'partner_id'

    partner_id          = fields.Many2one('res.partner', string="Nama Klien", domain="[('is_company', '=', True)]")
    sales_person       = fields.Many2one('res.users', string="Pic Person")
    contract_price = fields.Float(string='Harga Kontrak')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True, domain="[('standard', 'in', ['iso'])]", related="partner_id.tahun_masuk_lines.iso_standard_ids")
    scope = fields.Char(string='Scope', related="partner_id.scope")
    client_status = fields.Selection([
        ('active', 'Aktif'),
        ('inactive', 'Tidak Aktif')
    ], string='Status Klien', default='active', related="partner_id.status_klien")
    due_date_fu = fields.Date(string='Due Date FU')
    audit_date = fields.Date(string='Tanggal Sertifikasi')
    control = fields.Char(string='Control')
    audit_stage = fields.Selection([
        ('sv1', 'SV1'),
        ('sv2', 'SV2')
    ], string='Audit Stage')
    employee_count = fields.Integer(string='Jumlah Karyawan', related="partner_id.site_lines.jumlah_karyawan")
    reduction = fields.Float(string='Reduction (%)')
    stage_ids = fields.One2many('audit.stage', 'audit_id', string='Audit Stages')
    ca_closing_date = fields.Date(string='CA Closing Date')
    status_payment = fields.Char(string='Status Payment')
    november_income = fields.Float(string='November Income')
    december_income = fields.Float(string='December Income')


class AuditStage(models.Model):
    _name = 'audit.stage'
    _description = 'Audit Stage'

    audit_id = fields.Many2one('audit.record', string='Audit Record', ondelete='cascade')
    name = fields.Selection([
        ('stage1', 'Stage 1'),
        ('stage2', 'Stage 2')
    ], string='Stage', required=True)
    lead_audit = fields.Char(string='Lead Audit')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    audit_time = fields.Float(string='Audit Time (Hours)', compute='_compute_audit_time', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('start_date', 'end_date')
    def _compute_audit_time(self):
        for record in self:
            if record.start_date and record.end_date:
                # Hitung selisih tanggal dalam hari
                start = fields.Date.from_string(record.start_date)
                end = fields.Date.from_string(record.end_date)
                delta = (end - start).days + 1  # Tambahkan 1 agar hari dihitung penuh
                # Asumsi: Setiap hari audit adalah 8 jam
                record.audit_time = delta * 8
            else:
                record.audit_time = 0.0