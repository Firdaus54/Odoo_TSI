# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

# Customer Survey
class cust_survey(models.Model):
    _name = 'cust_survey'
    _inherit        = 'mail.thread'
    _description    = 'Customer Survey'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    name            = fields.Char(string="name")
    satisfaction    = fields.Char(string="satisfaction")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Customer Complaint
class cust_complaint(models.Model):
    _name           = 'cust_complaint'
    _inherit        = 'mail.thread'
    _description    = 'Customer Survey'
    _rec_name       = 'cust_name'
    nomor           = fields.Char(required=True)
    cust_name       = fields.Char(string="cust_name")
    tanggal         = fields.Date(default=datetime.today())
    description     = fields.Text()
    root_cause      = fields.Text(string="root_cause")
    status          = fields.Selection(selection=[('Open', 'Open'),('Close', 'Close')], required=True)
    closing_date    = fields.Date(default=datetime.today())
    # action_plan     = fields.Many2one('objective', ondelete='cascade', string="Action Plan")


# Customer Relation
class cust_relation(models.Model):
    _name = 'cust_relation'
    _inherit        = 'mail.thread'
    _description    = 'Customer Relation'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    tanggal         = fields.Date(default=datetime.today())
    agenda          = fields.Text(string="agenda")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')


# Internal Communication
class internalcomm(models.Model):
    _name = 'internalcomm'
    _inherit        = 'mail.thread'
    _description    = 'Internal Communication'
    name            = fields.Char(required=True)
    tanggal         = fields.Date(default=datetime.today())
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Eksternal Communication
class eksternalcomm(models.Model):
    _name = 'eksternalcomm'
    _inherit        = 'mail.thread'
    _description    = 'External Communication'
    name            = fields.Char(required=True)
    tanggal         = fields.Date(default=datetime.today())
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Participation
class participation(models.Model):
    _name = 'participation'
    _inherit        = 'mail.thread'
    _description    = 'Participation'
    name            = fields.Char(required=True)
    tanggal         = fields.Date(default=datetime.today())
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Social Responsibility Planning
class social_resp_plan(models.Model):
    _name = 'social_resp_plan'
    _inherit        = 'mail.thread'
    _description    = 'Social Responsibility Planning'
    name            = fields.Char(required=True)
    dep_name        = fields.Many2one('hr.department', ondelete='cascade', required=True)
    kpi_what        = fields.Char(string="What")
    kpi_who         = fields.Char(string="Who")
    kpi_when        = fields.Char(string="When")
    kpi_how         = fields.Text(string="How")
    kpi_resource    = fields.Char(string="Resource")
    kpi_input       = fields.Text(string="Input")
    kpi_output      = fields.Char(string="Output")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Social Responsibility Monitoring
class social_resp_mon(models.Model):
    _name = 'social_resp_mon'
    _inherit        = 'mail.thread'
    _description    = 'Social Responsibility Monitoring'
    _rec_name       = 'dep_name'
    dep_name        = fields.Many2one('hr.department', ondelete='cascade', string="Department", required=True)
    month           = fields.Char(string="month")
    csr_plan_id     = fields.Many2one('social_resp_plan', ondelete='cascade', string="Objective", required=True)
    result          = fields.Text(string="result")
    corrective      = fields.Text(string="corrective")
    pic_kpi         = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
