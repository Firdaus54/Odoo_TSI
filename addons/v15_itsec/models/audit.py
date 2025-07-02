# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

# Audit Program
class audit_program(models.Model):
    _name           = 'audit.audit_program'
    _inherit        = 'mail.thread'
    _description    = 'Audit Program'
    _rec_name       = 'activity'
    audit_no        = fields.Char(string="Audit No",required=True)
    periode         = fields.Char(string="Periode", required=True)
    activity        = fields.Char(string="Activity", required=True)
    plan_date       = fields.Date(string="Plan Date", default=datetime.today())
    audit_pic       = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Audit Report
class audit_report(models.Model):
    _name               = 'audit.audit_report'
    _inherit            = 'mail.thread'
    _description        = 'Internal Report'
    _rec_name           = 'auditor_id'
    auditor_id          = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor", required=True)
    audit_period        = fields.Char(required=True)
    audit_date          = fields.Date(default=datetime.today())
    subject_id          = fields.Many2one('audit.audit_subject', ondelete='cascade', string="Proses")
    pic_auditee_id      = fields.Many2one('hr.employee', ondelete='cascade', string="PIC Auditor")
    document_ids        = fields.One2many('audit.audit_docs', 'audit_docs_id', string="Documents")

class audit_docs(models.Model):
    _name               = 'audit.audit_docs'
    _description        = 'Document'
    audit_docs_id       = fields.Many2one('audit.audit_report', ondelete='cascade')
    finding_no          = fields.Char()
    category            = fields.Char(string="Category")
    description         = fields.Char(string="Description")
    file_bin            = fields.Binary('Attachment')
    file_name           = fields.Char('Filename')


# Audit Report
class audit_ex_report(models.Model):
    _name               = 'audit.audit_ex_report'
    _inherit            = 'mail.thread'
    _description        = 'External Report'
    _rec_name           = 'auditor_id'
    auditor_id          = fields.Many2one('res.partner', ondelete='cascade', string="Auditor", required=True)
    audit_period        = fields.Char(required=True)
    audit_date          = fields.Date(default=datetime.today())
    subject_id          = fields.Many2one('audit.audit_subject', ondelete='cascade', string="Proses")
    pic_auditee_id      = fields.Many2one('hr.employee', ondelete='cascade', string="Auditee")
    document_ids        = fields.One2many('audit.audit_docs', 'audit_docs_id', string="Documents")

# Audit Plan
class audit_plan(models.Model):
    _name = 'audit.audit_plan'
    _inherit     = 'mail.thread'
    _description = 'QMS Audit Plan'
    _rec_name   = 'periode'
    periode     = fields.Char(required=True)
    tanggal     = fields.Date(default=datetime.today())
    waktu       = fields.Char()
    proses_id   = fields.Many2one('audit.audit_subject', ondelete='cascade', string="Proses", required=True)
    auditor_id  = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor", required=True)
    standard    = fields.Char(string="Standard")

# Audit Subject
class audit_subject(models.Model):
    _name           = 'audit.audit_subject'
    _inherit        = 'mail.thread'
    _description    = 'QMS Subject'
    name            = fields.Char(required=True)
    departemen      = fields.Many2one('hr.department', ondelete='cascade', string="Department")
    penanggung      = fields.Many2one('hr.employee', ondelete='cascade', string="Employee")

# Inspeksi
class inspection(models.Model):
    _name           = 'audit.inspection'
    _inherit        = 'mail.thread'
    _description    = 'QMS Inspection'
    name            = fields.Char(required=True)
    description     = fields.Char(required=True)
    date            = fields.Date(default=datetime.today())
    pic             = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor", required=True)
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')