from odoo import models, fields, api
from datetime import datetime

# Backup
class backup(models.Model):
    _name           = 'itsec.backup'
    _inherit        = 'mail.thread'
    _description    = 'Backup'
    _rec_name       = 'doc_no'
    doc_no          = fields.Char(string="Nomor")
    rev_no          = fields.Char(string="Revisi")
    pelaksana       = fields.Many2one('hr.employee', ondelete='cascade', string="Pelaksana", required=True)
    atasan          = fields.Many2one('hr.employee', ondelete='cascade', string="Atasan", required=True)
    saksi           = fields.Many2one('hr.employee', ondelete='cascade', string="Saksi", required=True)
    tanggal         = fields.Date(default=datetime.today(), string="Pelaksanaan", required=True)

    hari            = fields.Char(string="Hari")
    tanggal_backup  = fields.Date(default=datetime.today(), string="Tanggal")
    lokasi          = fields.Char(string="Lokasi")
    perihal         = fields.Char(string="Perihal")

    server          = fields.Char(string="Server / PC")
    kegunaan        = fields.Char(string="Kegunaan")
    no_inventaris   = fields.Char(string="Nomor Inventaris")
    data            = fields.Char(string="Data yg dibackup")
    ukuran          = fields.Char(string="Ukuran")
    frekuensi       = fields.Char(string="Frekuensi")
    metode          = fields.Char(string="Metode Backup")
    enkripsi        = fields.Char(string="Teknik Enkripsi")

    jenis           = fields.Char(string="Jenis Media")
    size            = fields.Char(string="Size Media")
    berlaku         = fields.Char(string="Masa berlaku")
    no_media        = fields.Char(string="Nomor Media")

    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Restore
class restore(models.Model):
    _name           = 'itsec.restore'
    _inherit        = 'mail.thread'
    _description    = 'Backup'
    _rec_name       = 'doc_no'
    doc_no          = fields.Char(string="Nomor")
    rev_no          = fields.Char(string="Revisi")
    pelaksana       = fields.Many2one('hr.employee', ondelete='cascade', string="Pelaksana", required=True)
    atasan          = fields.Many2one('hr.employee', ondelete='cascade', string="Atasan", required=True)
    saksi           = fields.Many2one('hr.employee', ondelete='cascade', string="Saksi", required=True)
    tanggal         = fields.Date(default=datetime.today(), string="Pelaksanaan", required=True)

    hari            = fields.Char(string="Hari")
    tanggal_restore = fields.Date(default=datetime.today(), string="Tanggal")
    lokasi          = fields.Char(string="Lokasi")
    perihal         = fields.Char(string="Perihal")

    jenis           = fields.Char(string="Jenis Media")
    size            = fields.Char(string="Size Media")
    berlaku         = fields.Char(string="Masa berlaku")
    no_media        = fields.Char(string="Nomor Media")
    metode          = fields.Char(string="Metode Restore")

    server          = fields.Char(string="Server / PC")
    kegunaan        = fields.Char(string="Kegunaan")
    no_inventaris   = fields.Char(string="Nomor Inventaris")
    data            = fields.Char(string="Data yg dibackup")
    ukuran          = fields.Char(string="Ukuran")

    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Change
class change(models.Model):
    _name           = 'itsec.change'
    _inherit        = 'mail.thread'
    _description    = 'Change Request'
    _rec_name       = 'doc_no'
    doc_no          = fields.Char(string="Nomor")
    rev_no          = fields.Char(string="Revisi")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal", required=True)

    requestor       = fields.Many2one('hr.employee', ondelete='cascade', string="Requestor", required=True)
    bagian          = fields.Many2one('hr.department', ondelete='cascade', required=True, string="Bagian")
    uraian          = fields.Text(string="Uraian")
    justifikasi     = fields.Text(string="Justifikasi")
    penerapan       = fields.Date(default=datetime.today(), string="Penerapan", required=True)

    change_type     = fields.Selection(selection=[('EM', '(EM) Emergency'),('MA', '(MA) Major Normal'),('MI', '(MI) Minor Normal')], string="Change Type", required=True)
    change_cat      = fields.Selection(selection=[('L1', 'L1 : Software'),('L2', 'L2 : Application'),('L3', 'L3 : '),('L4', 'L4 : ')], string="Change Category", required=True)
    affected        = fields.Text(string="Service Affected")
    impact          = fields.Text(string="Impact Analysis")
    manager         = fields.Many2one('hr.employee', ondelete='cascade', string="Manager", required=True)

    asset_name      = fields.Char(string="Asset Name")
    estimated_time  = fields.Char(string="Estimated Time")
    rollback_plan   = fields.Text(string="Rollback Plan")
    implementator   = fields.Many2one('hr.employee', ondelete='cascade', string="Implementator", required=True)

    authorized      = fields.Selection(selection=[('A', 'A : Approved'),('R', 'R : Rejected'),('N', 'N : Revision Needed')], string="Otorisasi", required=True)
    catatan         = fields.Text(string="Catatan")
