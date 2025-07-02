from odoo import models, fields, api
from datetime import datetime

class AuditTaskFood(models.Model):
    _name = 'audit.task.food'
    _description = 'Food Quality Control'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISO 22000:2018', 'ISO 22000:2018'),
        ('HACCP', 'HACCP'),
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')

    # Field untuk menghitung rata-rata atau total
    total_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True
    )
    average_percentage = fields.Float(
        string='Average Percentage',
        compute='_compute_total_percentage',
        store=True
    )

    # @api.depends('percentage')
    # def _compute_total_percentage(self):
    #     # Menghitung total percentage
    #     total = 0.0
    #     # Mengiterasi semua record untuk menghitung total percentage
    #     for record in self:
    #         total += record.percentage
        
    #     # Menyimpan hasil ke dalam field `total_percentage`
    #     for record in self:
    #         record.total_percentage = total

    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain
        
class AuditTaskICT(models.Model):
    _name = 'audit.task.ict'
    _description = 'Audit Task'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISO/IEC 27001:2022', 'ISO/IEC 27001:2022'),
        ('ISO/IEC 20000-1:2018', 'ISO/IEC 20000-1:2018'),
        ('ISO/IEC 27701:2019', 'ISO/IEC 27701:2019'),
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')
    stage_id = fields.Many2one('audit.task.type', string='Stage', ondelete='restrict', group_expand='_read_group_stage_ids', index=True)
    # Field untuk menghitung rata-rata atau total
    # total_percentage = fields.Float(
    #     string='Total Percentage',
    #     compute='_compute_total_percentage',
    #     store=True
    # )

    @api.onchange('iso_standard_ids')
    def _onchange_iso_standard(self):
        # Menyaring standar ISO sesuai dengan jenis audit task
        if self._name == 'audit.task.food':
            self.iso_standard_ids = self.env['iso.standard'].search([
                ('name', 'in', ['ISO/IEC 27001:2022'])
            ])
    
    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain

class AuditTaskSustainability(models.Model):
    _name = 'audit.task.sustainability'
    _description = 'Audit Task'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISPO', 'ISPO'),
        ('ISCC', 'ISCC')
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('surveillance3', 'Surveillance 3'),
        ('surveillance4', 'Surveillance 4'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')

    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain

class AuditTaskOthers(models.Model):
    _name = 'audit.task.other'
    _description = 'Audit Task'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISO 37001:2016', 'ISO 37001:2016'),
        ('ISO 21001:2018', 'ISO 21001:2018'),
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')
    # Field untuk menghitung rata-rata atau total
    # total_percentage = fields.Float(
    #     string='Total Percentage',
    #     compute='_compute_total_percentage',
    #     store=True
    # )

    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain

class AuditTask9001(models.Model):
    _name = 'audit.task.9001'
    _description = 'Audit Task'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISO 9001:2015', 'ISO 9001:2015')
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')
    # Field untuk menghitung rata-rata atau total
    # total_percentage = fields.Float(
    #     string='Total Percentage',
    #     compute='_compute_total_percentage',
    #     store=True
    # )

    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain

class AuditTask14001(models.Model):
    _name = 'audit.task.14001'
    _description = 'Audit Task'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISO 14001:2015', 'ISO 14001:2015')
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')
    # Field untuk menghitung rata-rata atau total
    # total_percentage = fields.Float(
    #     string='Total Percentage',
    #     compute='_compute_total_percentage',
    #     store=True
    # )

    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain

class AuditTask45001(models.Model):
    _name = 'audit.task.45001'
    _description = 'Audit Task'
    _order = 'work_date'

    partner_id = fields.Many2one('res.partner', string='Nama Perusahaan', required=True, domain="[('is_company', '=', True)]")
    person = fields.Char(string='Person')
    iso_standard = fields.Selection([
        ('ISO 45001:2018', 'ISO 45001:2018')
    ], string='Scheme')
    status = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending')
    ], string='Status')
    method = fields.Selection([
        ('soft_file', 'Soft File'),
        ('hard_file', 'Hard File'),
        ('odoo', 'Odoo')
    ], string='Metode')
    stage = fields.Selection([
        ('initial_stage1', 'Initial Stage 1'),
        ('initial_stage2', 'Initial Stage 2'),
        ('surveillance1', 'Surveillance 1'),
        ('surveillance2', 'Surveillance 2'),
        ('recertification', 'Recertification')
    ], string='Tahapan')
    percentage = fields.Float(string='Percentage', default=0.0)
    work_date = fields.Date(string='Waktu Pengerjaan')
    notes = fields.Text(string='Catatan')
    # Field untuk menghitung rata-rata atau total
    # total_percentage = fields.Float(
    #     string='Total Percentage',
    #     compute='_compute_total_percentage',
    #     store=True
    # )

    @api.onchange('percentage')
    def _onchange_percentage(self):
        # Menghitung total percentage dari seluruh record yang ada
        total = sum(record.percentage for record in self.search([]))
        print(f"Total Percentage: {total}")
        # Anda bisa menampilkan total di UI atau logika lain

class AuditTaskType(models.Model):
    _name = 'audit.task.type'
    _description = 'Audit Task Type'

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    color = fields.Integer('Color')