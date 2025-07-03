from odoo import models, fields

class Guru(models.Model):
    _name = 'sekolah.guru'
    _description = 'Data Guru'
    _rec_name       = 'nm_guru'

    nip = fields.Char(string='NIP', required=True)
    nm_guru = fields.Char(string='Nama Guru', required=True)
    jns_kelamin = fields.Selection([
        ('l', 'Laki-laki'),
        ('p', 'Perempuan')
    ], string='Jenis Kelamin', required=True)
    mata_pelajaran = fields.Many2one('sekolah.mapel', string='Mata Pelajaran')
    usia = fields.Integer(string='Usia')
    no_telp = fields.Char(string='No. Telepon')
    alamat = fields.Text(string='Alamat')