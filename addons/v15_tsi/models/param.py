from odoo import models, fields, api, SUPERUSER_ID, _

class Hazard(models.Model):
    _name           = 'tsi.hazard'
    _description    = 'Hazard'

    name            = fields.Char(string='Nama')

class EnvAspect(models.Model):
    _name           = 'tsi.env_aspect'
    _description    = 'Environmental Aspect'

    name            = fields.Char(string='Nama')

class AltScope(models.Model):
    _name           = 'tsi.alt_scope'
    _description    = 'Alt Scope'

    name            = fields.Char(string='Nama')
