from odoo import models, fields

class MataPelajaran(models.Model):
    _name = 'sekolah.mapel'
    _description = 'Mata Pelajaran'
    _rec_name       = 'name'

    name = fields.Char(string='Nama Mata Pelajaran', required=True)
    jurusan = fields.Char(string='Jurusan', required=True)