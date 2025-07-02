# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count',
                                   groups="om_om_hr_payroll.group_hr_payroll_user")
    nip = fields.Char('NIP')
    phone_wa = fields.Char(string="No Whatsapp", tracking=True)
    # auditor = fields.Selection([
    #                         ('Yes', 'Yes'),
    #                         ('No', 'No'),
    #                     ], string='Certification Type', index=True, tracking=True,)
    #LinkedIn
    linkedin = fields.Char(string="LinkedIn", tracking=True)
    linkedin_url = fields.Char(string="LinkedIn URL", compute="_compute_social_urls")
    #Instagram
    instagram_username = fields.Char(string="Instagram", tracking=True)
    instagram_url = fields.Char(string="Instagram URL", compute="_compute_social_urls")
    #Facebook
    facebook_username = fields.Char(string="Facebook", tracking=True)
    facebook_url = fields.Char(string="Facebook URL", compute="_compute_social_urls")

    @api.depends('linkedin', 'instagram_username', 'facebook_username')
    def _compute_social_urls(self):
        for rec in self:
            # LinkedIn
            if rec.linkedin:
                if not rec.linkedin.startswith("http"):
                    rec.linkedin_url = f"https://www.linkedin.com/in/{rec.linkedin}"
                else:
                    rec.linkedin_url = rec.linkedin
            else:
                rec.linkedin_url = False

            # Instagram
            if rec.instagram_username:
                rec.instagram_url = f"https://instagram.com/{rec.instagram_username}"
            else:
                rec.instagram_url = False

            # Facebook
            if rec.facebook_username:
                rec.facebook_url = f"https://facebook.com/{rec.facebook_username}"
            else:
                rec.facebook_url = False

    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)
    
    @api.constrains('phone_wa')
    def _check_phone_wa(self):
        for rec in self:
            if rec.phone_wa:
                if not rec.phone_wa.isdigit():
                    raise ValidationError("Nomor WhatsApp hanya boleh berisi angka saja.")
                if not rec.phone_wa.startswith("62"):
                    raise ValidationError("Nomor WhatsApp harus dimulai dengan '62', bukan '0' atau lainnya.")
                if len(rec.phone_wa) < 10:
                    raise ValidationError("Nomor WhatsApp terlalu pendek.")