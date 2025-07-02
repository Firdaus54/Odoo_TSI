# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

# Vendor Selection
class vendor_selection(models.Model):
    _name           = 'vendor.vendor_selection'
    _inherit        = 'mail.thread'
    _description    = 'Vendor Selection'
    name            = fields.Char(required=True, string="Name")
    description     = fields.Text(string="Description")
    file_bin        = fields.Binary('File')

# Vendor Approval
class vendor_approval(models.Model):
    _name = 'vendor.vendor_approval'
    _inherit        = 'mail.thread'
    _description    = 'Vendor Approval'
    name            = fields.Char(required=True, string="Name")
    description     = fields.Text(string="Description")
    file_bin        = fields.Binary('File')

# Vendor Evaluation
class vendor_evaluation(models.Model):
    _name           = 'vendor.vendor_evaluation'
    _inherit        = 'mail.thread'
    _description    = 'QMS Vendor Evaluation'
    name            = fields.Char(required=True, string="Vendor Name")
    address         = fields.Text(string="Address")
    service_name    = fields.Char(string="Service Name")
    quality         = fields.Selection(selection=[('poor', 'Poor'),('moddle', 'Middle'),('good', 'Good')], string="Quality")
    cost            = fields.Selection(selection=[('1', 'Poor'),('2', 'Middle'),('3', 'Good')], required=True, string="Cost")
    delivery        = fields.Selection(selection=[('1', 'Poor'),('2', 'Middle'),('3', 'Good')], required=True, string="Delivery")
    service         = fields.Selection(selection=[('1', 'Poor'),('2', 'Middle'),('3', 'Good')], required=True, string="Service")
    hse_compliance  = fields.Selection(selection=[('1', 'Poor'),('2', 'Middle'),('3', 'Good')], required=True, string="Compliance")
    communication   = fields.Selection(selection=[('1', 'Poor'),('2', 'Middle'),('3', 'Good')], required=True, string="Communication")
    operator_skill  = fields.Selection(selection=[('1', 'Poor'),('2', 'Middle'),('3', 'Good')], required=True, string="Skill")
    total_point     = fields.Integer(compute='_get_point', string="Total Point")
    status          = fields.Selection(selection=[('Passed', 'Passed'),('Fail', 'Fail')], string="Status")
    evaluation_date = fields.Date(string="Evaluation Date")
    evaluated_by    = fields.Char(string="Evaluated by")
    # evaluated_by    = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor", required=True)
    # action_plan     = fields.Many2one('vendor.objective', ondelete='cascade', string="Action Plan")

    @api.depends('cost', 'delivery', 'service', 'hse_compliance', 'communication', 'operator_skill')
    def _get_point(self):
        self.total_point = 1
        # for r in self:
        #     r.total_point = r.cost + r.delivery + r.service + r.hse_compliance + r.communication + r.operator_skill

# Vendor Monitoring
class vendor_monitoring(models.Model):
    _name = 'vendor.vendor_monitoring'
    _inherit        = 'mail.thread'
    _description    = 'QMS Vendor Monitoring'
    name            = fields.Char(required=True, string="Name")
    address         = fields.Text(string="Address")
    service_name    = fields.Char(string="Service Name")
    quality         = fields.Char(string="Quality")
    on_time         = fields.Char(string="Ontime")
    after_sales     = fields.Char(string="Aftersales")
    hse_compliance  = fields.Char(string="HSE Compliance")
    evaluation_date = fields.Date(default=datetime.today(), string="Evaluation Date")
    evaluated_by    = fields.Char(string="Evaluated By")
    # evaluated_by    = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor", required=True)


# Customer Contract
class qms_cust_contract(models.Model):
    _name = 'contract.cust_contract'
    _inherit        = 'mail.thread'
    _description    = 'Customer Contract'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    cust_name       = fields.Char(string="cust_name")
    contract_title  = fields.Char(string="contract_title")
    contract_date   = fields.Date(default=datetime.today(), string="Contract date")
    expired_date    = fields.Date(default=datetime.today(), string="Expired Date")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Vendor Contract
class qms_vendor_contract(models.Model):
    _name = 'contract.vendor_contract'
    _inherit        = 'mail.thread'
    _description    = 'Vendor Contract'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    cust_name       = fields.Char(string="cust_name")
    contract_title  = fields.Char(string="contract_title")
    contract_date   = fields.Date(default=datetime.today(), string="Contract Date")
    expired_date    = fields.Date(default=datetime.today(), string="Expired Date")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Subcont Contract
class qms_subcont_contract(models.Model):
    _name = 'contract.subcont_contract'
    _inherit        = 'mail.thread'
    _description    = 'Subcont Contract'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    cust_name       = fields.Char(string="cust_name")
    contract_title  = fields.Char(string="contract_title")
    contract_date   = fields.Date(default=datetime.today(), string="Contract Date")
    expired_date    = fields.Date(default=datetime.today(), string="Expired Date")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
