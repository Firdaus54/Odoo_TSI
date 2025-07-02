from odoo import models, fields, api
from datetime import datetime

class emergency(models.Model):
    _name           = 'bcp.emergency'
    _inherit        = 'mail.thread'
    _description    = 'Emergency'
    _rec_name       = 'dep_name'
    dep_name        = fields.Char(required=True)
    job_position    = fields.Many2one('hr.job', ondelete='cascade', string="Auditee", required=True)
    responsibility  = fields.Text(string="Responsibility")
    authority       = fields.Text(string="Authority")
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    issued_date     = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

class emergency_number(models.Model):
    _name           = 'bcp.emergency_number'
    _inherit        = 'mail.thread'
    _description    = 'Emergency Number'
    name            = fields.Char(required=True)
    address         = fields.Text(string="address")
    position        = fields.Char(string="position")
    number          = fields.Char(string="number")
    alt_number      = fields.Char(string="alt_number")

class emergency_tools(models.Model):
    _name           = 'bcp.emergency_tools'
    _inherit        = 'mail.thread'
    _description    = 'Emergency Tools'
    name            = fields.Char(required=True)
    asset_no        = fields.Char(string="asset_no")
    description     = fields.Text(string="description")

class emergency_drill_plan(models.Model):
    _name           = 'bcp.emergency_drill_plan'
    _inherit        = 'mail.thread'
    _description    = 'Emergency Drill Plan`'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')


class emergency_drill_eval(models.Model):
    _name           = 'bcp.emergency_drill_eval'
    _inherit        = 'mail.thread'
    _description    = 'Emergency Drill Evaluation`'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    status          = fields.Selection(selection=[('Open', 'Open'),('Close', 'Close')], required=True)
    # action_plan     = fields.Many2one('bcp.objective', ondelete='cascade', string="Action Plan")


class drill_scenario(models.Model):
    _name           = 'bcp.drill_scenario'
    _inherit        = 'mail.thread'
    _description    = 'Emergency Drill Scenario'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

class recovery_plan(models.Model):
    _name           = 'bcp.recovery_plan'
    _inherit        = 'mail.thread'
    _description    = 'Recovery Plan`'
    name            = fields.Char(required=True)
    doc_no          = fields.Char(string="doc_no")
    rev_no          = fields.Char(string="rev_no")
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
