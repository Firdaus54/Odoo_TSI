from odoo import models, fields

class Kelas(models.Model):
    _name = 'sekolah.kelas'
    _description = 'Data Kelas'
    _rec_name       = 'name'

    name = fields.Char(string='Nama Kelas', required=True)
    siswa_ids = fields.One2many('sekolah.siswa', 'kelas_id', string='Siswa')
    guru_id = fields.Many2one('sekolah.guru', string='Wali Kelas')