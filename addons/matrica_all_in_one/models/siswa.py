from odoo import models, fields

class Siswa(models.Model):
    _name = 'sekolah.siswa'
    _description = 'Data Siswa'
    _rec_name       = 'nm_siswa'

    nis = fields.Char(string='NIS', required=True)
    nm_siswa = fields.Char(string='Nama Siswa', required=True)
    jns_kelamin = fields.Selection([
        ('l', 'Laki-laki'),
        ('p', 'Perempuan')
    ], string='Jenis Kelamin', required=True)
    tgl_lahir = fields.Date(string='Tanggal Lahir')
    agama = fields.Selection([
        ('islam', 'Islam'),
        ('kristen', 'Kristen'),
        ('katolik', 'Katolik'),
        ('hindu', 'Hindu'),
        ('budha', 'Budha'),
        ('konghucu', 'Konghucu'),
        ('lainnya', 'Lainnya')
    ], string='Agama')
    nm_ayah = fields.Char(string='Nama Ayah')
    nm_ibu = fields.Char(string='Nama Ibu')
    usia = fields.Integer(string='Usia')
    alamat = fields.Text(string='Alamat')
    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas')