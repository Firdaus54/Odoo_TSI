from odoo import models, fields, api
from datetime import datetime

# Kehilangan
class kehilangan(models.Model):
    _name           = 'itsec.kehilangan'
    _inherit        = 'mail.thread'
    _description    = 'Formulir Kehilangan'
    _rec_name       = 'doc_no'
    doc_no          = fields.Char(string="Nomor Dokumen")
    rev_no          = fields.Char(string="Revisi")
    nomor           = fields.Char(string="Nomor")
    hari            = fields.Char(string="Hari")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal")

    pegawai         = fields.Many2one('hr.employee', ondelete='cascade', string="Nama", required=True)
    nip             = fields.Char(string="NIP")
    jabatan         = fields.Many2one('hr.job', ondelete='cascade', string="Jabatan", required=True)
    bagian          = fields.Many2one('hr.department', ondelete='cascade', string="Bagian", required=True)

    saat            = fields.Char(string="Hari Kejadian")
    tanggal_event   = fields.Date(default=datetime.today(), string="Tanggal Kejadian")
    pukul           = fields.Char(string="Pukul")
    lokasi          = fields.Char(string="Lokasi")
    keterangan      = fields.Text(string="Keterangan")
    kondisi         = fields.Selection(selection=[
                        ('rusak', 'Rusak'),
                        ('hilang', 'Hilang')], string="Kondisi")

    kepala_bagian   = fields.Many2one('hr.employee', ondelete='cascade', string="Kepala Bagian")
    kepala_asset    = fields.Many2one('hr.employee', ondelete='cascade', string="Asset Management ")
    kepala_admin    = fields.Many2one('hr.employee', ondelete='cascade', string="Kepala Tata Usaha")

    barang_line     = fields.One2many('risk.barang_line', 'hilang_line_id', string='Assets')

class risk_barang_line(models.Model):
    _name           = 'risk.barang_line'
    _description    = 'Barang'
    hilang_line_id  = fields.Many2one('itsec.kehilangan', ondelete='cascade')
    pinjam_line_id  = fields.Many2one('itsec.peminjaman', ondelete='cascade')
    minta_line_id   = fields.Many2one('itsec.permintaan', ondelete='cascade')
    nama            = fields.Char(string="Nama")
    nomor           = fields.Char(string="Nomor")
    merk            = fields.Char(string="Merek")
    qty             = fields.Char(string="Qty")
    keterangan      = fields.Char(string="Keterangan")
    untuk           = fields.Char(string="Digunakan Pada")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal Dibutuhkan")
    

# Kehilangan
class peminjaman(models.Model):
    _name           = 'itsec.peminjaman'
    _inherit        = 'mail.thread'
    _description    = 'Formulir Peminjaman'
    _rec_name       = 'doc_no'
    doc_no          = fields.Char(string="Nomor Dokumen")
    rev_no          = fields.Char(string="Revisi")
    nomor           = fields.Char(string="Nomor")
    hari            = fields.Char(string="Hari")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal")

    pegawai         = fields.Many2one('hr.employee', ondelete='cascade', string="Nama", required=True)
    nip             = fields.Char(string="NIP")

    pegawai_2       = fields.Many2one('hr.employee', ondelete='cascade', string="Digunakan Oleh", required=True)
    nip_2           = fields.Char(string="NIP Pegawai")
    bagian_2        = fields.Many2one('hr.department', ondelete='cascade', string="Divisi", required=True)
    referensi_2     = fields.Char(string="Referensi")
    keterangan      = fields.Text(string="Keterangan")

    kondisi         = fields.Selection(selection=[
                        ('disetujui', 'Disetujui'),
                        ('tidak', 'Tidak Disetujui')], string="Kondisi")
    kepala_bagian   = fields.Many2one('hr.employee', ondelete='cascade', string="Kepala Bagian")

    barang_line     = fields.One2many('risk.barang_line', 'pinjam_line_id', string='Assets')

# Permintaan
class permintaan(models.Model):
    _name           = 'itsec.permintaan'
    _inherit        = 'mail.thread'
    _description    = 'Formulir Permintaan'
    _rec_name       = 'doc_no'
    doc_no          = fields.Char(string="Nomor Dokumen")
    rev_no          = fields.Char(string="Revisi")
    nomor           = fields.Char(string="Nomor")
    hari            = fields.Char(string="Hari")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal")

    pegawai         = fields.Many2one('hr.employee', ondelete='cascade', string="Nama", required=True)
    nip             = fields.Char(string="NIP")
    bagian          = fields.Many2one('hr.department', ondelete='cascade', string="Bagian", required=True)
    nomor_perminta  = fields.Char(string="Nomor Permintaan")

    keterangan      = fields.Text(string="Keterangan")

    kepala_bagian   = fields.Many2one('hr.employee', ondelete='cascade', string="Kepala Bagian")
    kepala_asset    = fields.Many2one('hr.employee', ondelete='cascade', string="Asset Management ")
    kepala_admin    = fields.Many2one('hr.employee', ondelete='cascade', string="Kepala Tata Usaha")

    barang_line     = fields.One2many('risk.barang_line', 'minta_line_id', string='Assets')
        