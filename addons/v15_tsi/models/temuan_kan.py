from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class TemuanKANInternal(models.Model):
    _name = 'temuan.kan.internal'
    _description    = 'Temuan KAN Internal'
    _rec_name       = 'ketidaksesuaian'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('temuan.kan.line', string="Reference")
    nomor                 = fields.Char(string="Nomor")
    ketidaksesuaian = fields.Text(string="Task Name", size=150, tracking=True)
    assignee = fields.Text(string='Assignee', tracking=True)
    tanggal = fields.Date(string='Tanggal', default=datetime.today(), tracking=True)
    kategori = fields.Text(string="Kategori", size=150, tracking=True)
    pic = fields.Text(string="PIC", size=150, tracking=True)
    percentage = fields.Integer(string='Percentage', default=0, tracking=True)
    amount_percentage = fields.Float(string='Average Percentage', compute='_compute_average_percentage', store=True, tracking=True)
    progress = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Progress', default='not_started', compute="_compute_progress", store=True, readonly=False, tracking=True)
    analisis = fields.Text(string="Analisis Penyebab", size=150, tracking=True)
    koreksi = fields.Text(string="Koreksi", size=150, tracking=True)
    tindakan = fields.Text(string="Tindakan", size=150, tracking=True)
    upload_dokumen = fields.Binary('Dokumen Pendukung', tracking=True)
    file_name       = fields.Char('Filename', tracking=True)
    status = fields.Text(string="Status",compute="_compute_status_warning", store=True, size=150, tracking=True)
    skema = fields.Text(string="Schema", size=150, tracking=True)
    sla = fields.Integer('SLA', compute="_compute_sla", store=True, tracking=True)

    @api.model
    def create(self, vals):
        record = super(TemuanKANInternal, self).create(vals)
        partner = record.reference_id
        partner.message_post(body=f"Created Internal Audit: {record.nomor}, Task Name: {record.ketidaksesuaian}, Assigne: {record.assignee}, Tanggal: {record.tanggal}, PIC: {record.pic}, Percentage: {record.percentage}, Analisis Penyebab: {record.analisis}, Koreksi: {record.koreksi}, Tindakan: {record.tindakan}, Schema: {record.skema}, SLA: {record.sla}")
        return record

    def write(self, vals):
        res = super(TemuanKANInternal, self).write(vals)
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Updated Internal Audit: {record.nomor}, Task Name: {record.ketidaksesuaian}, Assigne: {record.assignee}, Tanggal:{record.tanggal}, PIC: {record.pic}, Percentage: {record.percentage}, Analisis Penyebab: {record.analisis}, Koreksi: {record.koreksi}, Tindakan: {record.tindakan}, Schema: {record.skema}, SLA: {record.sla}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Deleted Internal Audit: {record.nomor}, Task Name:{record.ketidaksesuaian}, Assigne: {record.assignee}, Tanggal:{record.tanggal}, PIC: {record.pic}, Percentage: {record.percentage}, Analisis Penyebab: {record.analisis}, Koreksi: {record.koreksi}, Tindakan: {record.tindakan}, Schema: {record.skema}, SLA: {record.sla}")
        return super(TemuanKANInternal, self).unlink()  

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
    
    @api.depends('tanggal')
    def _compute_sla(self):
        """Menghitung SLA (berapa hari keterlambatan)"""
        for record in self:
            if record.tanggal:
                hari_ini = fields.Date.today()
                selisih_hari = (hari_ini - record.tanggal).days
                record.sla = selisih_hari if selisih_hari > 0 else 0
            else:
                record.sla = 0
    
    @api.model
    def update_sla_automatically(self):
        """Memperbarui SLA otomatis untuk semua record pada pergantian hari"""
        records = self.search([('tanggal', '!=', False)])  # Cari record dengan tanggal
        for record in records:
            record._compute_sla()  # Panggil method _compute_sla

    @api.depends('sla', 'percentage')
    def _compute_status_warning(self):
        """Menentukan apakah status perlu menjadi 'Sudah Melewati Masa Pengerjaan'"""
        for record in self:
            if record.sla > 11 and record.percentage < 100:
                record.status = "Sudah Melewati Masa Pengerjaan"
            else:
                record.status = ""
    
    @api.depends('percentage')
    def _compute_progress(self):
        """Mengatur progress otomatis berdasarkan nilai percentage"""
        for record in self:
            if record.percentage == 100:
                record.progress = 'done'
            elif record.percentage >= 10:
                record.progress = 'in_progress'
            else:
                record.progress = 'not_started'
    
    @api.constrains('percentage')
    def _check_percentage(self):
        """Cek agar percentage tidak lebih dari 100%"""
        for record in self:
            if record.percentage > 100:
                raise ValidationError("Percentage tidak boleh lebih dari 100%!")

class TemuanKANEksternal(models.Model):
    _name = 'temuan.kan.eksternal'
    _description    = 'Temuan KAN Eksternal'
    _rec_name       = 'ketidaksesuaian'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('temuan.kan.eksternal.line', string="Reference")
    nomor                 = fields.Char(string="Nomor")
    ketidaksesuaian = fields.Text(string="Task Name", size=150, tracking=True)
    assignee = fields.Text(string='Assignee', tracking=True)
    tanggal = fields.Date(string='Tanggal', default=datetime.today(), tracking=True)
    kategori = fields.Text(string="Kategori", size=150, tracking=True)
    pic = fields.Text(string="PIC", size=150, tracking=True)
    percentage = fields.Integer(string='Percentage', default=0, tracking=True)
    amount_percentage = fields.Float(string='Average Percentage', compute='_compute_average_percentage', store=True, tracking=True)
    progress = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Progress', default='not_started', compute="_compute_progress", store=True, readonly=False, tracking=True)
    analisis = fields.Text(string="Analisis Penyebab", size=150, tracking=True)
    koreksi = fields.Text(string="Koreksi", size=150, tracking=True)
    tindakan = fields.Text(string="Tindakan", size=150, tracking=True)
    upload_dokumen = fields.Binary('Dokumen Pendukung', tracking=True)
    file_name       = fields.Char('Filename', tracking=True)
    status = fields.Text(string="Status",compute="_compute_status_warning", store=True, size=150, tracking=True)
    skema = fields.Text(string="Schema", size=150, tracking=True)
    sla = fields.Integer('SLA', compute="_compute_sla", store=True, tracking=True)

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
    
    @api.depends('tanggal')
    def _compute_sla(self):
        """Menghitung SLA (berapa hari keterlambatan)"""
        for record in self:
            if record.tanggal:
                hari_ini = fields.Date.today()
                selisih_hari = (hari_ini - record.tanggal).days
                record.sla = selisih_hari if selisih_hari > 0 else 0
            else:
                record.sla = 0
    
    @api.model
    def update_sla_automatically_external(self):
        """Memperbarui SLA otomatis untuk semua record pada pergantian hari"""
        records = self.search([('tanggal', '!=', False)])  # Cari record dengan tanggal
        for record in records:
            record._compute_sla()  # Panggil method _compute_sla

    @api.depends('sla', 'percentage')
    def _compute_status_warning(self):
        """Menentukan apakah status perlu menjadi 'Sudah Melewati Masa Pengerjaan'"""
        for record in self:
            if record.sla > 11 and record.percentage < 100:
                record.status = "Sudah Melewati Masa Pengerjaan"
            else:
                record.status = ""
    
    @api.depends('percentage')
    def _compute_progress(self):
        """Mengatur progress otomatis berdasarkan nilai percentage"""
        for record in self:
            if record.percentage == 100:
                record.progress = 'done'
            elif record.percentage >= 10:
                record.progress = 'in_progress'
            else:
                record.progress = 'not_started'
    
    @api.constrains('percentage')
    def _check_percentage(self):
        """Cek agar percentage tidak lebih dari 100%"""
        for record in self:
            if record.percentage > 100:
                raise ValidationError("Percentage tidak boleh lebih dari 100%!")

class TemuanKANInternalLine(models.Model):
    _name = 'temuan.kan.line'
    _description    = 'Temuan KAN Internal'
    _rec_name       = 'name_project'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name_project    = fields.Text('Name Project')
    inconsistency_ids = fields.One2many('temuan.kan.internal', 'reference_id', string="Inconsistencies")
    upload_dokumen = fields.Binary('Dokumen Pendukung', tracking=True)
    file_name       = fields.Char('Filename', tracking=True)
    progress = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Progress', compute='_compute_progresss', store=True)

    @api.depends('inconsistency_ids.progress')
    def _compute_progresss(self):
        for record in self:
            progresses = record.inconsistency_ids.mapped('progress')
            if 'in_progress' in progresses:
                record.progress = 'in_progress'
            elif 'done' in progresses:
                record.progress = 'done'
            else:
                record.progress = 'not_started'


class TemuanKANEksternalLine(models.Model):
    _name = 'temuan.kan.eksternal.line'
    _description    = 'Temuan KAN Eksternal'
    _rec_name       = 'name_project'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name_project    = fields.Text('Name Project')
    inconsistency_ids = fields.One2many('temuan.kan.eksternal', 'reference_id', string="Inconsistencies")
    upload_dokumen = fields.Binary('Dokumen Pendukung', tracking=True)
    file_name       = fields.Char('Filename', tracking=True)
    progress = fields.Selection([
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ], string='Progress', compute='_compute_progresss', store=True)

    @api.depends('inconsistency_ids.progress')
    def _compute_progresss(self):
        for record in self:
            progresses = record.inconsistency_ids.mapped('progress')
            if 'in_progress' in progresses:
                record.progress = 'in_progress'
            elif 'done' in progresses:
                record.progress = 'done'
            else:
                record.progress = 'not_started'
    