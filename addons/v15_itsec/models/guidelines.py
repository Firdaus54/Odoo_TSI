# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

# Manual
class manual(models.Model):
    _name           = 'itsec.manual'
    _inherit        = 'mail.thread'
    _description    = 'Manual'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Company Policy
class compolicy(models.Model):
    _name = 'itsec.compolicy'
    _inherit        = 'mail.thread'
    _description    = 'Company Policy'
    
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    issued_date     = fields.Date(default=datetime.today())
    description     = fields.Text()
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Prosedur
class prosedur(models.Model):
    _name = 'itsec.prosedur'
    _inherit        = 'mail.thread'
    _description    = 'Procedure'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Instruksi Kerja
class instruksi(models.Model):
    _name = 'itsec.instruksi'
    _inherit        = 'mail.thread'
    _description    = 'Instruksi'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Drawing
class drawing(models.Model):
    _name = 'itsec.drawing'
    _inherit        = 'mail.thread'
    _description    = 'Drawing'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Standard
class standard(models.Model):
    _name = 'itsec.standard'
    _inherit        = 'mail.thread'
    _description    = 'Standard'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Form
class form(models.Model):
    _name = 'itsec.form'
    _inherit        = 'mail.thread'
    _description    = 'Form'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Quality Plan
class quality_plan(models.Model):
    _name = 'itsec.quality_plan'
    _inherit        = 'mail.thread'
    _description    = 'Quality Plan'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text()
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
